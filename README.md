# AI automation portfolio

Exported automation workflows by Marylinda Malachy.

I am learning n8n, voice agents, and API-based business automation. This repository is public so the workflow files and the notes next to them can be reviewed. The current files use placeholders instead of live account data. Older Git commits are unchanged. [Privacy and Git history](docs/privacy-and-history.md) explains that limit and the cleanup plan.

No license is specified.

## Status words

| Word | Meaning here |
| --- | --- |
| Exported | The workflow or assistant file is in the current tree. |
| Built | The file contains a constructed node graph or assistant configuration. |
| Not run here | This repository has no execution log, call transcript, screenshot, demo video, or saved successful result. |
| Unfinished | A behavior is named in a prompt or an older note, but this export does not implement it. |

Sample rows and the scoring example below are synthetic or were calculated locally from the scoring code. They are not n8n or Vapi runs.

## Inventory

| Project | What the file contains | Status |
| --- | --- | --- |
| [Studio Inbox](projects/studio-inbox/README.md) | [13-node n8n workflow](projects/studio-inbox/studio-inbox-email-sorting.json). Classifies Gmail with Anthropic Claude, extracts new-enquiry fields, appends a Google Sheet, and notifies a fixed mailbox. | Exported and built. Not run here. Replies to the sender are unfinished. |
| [PharmaCare customer support](projects/pharmacare/README.md) | [15-node n8n workflow](projects/pharmacare/pharmacare-customer-support.json) for a fictional community pharmacy. Classifies Gmail, runs an OpenAI agent against an in-memory vector store, and escalates the non-support branch. | Exported and built. Not run here. Customer replies and the separate error-handler workflow are unfinished. |
| [Lead enrichment and CRM](projects/lead-enrichment/README.md) | [14-node n8n workflow](projects/lead-enrichment/lead-enrichment-crm-pipeline.json): webhook, validation, two Apify actors, scoring, a HubSpot create-or-update node, an error-log sheet, and a manual fixture that POSTs synthetic leads. | Exported and built. Not run here. An older README called this planned only. A separate duplicate-search branch is unfinished. |
| [Sophie receptionist](projects/sophie-receptionist/README.md) | [Vapi assistant export](projects/sophie-receptionist/sophie-assistant.json) for a fictional plumbing receptionist. The prompt, model, voice settings, and transcriber settings are included. Six tool IDs have no tool definitions. | Exported configuration. Not run here. The six tools are missing from this repository. |
| [Manual five-step demo](projects/manual-five-step-demo/README.md) | [5-node manual n8n workflow](projects/manual-five-step-demo/manual-five-step-event-routing.json): trigger, set a synthetic registration list, split rows, rename fields, and switch on ticket type. | Exported and built. Not run here. It does not call YouTube. |

## Technologies present in these files

n8n, Gmail, Google Sheets, Google Drive, Anthropic Claude, OpenAI chat and embeddings, an in-memory vector store, Apify, HubSpot, Vapi, ElevenLabs, and Deepgram.

This is an inventory of nodes and settings. It is not a scored skills list, and it is not evidence that each integration ran successfully.

## PharmaCare context

I have a BPharm background. PharmaCare is a learning workflow set in a fictional community pharmacy. It is not a clinical product, it has not been clinically validated, and it is not a record of pharmacy software in production. The [PharmaCare notes](projects/pharmacare/README.md) separate prompt instructions from nodes that are actually connected.

## Layout

Each project folder has a README and one export. Previous root filenames remain only in Git history on `main`:

| Previous path | Current path |
| --- | --- |
| `Studio Inbox-Email Sorting & Enquiry Extraction.json` | [projects/studio-inbox/studio-inbox-email-sorting.json](projects/studio-inbox/studio-inbox-email-sorting.json) |
| `PharmaCare AI Customer Support.json` | [projects/pharmacare/pharmacare-customer-support.json](projects/pharmacare/pharmacare-customer-support.json) |
| `Lead Enrichment & CRM Pipeline main (1).json` | [projects/lead-enrichment/lead-enrichment-crm-pipeline.json](projects/lead-enrichment/lead-enrichment-crm-pipeline.json) |
| `Sophie .json` | [projects/sophie-receptionist/sophie-assistant.json](projects/sophie-receptionist/sophie-assistant.json) |
| `youtube-research-automation.json` | [projects/manual-five-step-demo/manual-five-step-event-routing.json](projects/manual-five-step-demo/manual-five-step-event-routing.json) |

The old YouTube filename described research automation. The exported graph is the five-step manual demo.

## Checks

From the repository root, these commands read the current files only. They do not call n8n, Vapi, Google, Apify, HubSpot, or any other external service.

```bash
python3 scripts/check_sanitization.py
python3 scripts/check_docs.py
```

## Still to do outside this branch

- Review this change before it is merged. Merging does not erase older commits.
- Replace the placeholders in a private n8n or Vapi account and run the checklist in each project README.
- Add screenshots or a demo video only after a real run.
- Follow [Privacy and Git history](docs/privacy-and-history.md) if the older commits should stop being publicly readable.
- Build Sophie's six tools before expecting the receptionist to call them.
- Choose a license if other people should have permission to reuse the files. None is set.
