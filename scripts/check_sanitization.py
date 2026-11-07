#!/usr/bin/env python3
"""Scan the current tree for leftover personal data and broken workflow links.

Prints categories and counts only. It does not print matched addresses, message
bodies, hosts, or identifier values. It does not read Git history and it does
not call any network service.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_FILES = sorted(ROOT.glob("projects/**/*.json"))
MD_FILES = sorted(ROOT.glob("**/*.md"))

EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
URL = re.compile(r"https?://[^\s\"'\\<>)\]'`]+")
ALLOWED_EMAIL_DOMAINS = {"example.com", "example.org", "example.net"}
ALLOWED_HOSTS = {"your_n8n_host", "console.apify.com", "api.apify.com", "docs.apify.com"}

FINDINGS: list[str] = []


def add(path: Path, line: int | None, category: str) -> None:
    where = str(path.relative_to(ROOT))
    if line is None:
        FINDINGS.append(f"FINDING file={where} category={category}")
    else:
        FINDINGS.append(f"FINDING file={where} line={line} category={category}")


def host_allowed(host: str) -> bool:
    host = host.lower().strip(".")
    if host in ALLOWED_HOSTS:
        return True
    if host == "example" or host.endswith(".example"):
        return True
    if host in ALLOWED_EMAIL_DOMAINS or host.endswith(".example.com"):
        return True
    return False


def check_emails(path: Path, text: str) -> int:
    allowed = 0
    for match in EMAIL.finditer(text):
        domain = match.group(0).rsplit("@", 1)[1].lower()
        line = text.count("\n", 0, match.start()) + 1
        if domain in ALLOWED_EMAIL_DOMAINS:
            allowed += 1
            continue
        add(path, line, "email")
    return allowed


def check_urls(path: Path, text: str) -> None:
    for match in URL.finditer(text):
        raw = match.group(0)
        # Ignore n8n expressions that concatenate a scheme with a field.
        if "'" in raw or "+" in raw or raw.endswith("://"):
            continue
        host = raw.split("://", 1)[1].split("/", 1)[0].split("?", 1)[0]
        if host_allowed(host):
            continue
        line = text.count("\n", 0, match.start()) + 1
        add(path, line, "url-host")


def walk(obj, path_parts: list[str]):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield path_parts + [str(key)], key, value
            yield from walk(value, path_parts + [str(key)])
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from walk(value, path_parts + [str(index)])


def check_workflow(path: Path, data: dict) -> None:
    if data.get("pinData"):
        add(path, None, "pin-data")
    meta = data.get("meta") or {}
    if "instanceId" in meta:
        add(path, None, "instance-id")
    if "id" in data or "versionId" in data:
        add(path, None, "workflow-instance-id")
    error_workflow = (data.get("settings") or {}).get("errorWorkflow")
    if error_workflow is not None and not str(error_workflow).startswith("REPLACE_"):
        add(path, None, "error-workflow-id")
    names = set()
    for node in data.get("nodes") or []:
        names.add(node.get("name"))
        if "webhookId" in node:
            add(path, None, "webhook-id")
        for cred_name, cred in (node.get("credentials") or {}).items():
            cred_id = cred.get("id")
            if cred_id is None:
                add(path, None, "empty-credential-id")
            elif not str(cred_id).startswith("REPLACE_"):
                add(path, None, "credential-id")
            if "__aiGatewayManaged" in cred:
                add(path, None, "gateway-flag")
        params = node.get("parameters") or {}
        for locator_name in ("documentId", "folderToWatch"):
            locator = params.get(locator_name)
            if isinstance(locator, dict):
                if "cachedResultUrl" in locator or "cachedResultName" in locator:
                    add(path, None, "cached-resource-url")
                value = str(locator.get("value", ""))
                if value.startswith("http") or (len(value) > 20 and not value.startswith("YOUR_")):
                    add(path, None, "resource-id")
        sheet = params.get("sheetName")
        if isinstance(sheet, dict) and "cachedResultUrl" in sheet:
            add(path, None, "cached-resource-url")
        actor = params.get("actorId")
        if isinstance(actor, dict) and "cachedResultUrl" in actor:
            url = str(actor.get("cachedResultUrl", ""))
            host = url.split("://", 1)[-1].split("/", 1)[0]
            if host != "console.apify.com":
                add(path, None, "actor-url")
    for source, outputs in (data.get("connections") or {}).items():
        if source not in names:
            add(path, None, "dangling-connection-source")
        for channel in outputs.values():
            for group in channel:
                for link in group:
                    if link.get("node") not in names:
                        add(path, None, "dangling-connection-target")


def check_sophie(path: Path, data: dict) -> None:
    model = data["assistant"]["model"]
    tool_ids = model.get("toolIds") or []
    if len(tool_ids) != 6 or any(not str(item).startswith("REPLACE_VAPI_TOOL_ID_") for item in tool_ids):
        add(path, None, "vapi-tool-id")
    file_ids = (model.get("knowledgeBase") or {}).get("fileIds") or []
    if len(file_ids) != 2 or any(not str(item).startswith("YOUR_VAPI_KNOWLEDGE_FILE_ID_") for item in file_ids):
        add(path, None, "vapi-file-id")
    voice = data["assistant"]["voice"]
    if voice.get("voiceId") != "YOUR_ELEVENLABS_VOICE_ID":
        add(path, None, "voice-id")
    fallbacks = (voice.get("fallbackPlan") or {}).get("voices") or []
    for item in fallbacks:
        if not str(item.get("voiceId", "")).startswith("YOUR_ELEVENLABS_FALLBACK_VOICE_ID_"):
            add(path, None, "voice-id")
    if "tools" in model or "functions" in data["assistant"]:
        add(path, None, "unexpected-tool-definition")


def check_lead_fixture(path: Path, data: dict) -> None:
    code = next(node["parameters"]["jsCode"] for node in data["nodes"] if node["name"] == "Code in JavaScript")
    runner = compile_js_count(code)
    if runner != (10, 7, 3):
        add(path, None, "synthetic-lead-count")


def compile_js_count(code: str) -> tuple[int, int, int]:
    """Count fixture rows with Node by executing only the local return array."""
    import subprocess

    program = (
        "const rows = (() => {\n"
        + code
        + "\n})();\n"
        + "const complete = rows.filter(r => r.json.email && r.json.companyName && r.json.website).length;\n"
        + "const incomplete = rows.length - complete;\n"
        + "const blob = JSON.stringify(rows);\n"
        + "if (blob.includes('@') && blob.split('@example.com').length - 1 !== (blob.match(/@/g) || []).length) process.exit(2);\n"
        + "console.log(rows.length + ',' + complete + ',' + incomplete);\n"
    )
    result = subprocess.run(["node", "-e", program], check=False, capture_output=True, text=True)
    if result.returncode != 0:
        return (-1, -1, -1)
    total, complete, incomplete = (int(part) for part in result.stdout.strip().split(","))
    return total, complete, incomplete


def check_score_example(path: Path, data: dict) -> None:
    code = next(node["parameters"]["jsCode"] for node in data["nodes"] if node["name"] == "Calculate Lead Score")
    import subprocess

    program = r"""
const $input = { all() { return [{ json: {
  firstName: "Avery", lastName: "Stone", name: "Avery Stone",
  email: "avery.stone@example.com", companyName: "Northwind Studio",
  website: "https://northwind.example", domain: "northwind.example",
  country: "United Kingdom", industry: "Furniture", employee_count: 120,
  emails: ["hello@example.com"], phones: [], linkedIns: [], twitters: []
}}]; } };
const run = new Function("$input", process.argv[1]);
const row = run($input)[0].json;
const ok = row.leadScore === 80 && row.leadTemperature === "Hot" && row.scoringReasons.length === 5;
if (!ok) process.exit(3);
"""
    result = subprocess.run(["node", "-e", program, code], check=False, capture_output=True, text=True)
    if result.returncode != 0:
        add(path, None, "score-example-mismatch")


def main() -> int:
    allowed_emails = 0
    parsed = 0
    if not JSON_FILES:
        add(ROOT / "projects", None, "missing-json")
    for path in JSON_FILES:
        text = path.read_text()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            add(path, None, "invalid-json")
            continue
        parsed += 1
        allowed_emails += check_emails(path, text)
        check_urls(path, text)
        if "nodes" in data:
            check_workflow(path, data)
        if "assistant" in data:
            check_sophie(path, data)
        if path.name == "lead-enrichment-crm-pipeline.json":
            check_lead_fixture(path, data)
            check_score_example(path, data)
        if path.name == "manual-five-step-event-routing.json":
            raw = next(node["parameters"]["jsonOutput"] for node in data["nodes"] if node["name"] == "Edit Fields")
            fixture = json.loads(raw)
            tickets = [row["tkt"] for row in fixture["registrations"]]
            if tickets != ["vip", "regular", "student", "vip", "regular", "complimentary", "student"]:
                add(path, None, "demo-fixture-shape")
            if len(data["nodes"]) != 5:
                add(path, None, "demo-node-count")
    for path in MD_FILES:
        if ".git" in path.parts:
            continue
        text = path.read_text()
        allowed_emails += check_emails(path, text)
        check_urls(path, text)
    print(f"json_files_parsed={parsed}")
    print(f"markdown_files_scanned={len(MD_FILES)}")
    print(f"allowed_placeholder_emails={allowed_emails}")
    print(f"disallowed_findings={len(FINDINGS)}")
    for finding in FINDINGS:
        print(finding)
    return 1 if FINDINGS else 0


if __name__ == "__main__":
    sys.exit(main())
