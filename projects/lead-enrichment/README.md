# Lead enrichment and CRM pipeline

[Workflow file](lead-enrichment-crm-pipeline.json) · [Portfolio index](../../README.md) · [Privacy notes](../../docs/privacy-and-history.md)

**Status:** exported and built. Not run here.

An older portfolio README called this project planned. The current file is a 14-node export, so "planned" was incomplete. Built does not mean executed. The file has no saved run, and this update did not call Apify, HubSpot, Google Sheets, or a live webhook.

## Problem

Accept a lead posted as JSON, reject rows that are missing a name, email, company, or website, look up company and contact details, score what comes back, and create or update a HubSpot contact. Failures on the validation and enrichment branches should be appended to a sheet.

## What the graph does

The source export was `active: true`. This file is `active: false`.

```text
Lead Form Submission (POST path lead-intake)
  -> Clean & Normalize Lead Data
  -> Validate Lead Data (name, email, companyName, and website are all non-empty)
       false -> Log Enrichment Errors
       true  -> Enrich Company Details
                and also into Merge, input 2
       Enrich Company Details
            success -> Get dataset items -> Merge, input 1
            error   -> Log Enrichment Errors
       Merge (combine by position)
            -> Enrich Contact Details
            -> Merge1, input 2
       Enrich Contact Details
            success -> Merge1, input 1
            error   -> Log Enrichment Errors
       Merge1 (combine by position)
            -> Calculate Lead Score
            -> Create or update a contact (HubSpot)

When clicking ‘Execute workflow’
  -> Code in JavaScript (10 synthetic leads)
  -> HTTP Request (POST https://YOUR_N8N_HOST/webhook/lead-intake)
```

The manual trigger is not wired to `Clean & Normalize Lead Data`. It only reaches the pipeline if the HTTP node can call the webhook. The workflow must be active for that webhook to receive the post, and `YOUR_N8N_HOST` must be replaced with the host of the imported workflow. This file deliberately does not contain the previous host.

### Node behavior that is in the file

- Clean & Normalize trims the name, lowercases the email, splits a first and last name, strips common company suffixes, and derives a domain from the website. It sets `missingFields` and `isValidBasicData`. The IF node does not read `isValidBasicData`. It checks the four fields itself.
- Company enrichment runs the Apify store actor named in the node: `mambalabs/company-firmographic-enricher` ("Company Firmographics: Employees Industry HQ Revenue Clay"). The body sends the domain. `onError` is `continueErrorOutput`.
- Get dataset items reads `{{ $json.defaultDatasetId }}`. `onError` is `continueRegularOutput` and `alwaysOutputData` is true. Its only connection is to Merge. An error on this node is not wired to the sheet.
- Contact enrichment runs the Apify store actor named in the node: `vdrmota/contact-info-scraper` ("Contact Details Scraper"), starting from the cleaned website, with `maxRequestsPerStartUrl` 3, `maxDepth` 2, and `mergeContacts` true. `onError` is `continueErrorOutput`.
- The sheet appends `Name`, `Email`, `Company`, `Website`, and `Error`.
- HubSpot uses the create-or-update contact operation, keyed by the lead email, and writes `companyName`, `websiteUrl` (`https://` plus the domain), `firstName`, `lastName`, and custom properties `lead_score` and `lead_temperature`. There is no separate duplicate-search node and no error output from this node.
- Scoring caps the total at 100. Hot is 70 or above, Warm is 40 to 69, and Cold is below 40.

| Rule in the scoring code | Points |
| --- | --- |
| Country is United States, USA, or US | 50 |
| Country is United Kingdom or UK | 40 |
| Some other non-empty country | 20 |
| Employee count 1000 or more | 30 |
| Employee count 100 to 999 | 20 |
| Employee count 10 to 99 | 10 |
| No count, but an employee band is present | 10 |
| Industry is present | 10 |
| Lead email is present | 5 |
| At least one scraped email is present | 5 |

Phones, LinkedIn URLs, and Twitter URLs are copied onto the item. They do not add points. `country` is not created by the clean node. It has to be on the submitted body or on the merged enrichment item. The code looks for `employee_count` or `employeeCount`, `employee_band` or `employeeBand`, `industry`, `emails`, `phones`, `linkedIns`, and `twitters`. Whether those actor responses use these names was not checked against a live Apify run.

Position-based merges assume one enrichment item lines up with one lead. A run that returns a different number of items can pair the wrong rows. That failure mode is visible from the node settings and was not executed.

## Services

| Service | Credential placeholder |
| --- | --- |
| n8n webhook and code nodes | None. |
| Apify | `REPLACE_APIFY_OAUTH_CREDENTIAL` |
| Google Sheets | `REPLACE_LEAD_GOOGLE_SHEETS_CREDENTIAL` |
| HubSpot | `REPLACE_HUBSPOT_OAUTH_CREDENTIAL` |

The Studio Inbox workflow uses a different Sheets placeholder because the source export had a different Sheets credential record. This file does not say whether both records belonged to the same Google user.

## Setup and import

1. Import `lead-enrichment-crm-pipeline.json` and leave it inactive.
2. Select your Apify, Google Sheets, and HubSpot credentials.
3. Create a spreadsheet and set `YOUR_LEAD_ERROR_LOG_SPREADSHEET_ID`. The sheet locator remains `gid=0`.
4. Create HubSpot contact properties `lead_score` and `lead_temperature` if your portal does not already have them. This file does not create properties.
5. Confirm the two Apify store actors are still available to your account. The actor selections from the export were kept.
6. Only for a private test, replace `YOUR_N8N_HOST` with the host of this imported workflow, activate it, and use the manual trigger. Deactivate it afterward. The 10 rows in the Code node are fictional.

## Synthetic fixture

The Code node returns 10 invented leads: 7 complete rows and 3 incomplete rows. Companies and domains use the reserved `.example` suffix. This replaces an earlier fixture that contained real mailbox addresses.

| Name | Email | Company | Website | Expected validation branch |
| --- | --- | --- | --- | --- |
| Avery Stone | avery.stone@example.com | Northwind Studio | https://northwind.example | Continue |
| Blake Okonkwo | blake.okonkwo@example.com | Harbor and Co | https://harbor.example | Continue |
| Casey Nguyen | casey.nguyen@example.com | Lumen Field Labs | https://lumenfield.example | Continue |
| Devon Alvarez | devon.alvarez@example.com | Paper Kite Goods | https://paperkite.example | Continue |
| Ellis Rahman | ellis.rahman@example.com | Cedar Line Logistics | https://cedarline.example | Continue |
| Frankie Berg | frankie.berg@example.com | Mesa Clockworks | https://mesaclock.example | Continue |
| Gray Ibarra | gray.ibarra@example.com | Kindred Parcel | https://kindredparcel.example | Continue |
| Harper Quinn | empty | Example Missing Email Ltd | https://missing-email.example | Error sheet |
| Indigo Shah | indigo.shah@example.com | Example Missing Website Ltd | empty | Error sheet |
| Jules Moreau | jules.moreau@example.com | empty | https://missing-company.example | Error sheet |

"Expected validation branch" is a reading of the IF node. It was not observed in n8n.

### Local scoring example

This input is synthetic. It was passed through the scoring function with Node on this machine, not through n8n, Apify, or HubSpot. `scripts/check_sanitization.py` repeats that check.

```json
{
  "name": "Avery Stone",
  "email": "avery.stone@example.com",
  "country": "United Kingdom",
  "industry": "Furniture",
  "employee_count": 120,
  "emails": ["hello@example.com"]
}
```

The function returns score 80 and temperature Hot, with these reasons:

- Tier-1 country (UK): +40
- Medium company (120+ employees): +20
- Industry identified (Furniture): +10
- Lead email provided: +5
- Public company email found: +5

That does not show that the Apify actors return `country`, `industry`, `employee_count`, or `emails`.

## Test checklist

Not done in this repository.

- [ ] An incomplete synthetic lead reaches the error sheet and does not reach HubSpot.
- [ ] A complete synthetic lead reaches both Apify nodes. Record the real response fields and compare them with the names the scoring code reads.
- [ ] The position merges still pair one lead with one enrichment item.
- [ ] HubSpot shows one contact and the two custom properties.
- [ ] Submitting the same synthetic email again shows whether create-or-update deduplicates. The export has no separate duplicate branch to inspect.
- [ ] A forced Apify error on company enrichment, dataset retrieval, and contact enrichment shows which of those three actually append a sheet row.
- [ ] Deactivate the workflow and remove the test contacts and sheet rows when finished.

## Validation limits

- No end-to-end run, success rate, or duplicate-handling result is stored here.
- Actor field names, HubSpot property creation, and merge alignment are unverified.
- Get dataset items does not have an error-sheet connection.
- The HTTP fixture is not a substitute for a logged execution.
