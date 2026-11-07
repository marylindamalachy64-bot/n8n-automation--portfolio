# Privacy and Git history

This branch sanitizes the current files and corrects the portfolio notes. It does not rewrite Git history, force-push, change repository visibility, or delete the repository. The public repository URL stays the same. Until a later, separately authorized history rewrite, older commits on `main` still contain the pre-sanitization files.

## What the current files no longer contain

The exports on this branch had personal and third-party data and live account bindings removed or replaced:

- A pinned Gmail item on the Studio Inbox trigger, including the message body, headers, and mailbox addresses. One of those addresses was the workflow owner's notification address. Others were not.
- The owner's notification address, which had been hardcoded on Gmail send nodes in Studio Inbox and PharmaCare. Those nodes now use `owner.notifications@example.com`.
- Nine mailbox addresses in the lead-enrichment manual fixture, and seven mailbox addresses in the five-step manual demo. Both fixtures are now synthetic `example.com` data.
- n8n credential record IDs for Gmail, Google Drive, Google Sheets, Apify, and HubSpot.
- The n8n instance id, workflow id, and version id stored in each n8n export.
- Node `webhookId` values.
- A Google Drive folder id and two Google Sheets document ids, including cached Google URLs.
- A full n8n webhook URL in the lead-enrichment HTTP node. The path `lead-intake` is unchanged so the webhook node and the HTTP fixture still refer to the same path. The host is `YOUR_N8N_HOST`.
- A PharmaCare `errorWorkflow` id. The handler workflow was never in this repository. The setting is now `REPLACE_ERROR_WORKFLOW_ID`.
- Six Vapi tool IDs, two Vapi knowledge-file IDs, and ElevenLabs voice IDs on Sophie.

No raw API key, OAuth token, or password string was found in the current-tree JSON. Credential fields identified n8n credential records. Those record IDs were still account-specific, so they were replaced.

Anthropic and OpenAI nodes in the source exports used n8n's managed AI gateway (`__aiGatewayManaged` with an empty credential id). No provider API key was stored. This branch removes that gateway flag and points the nodes at `REPLACE_ANTHROPIC_API_CREDENTIAL` or `REPLACE_OPENAI_API_CREDENTIAL`, so an import does not depend on the original n8n account's gateway.

Public Apify store actor selections were kept. They identify the actors the workflow calls, not an Apify user.

## Import behavior that changed

| Change | Why |
| --- | --- |
| `active` is false on every n8n workflow. | PharmaCare and the lead workflow were `active: true` in the source export. Leaving them active could start Gmail, Drive, or webhook processing on import. Studio Inbox and the manual demo were already inactive. |
| Credential ids are placeholders. | After import, select your own credential on each flagged node. |
| Google Drive and Google Sheets resource locators use mode `id` and a `YOUR_...` value. | The cached list entries belonged to the original account. |
| Managed AI gateway flags were removed. | Attach a normal Anthropic or OpenAI credential. The selected model values are unchanged: `claude-sonnet-5` and `gpt-5-mini`. |
| Pinned data is an empty object. | The pinned Studio Inbox message was real mailbox content. |
| Workflow `id` and `versionId` were removed. | Import should create a new workflow instead of colliding with the original ids. |
| The lead HTTP node posts to `https://YOUR_N8N_HOST/webhook/lead-intake`. | Replace the host before any manual test. Do not point it at a live production webhook. |

Workflow graphs, prompts, classifier categories, scoring code, and Sophie's system prompt are otherwise unchanged.

## What is still exposed

Older commits, including the current `main` branch until this change is merged, still contain the original files. A public repository lets anyone who can open those commits read them. GitHub may also retain caches. Commit metadata on those commits includes the owner's email address. This branch does not rewrite author metadata, and this note does not repeat that address.

Merging this pull request updates only the new commits. It does not remove the old ones.

## Remediation plan

Do this only with a separate, explicit decision. None of it was done here.

1. Treat the old commits as a disclosure of the pinned message and the account bindings listed above. If a third party's message was published, decide whether to tell them. Do not copy the message into a new commit, issue, or chat log.
2. On the live n8n instance, change the lead webhook path if that workflow is still active, and deactivate workflows you do not want polling. Review the connected Gmail, Google Drive, Google Sheets, Apify, and HubSpot accounts. The Git files did not contain the OAuth tokens, but the workflows were bound to real credential records.
3. In Vapi, review the assistant, the six tools, and the two knowledge files. The tool implementations are not in this repository, so they may still exist in the Vapi account.
4. To remove the data from the public history while keeping this repository URL, rewrite history with a tool such as `git filter-repo` or BFG, force-push the rewritten branches, and ask GitHub Support to purge cached views. That invalidates existing clones and open pull requests based on the old history. It needs a force-push, which this task does not allow.
5. The alternative that avoids a rewrite is to accept that the old commits remain readable for as long as the repository is public. Making the repository private would hide them from anonymous visitors and would also hide the portfolio URL. That visibility change was not made.
6. After any future rewrite, run `python3 scripts/check_sanitization.py` on the new tree and review GitHub secret scanning. The checker looks at the current files only. It does not prove that history is clean.

## Checker scope

`scripts/check_sanitization.py` fails if the current JSON or Markdown contains a mailbox address outside `example.com`, `example.org`, or `example.net`, a URL host outside the placeholder and public Apify hosts, non-empty pin data, instance ids, raw credential ids, or Sophie resource ids that are not placeholders. It prints categories and counts, not matched values.
