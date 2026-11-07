# Studio Inbox — email sorting and enquiry extraction

[Workflow file](studio-inbox-email-sorting.json) · [Portfolio index](../../README.md) · [Privacy notes](../../docs/privacy-and-history.md)

**Status:** exported and built. Not run here. Sending a reply to the person who emailed is unfinished.

The language model in this workflow is Anthropic Claude, selected in the export as `claude-sonnet-5` (the source node label was "Claude Sonnet 5"). It does not use OpenAI.

## Problem

An interior-design studio inbox needs a first pass over incoming mail: new project enquiries should be stored as structured rows, and other mail should be brought to a person's attention. The export classifies each message and, for a new enquiry, extracts a fixed set of fields.

## What the graph does

13 nodes. The source export was inactive, and this file is inactive.

```text
Receive New Email (Gmail trigger, every minute)
  -> Classify Email
       -> New client enquiry
            -> Extract Client Details
            -> Prepare Sheet Data
            -> Save Client Enquiry (Google Sheets append)
       -> Existing client
            -> Draft Client Reply
            -> Send Existing Client Update1
       -> Job application -> Job Application Update
       -> Spam -> Send Spam Notification
       -> Other -> Send Other Notification
```

Three Anthropic chat-model nodes are connected as the language models for classification, extraction, and the reply draft. There is no separate provider node.

Classifier categories stored in the node:

| Category | Role in the graph |
| --- | --- |
| New client enquiry | New interior-design, renovation, decoration, or property project. |
| Existing client | Current client update, question, follow-up, or complaint. |
| Job application | Employment enquiry or CV. |
| Spam | Unwanted or irrelevant mail. |
| Other | Anything that does not fit the four categories above. |

The extractor asks for `name`, `email`, `phone`, `project_type`, `budget` (number), `property_location`, and `start_timeline`. Its instructions say to leave a field empty when the message does not provide it, and not to invent a budget.

`Prepare Sheet Data` sets `ready_to_go` to true only when both `budget` and `start_timeline` are present. It does not stop the append. The sheet node still receives the row.

The four Gmail send nodes are notifications to `owner.notifications@example.com`. They are not addressed to the sender.

- Existing-client notifications send `{{ $json.text }}` after the draft node. In n8n that is the draft node's output text, not a message created by a Gmail reply action.
- Job-application, spam, and other notifications send the original trigger text.

The draft prompt asks for a short professional reply and tells the model not to invent information or promises. The prompt text is stored in the node. This repository has no model output from it.

## Services

| Service | Where it is used |
| --- | --- |
| n8n | Workflow host. |
| Gmail | Trigger and four notification sends. |
| Anthropic | `claude-sonnet-5` on the three chat-model nodes. |
| Google Sheets | Append one row for a new client enquiry. |

## Setup and import

1. In n8n, import `studio-inbox-email-sorting.json`.
2. Select your own credentials where the placeholders are reported:
   - Gmail nodes: `REPLACE_GMAIL_OAUTH_CREDENTIAL`
   - Anthropic nodes: `REPLACE_ANTHROPIC_API_CREDENTIAL`
   - Google Sheets node: `REPLACE_STUDIO_GOOGLE_SHEETS_CREDENTIAL`
3. The source Anthropic nodes were bound to n8n's managed AI gateway and did not contain an API key. This file expects a normal Anthropic credential instead. Confirm that `claude-sonnet-5` exists on the n8n and Anthropic versions you use. This repository did not query the model list.
4. Create a spreadsheet and put its id in `YOUR_STUDIO_ENQUIRY_SPREADSHEET_ID`. The sheet locator is `gid=0`, the first sheet. Columns written by the node: `name`, `email`, `phone`, `project_type`, `budget`, `property_location`, `start_timeline`, `ready_to_go`.
5. Replace `owner.notifications@example.com` on all four send nodes before activating the workflow.
6. Leave the workflow inactive until those replacements are done. The Gmail trigger is set to poll every minute.

The original pinned Gmail item was removed. Do not restore it from Git history.

## Illustrative input and output

The following message is invented for this README. It is not a message the workflow received, and the JSON is the field shape the sheet node expects, not a recorded model response.

```text
From: jordan.lee@example.com
Subject: Kitchen renovation in Example Town

Hello, I am Jordan Lee (jordan.lee@example.com, 555-0100).
I want to renovate a kitchen in Example Town.
My budget is 15000 and I would like to start in March.
```

```json
{
  "name": "Jordan Lee",
  "email": "jordan.lee@example.com",
  "phone": "555-0100",
  "project_type": "kitchen renovation",
  "budget": 15000,
  "property_location": "Example Town",
  "start_timeline": "March",
  "ready_to_go": true
}
```

`555-0100` is a fictional phone number. `ready_to_go` is true in this illustration because both budget and start timeline are filled. A message with no budget would still be appended, with `ready_to_go` false, if the classifier chose "New client enquiry".

## Test checklist

Not done in this repository.

- [ ] Import completes and every credential placeholder is replaced.
- [ ] A message you send yourself is classified into the category you expect.
- [ ] A new-enquiry fixture writes one sheet row and does not invent an empty budget.
- [ ] An existing-client fixture produces a draft notification to your mailbox, not to the sender.
- [ ] Job, spam, and other fixtures each hit only their own notification node.
- [ ] The workflow is inactive again after the test.

## Validation limits

- No execution is stored in the file, and none was run for this portfolio update.
- Classification and extraction quality are not measured.
- `ready_to_go` is not a gate.
- The draft is not sent back to the client.
- There is no error-handler workflow in this export.
- Polling every minute and appending rows will consume Gmail and Sheets quota once the workflow is activated. That behavior was not measured.
