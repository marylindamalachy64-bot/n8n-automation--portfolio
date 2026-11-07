# PharmaCare — AI customer support

[Workflow file](pharmacare-customer-support.json) · [Portfolio index](../../README.md) · [Privacy notes](../../docs/privacy-and-history.md)

**Status:** exported and built. Not run here. A customer-facing reply is unfinished. The error-handler workflow referenced by the source export is not in this repository.

PharmaCare Community Pharmacy is a fictional setting for this exercise. Marylinda Malachy has a BPharm background, which is why the example is a community pharmacy. That background is context for the workflow design. It is not clinical validation, and this repository does not show the workflow being used in a pharmacy.

## Problem

The exercise is to sort pharmacy customer email into routine questions that can be answered from approved material, and everything else that should be read by a person. The system prompt also forbids clinical advice.

## What the graph does

15 nodes. The source export was `active: true`. This file is `active: false` so importing it does not start the every-minute Gmail and Drive polls.

```text
Gmail Trigger (every minute)
  -> Get a message
  -> Text Classifier (OpenAI chat model, gpt-5-mini)
       -> Support -> AI Agent (OpenAI chat model, gpt-5-mini)
            retrieve tool: Simple Vector Store (memory key vector_store_key)
            embeddings: OpenAI embeddings
            main output: not connected
       -> Non-Support -> Send a message
            to owner.notifications@example.com
            subject: Customer Support Escalation
            body template includes the original message text

Google Drive Trigger (file created in one folder, every minute)
  -> Download file
  -> Extract from File (PDF)
  -> Simple Vector Store insert (same memory key vector_store_key)
       document loader and a second OpenAI embeddings node
```

### Implemented in the export

- Gmail trigger, full-message fetch, and a two-way text classifier.
- Support category text: routine questions that can be answered from the approved knowledge base, such as pharmacy services, prescription collection or delivery, opening hours, and general FAQs.
- Non-support category text: complaints, urgent or clinical concerns, medication-specific decisions, refund disputes, requests to change treatment, and questions that cannot be answered confidently from the approved knowledge base.
- An AI Agent whose system prompt says to answer only from retrieved knowledge-base information, not to invent, not to give clinical advice, not to change doses or treatment, and to treat pharmacist-judgement cases as human review.
- A non-support Gmail send that notifies `owner.notifications@example.com` and includes the original email text. The subject is `Customer Support Escalation`.
- A Drive path that downloads a new file from one folder and extracts PDF text into an in-memory vector store.
- `settings.errorWorkflow` set to `REPLACE_ERROR_WORKFLOW_ID`.

### Prompt instructions, not separate controls

The classifier descriptions and the agent system prompt are the only place those safety rules appear. There is no second node that blocks a clinical answer, checks a source citation, or requires a person to approve text before it is sent. The agent output is not connected to a send node, so the export also does not send an unapproved answer.

### Not in this export

- No Gmail node sends the agent's answer to the customer.
- No node replies on the original thread. The escalation send uses a fixed recipient and a new subject.
- The error-handler workflow id in the source file pointed at another workflow. That workflow was not exported, so this repository cannot say what the notification contained or whether it ran.
- No knowledge-base PDF is included. The Drive folder id is `YOUR_PHARMACARE_DRIVE_FOLDER_ID`.

The vector store node type is `vectorStoreInMemory`. Insert and retrieve are on two different triggers, so they are different executions. This repository does not show that a document inserted by the Drive path is still available when a later Gmail execution runs. Treat cross-execution retrieval as unverified. A persistent store would be a different design.

## Services

| Service | Where it is used |
| --- | --- |
| n8n | Workflow host. |
| Gmail | Trigger, message fetch, and the non-support escalation send. |
| OpenAI | `gpt-5-mini` for the classifier and the agent, plus two embeddings nodes. |
| In-memory vector store | Retrieve-as-tool for the agent, and insert on the Drive path. Memory key `vector_store_key`. |
| Google Drive | Folder trigger and file download. |

The source OpenAI nodes used n8n's managed AI gateway and did not contain an API key. This file expects `REPLACE_OPENAI_API_CREDENTIAL` instead.

## Setup and import

1. Import `pharmacare-customer-support.json`.
2. Replace credentials:
   - Gmail: `REPLACE_GMAIL_OAUTH_CREDENTIAL`
   - Google Drive: `REPLACE_GOOGLE_DRIVE_OAUTH_CREDENTIAL`
   - OpenAI chat and embeddings: `REPLACE_OPENAI_API_CREDENTIAL`
3. Confirm `gpt-5-mini` is available on your account. This repository did not query OpenAI's model list.
4. Put your Drive folder id in `YOUR_PHARMACARE_DRIVE_FOLDER_ID`. The trigger listens for `fileCreated` and the extract node expects a PDF.
5. Replace `owner.notifications@example.com` on `Send a message`.
6. Clear `REPLACE_ERROR_WORKFLOW_ID`, or point it at an error workflow you have actually created. None is included here.
7. Keep the workflow inactive until the steps above are done.

## Illustrative messages

These messages were written for this README. They are not customer mail, and no model output is shown because none was produced.

Routine shape the support category describes:

```text
From: riley.chen@example.com
Subject: Collection hours

What time can I collect a prescription on Saturday?
```

The support branch ends at the AI Agent. Nothing in the graph emails Riley, even if the agent produced an answer.

Non-support shape the escalation branch is built for:

```text
From: riley.chen@example.com
Subject: Dose change

Please change my dose before tomorrow.
```

The connected send node would notify `owner.notifications@example.com` with the subject `Customer Support Escalation` and a body that includes that original text. That is a reading of the node configuration, not a sent message.

## Test checklist

Not done in this repository.

- [ ] Import and replace every credential, folder id, notification address, and error-workflow id.
- [ ] With a PDF you wrote yourself, confirm whether a later Gmail execution can retrieve it. Do not assume the in-memory store survives between executions.
- [ ] Send yourself one routine question and one clinical request. Record which branch runs.
- [ ] Confirm the agent text is not delivered to the sender unless you add that node yourself.
- [ ] Confirm the non-support branch notifies only your mailbox.
- [ ] Deactivate the workflow when you finish.

## Validation limits

- No execution record is in the file, and this portfolio update did not run n8n.
- Approved-source behavior depends on documents you add and on retrieval that was not demonstrated across executions.
- Human escalation is implemented only as the non-support Gmail notification. The support branch does not have its own escalation send.
- Prompt text that forbids clinical advice is not an independent control and has not been evaluated against clinical cases.
- No accuracy, safety, or response-time number is available from this repository.
