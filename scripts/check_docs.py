#!/usr/bin/env python3
"""Resolve relative Markdown links and confirm each project JSON is linked.

Does not print file contents. Does not call the network.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REQUIRED = [
    "README.md",
    "docs/privacy-and-history.md",
    "projects/studio-inbox/README.md",
    "projects/pharmacare/README.md",
    "projects/lead-enrichment/README.md",
    "projects/sophie-receptionist/README.md",
    "projects/manual-five-step-demo/README.md",
    "projects/studio-inbox/studio-inbox-email-sorting.json",
    "projects/pharmacare/pharmacare-customer-support.json",
    "projects/lead-enrichment/lead-enrichment-crm-pipeline.json",
    "projects/sophie-receptionist/sophie-assistant.json",
    "projects/manual-five-step-demo/manual-five-step-event-routing.json",
]


def main() -> int:
    missing = [rel for rel in REQUIRED if not (ROOT / rel).is_file()]
    broken: list[str] = []
    checked = 0
    for readme in sorted(ROOT.glob("**/*.md")):
        text = readme.read_text()
        for match in LINK.finditer(text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                broken.append(f"external-link-not-checked file={readme.relative_to(ROOT)}")
                continue
            path_part, _, _fragment = target.partition("#")
            if not path_part:
                continue
            resolved = (readme.parent / path_part).resolve()
            checked += 1
            if not resolved.is_file():
                broken.append(f"BROKEN file={readme.relative_to(ROOT)} category=missing-relative-target")
    for rel in (
        "projects/studio-inbox/studio-inbox-email-sorting.json",
        "projects/pharmacare/pharmacare-customer-support.json",
        "projects/lead-enrichment/lead-enrichment-crm-pipeline.json",
        "projects/sophie-receptionist/sophie-assistant.json",
        "projects/manual-five-step-demo/manual-five-step-event-routing.json",
    ):
        json.loads((ROOT / rel).read_text())
    root = (ROOT / "README.md").read_text()
    for rel in REQUIRED[1:]:
        name = Path(rel).name
        if name not in root and rel not in root:
            # Project docs are linked by their directory README name or path.
            leaf = Path(rel).parent.name if rel.endswith("README.md") else name
            if leaf not in root and rel not in root:
                missing.append(f"root-readme-missing:{rel}")
    print(f"relative_links_checked={checked}")
    print(f"required_files_missing={len(missing)}")
    print(f"link_findings={len(broken)}")
    for item in missing:
        print(f"MISSING {item}")
    for item in broken:
        print(item)
    return 1 if missing or broken else 0


if __name__ == "__main__":
    sys.exit(main())
