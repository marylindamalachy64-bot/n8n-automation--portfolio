# Manual five-step event routing

[Workflow file](manual-five-step-event-routing.json) · [Portfolio index](../../README.md) · [Privacy notes](../../docs/privacy-and-history.md)

**Status:** exported and built. Not run here.

This is a basic five-step manual n8n workflow. It does not research YouTube videos, and it does not call the YouTube API or any other external service.

The file was previously at the repository root as `youtube-research-automation.json`. Before that rename, the file was `My workflow.json`, and the workflow name inside the export was "My workflow". The graph did not gain YouTube nodes in either commit. The name in this copy is "Manual five-step event routing".

## Problem

The exercise is to take one JSON object that contains several registrations, split those registrations into items, rename short keys into readable fields, and route each item by ticket type.

## What the graph does

5 nodes. The source export was inactive, and this file is inactive. There are no credentials.

```text
When clicking ‘Execute workflow’
  -> Edit Fields (raw JSON fixture)
  -> Split Out (field registrations)
  -> Edit Fields1
  -> Switch
```

`Edit Fields1` copies:

| Fixture key | Output field |
| --- | --- |
| `fn` | `first_name` |
| `ln` | `last_name` |
| `fn` and `ln` | `full_name` |
| `em` | `email` |
| `tkt` | `ticket_type` |
| `amt` | `amount` |
| `pd` | `paid` |

The Switch compares `ticket_type` with `vip`, `regular`, and `student`. Each match has a renamed output (`vip`, `Regular`, `Student`). The fallback output is `extra`. No node is connected after the Switch, so every item stops there.

A `complimentary` ticket does not match the three rules, so a static reading of the Switch sends it to `extra`. That path was not executed in n8n.

## Synthetic fixture

The raw JSON in `Edit Fields` is an invented workshop. It replaces an earlier fixture that contained real mailbox addresses. Amounts are made-up numbers so the `amount` field has something to copy. They are not payments.

| first_name | last_name | email | ticket_type | amount | paid | Switch output, from the rules |
| --- | --- | --- | --- | --- | --- | --- |
| Avery | Stone | avery.stone@example.com | vip | 100 | true | vip |
| Blake | Okonkwo | blake.okonkwo@example.com | regular | 40 | true | Regular |
| Casey | Nguyen | casey.nguyen@example.com | student | 15 | false | Student |
| Devon | Alvarez | devon.alvarez@example.com | vip | 100 | true | vip |
| Ellis | Rahman | ellis.rahman@example.com | regular | 40 | false | Regular |
| Frankie | Berg | frankie.berg@example.com | complimentary | 0 | true | extra |
| Gray | Ibarra | gray.ibarra@example.com | student | 15 | true | Student |

The event fields in the fixture are `Sample Community Workshop`, `2026-01-15`, and `Example City`. Split Out does not pass those parent fields to the later nodes unless n8n's split options are changed. The current options are empty.

## Setup

1. Import `manual-five-step-event-routing.json`.
2. Open the manual trigger and run it only if you want to see the five nodes on your own n8n instance.
3. No credential or webhook replacement is required.

## Illustrative item

This is the field mapping applied to the first fixture row. It is a reading of `Edit Fields1`, not an execution log.

```json
{
  "first_name": "Avery",
  "last_name": "Stone",
  "full_name": "Avery Stone",
  "email": "avery.stone@example.com",
  "ticket_type": "vip",
  "amount": 100,
  "paid": true
}
```

## Test checklist

Not done in this repository.

- [ ] Manual run produces seven items.
- [ ] `full_name` is the two name fields joined by a space.
- [ ] vip, regular, and student items leave through the matching Switch outputs.
- [ ] The complimentary item leaves through `extra`.
- [ ] No credential prompt appears.

## Validation limits

- There is no pinned output and no saved execution.
- The Switch output names are not a completed registration system. Nothing stores or emails the routed items.
- The historical YouTube filename is not a description of this graph.
