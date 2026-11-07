# Privacy and Git history

The current files are the sanitized portfolio. On 7 November 2026 the writable history of this repository was rewritten and published with an atomic `--force-with-lease` push. The repository is still public at the same URL. Visibility, access, and the repository itself were not changed. No second repository was created, and no backup ref containing the original files was pushed.

This was not a complete erasure. The limits are listed below.

## What the current files no longer contain

The exports had personal and third-party data and live account bindings removed or replaced:

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

No raw API key, OAuth token, or password string was found in the JSON. Credential fields identified n8n credential records. Those record IDs were still account-specific, so they were replaced.

Anthropic and OpenAI nodes in the source exports used n8n's managed AI gateway (`__aiGatewayManaged` with an empty credential id). No provider API key was stored. The sanitized files remove that gateway flag and point the nodes at `REPLACE_ANTHROPIC_API_CREDENTIAL` or `REPLACE_OPENAI_API_CREDENTIAL`.

Public Apify store actor selections were kept. They identify the actors the workflow calls, not an Apify user.

## What the rewrite measured

Immediately before the rewrite the remote had:

| Item | Measured value |
| --- | --- |
| Unique commits | 10 |
| Writable branches | `main`, `cursor/portfolio-privacy-docs-f4ac` |
| Tags | 0 |
| Forks | 0 |
| Commits containing a flagged file blob | 7 |
| Historical blobs rewritten | 6 |

Those six blobs were the earlier copies of the workflow exports under their original filenames. The rewritten blobs drop non-empty pinned mailbox data, replace mailbox addresses with `redacted@example.com`, and replace account and resource identifiers with placeholders. Workflow node graphs, prompts, scoring code, and the public Apify actor selections were kept.

Commit metadata had 9 public-mailbox author or committer fields. Those were rewritten to `portfolio-owner@example.com`. Author and committer names were not changed. Nine `github.com` fields and two `cursor.com` fields were left as recorded.

The rewrite kept 10 commits. The already-sanitized portfolio tree was `d9ac1e71b137c726dc0d17d2d74a8ede41b89aaa` before and after the rewrite, on both the merge commit and the portfolio commit. This documentation commit is the only change after that.

The atomic force-with-lease push was accepted:

| Ref | Published rewritten tip before this note |
| --- | --- |
| `main` | `4fb0b20a19aca328168eee5de91ad8f3213c24b8` |
| `cursor/portfolio-privacy-docs-f4ac` | `7f928c2693b89176b949c69fa3e254c920e54420` |

No `refs/replace` or `refs/original` refs were created or pushed.

## Import behavior that changed in the sanitized files

| Change | Why |
| --- | --- |
| `active` is false on every n8n workflow. | PharmaCare and the lead workflow were `active: true` in the source export. Leaving them active could start Gmail, Drive, or webhook processing on import. Studio Inbox and the manual demo were already inactive. |
| Credential ids are placeholders. | After import, select your own credential on each flagged node. |
| Google Drive and Google Sheets resource locators use mode `id` and a `YOUR_...` value. | The cached list entries belonged to the original account. |
| Managed AI gateway flags were removed. | Attach a normal Anthropic or OpenAI credential. The selected model values are unchanged: `claude-sonnet-5` and `gpt-5-mini`. |
| Pinned data is an empty object. | The pinned Studio Inbox message was real mailbox content. |
| Workflow `id` and `versionId` were removed. | Import should create a new workflow instead of colliding with the original ids. |
| The lead HTTP node posts to `https://YOUR_N8N_HOST/webhook/lead-intake`. | Replace the host before any manual test. Do not point it at a live production webhook. |

## What is still exposed

Reachable branch history on `main` and `cursor/portfolio-privacy-docs-f4ac` no longer contains the removed mailbox content or the replaced identifiers. These copies still can:

- `refs/pull/1/head` still points at the pre-rewrite pull request head. Updating it by push was rejected with `deny updating a hidden ref`. The GitHub Git refs API returned HTTP 422 and `refs/pull/* is read-only`. That ref still reaches the old history. It was not deleted, because this account cannot write it.
- The pull request record still reports the pre-rewrite head and merge commit. Immediately after the force-push, all 10 pre-rewrite commits were still returned by GitHub's commit API.
- GitHub can keep serving a commit URL after no branch points at it. Purging those cached views is a GitHub Support action. Nobody was contacted from this cleanup.
- Clones and downloads made before the rewrite still contain the old objects. They cannot be recalled. Do not push an old clone back to this repository.
- No forks existed at the check. A fork taken from the old history would keep its own copy.
- The pre-rewrite commit IDs are intentionally not repeated in this file.

## Still for the owner

- Ask GitHub Support to purge the cached pre-rewrite commits and the read-only pull ref if those views must stop being public.
- On the live n8n and Vapi accounts, review the credentials, webhook path, and knowledge files that the old exports were bound to. The Git files did not contain raw OAuth tokens.
- Decide separately whether to tell a person whose message was in the old pinned mail. That message was not sent to anyone from this cleanup.
- Replace the placeholders and run the project checklists before any live use.
- Re-clone rather than reusing a clone created before the rewrite.

## Checker scope

`scripts/check_sanitization.py` and `scripts/check_docs.py` read the current files only. They do not prove that GitHub's cache or `refs/pull/1/head` is clean. A separate scan of the rewritten branch history found no remaining disallowed mailbox addresses, pinned message data, or account identifiers in those branches.
