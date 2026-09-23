# Offer schema

Authoritative schema for offer records and the dashboard. Create files only when needed; preserve unknown fields, manual sections, and `Personal notes`. Use quoted free-form YAML strings, lists for URLs/technologies, relative Markdown links, and offset-bearing ISO timestamps. Unavailable values are `not-available`.

## Identity

Directory: `offers/YYYY-MM-DD-company-role-short-id/`, using the local capture date and lowercase hyphenated company/role slugs. The short ID is the first eight hexadecimal characters of SHA-256 of the first canonical URL. Keep directory and `record_id` stable after capture. IDs must be unique among active offers; report a collision before writing rather than overwriting a record. Exact frontmatter `record_id` is the selector, not a prefix or directory suffix.

## Files

`offer.md` contains at least:

```yaml
---
schema_version: 1
record_id: "<short-id>"
company: "<value>"
role: "<value>"
source_urls: []
canonical_urls: []
requisition_id: "not-available"
published_on: "not-available"
expires_on: "not-available"
location: "not-available"
remote_policy: "not-available"
employment_type: "not-available"
compensation: "not-available"
seniority: "not-available"
application_language: "not-available"
technologies: []
capture_quality: "complete"
status: "saved"
application_channel: "not-available"
application_contact_method: "not-available"
application_contact_name: "not-available"
application_contact_details: "not-available"
application_submitted_at: "not-available"
added_at: "<ISO-8601>"
updated_at: "<ISO-8601>"
latest_snapshot: null
---
```

`capture_quality` is `complete`, `partial`, or `materially-incomplete`. The body contains responsibilities, mandatory/preferred requirements, benefits, material unavailable fields, and the full cleaned initial posting. Compact mode retains that evidence too. Later explicit refreshes go in `snapshots/<timestamp-safe-for-filename>.md`; preserve the initial capture.

`expires_on` is the offer's end-of-term/application deadline (EOT), stored only as `YYYY-MM-DD` or `not-available`. Normalize explicit, partial, and relative deadline wording using the offset-bearing capture timestamp and the timezone from project settings, defaulting to `Europe/Warsaw`. Use the nearest future date only when the source wording makes it unambiguous. Preserve the source wording in the cleaned posting evidence; never derive EOT from `added_at`, publication date, directory date, or the offer's current age.

`company.md` contains context at the requested research depth, source URLs and access dates, reused-fact attribution, and `Not quickly verifiable` markers.

`history.md` is append-only: ISO timestamp, action, before/after values where applicable, source/reason, and unresolved work. Corrections are new entries.

Statuses: `saved`, `applied`, `screening`, `interviewing`, `offer-received`, `accepted`, `rejected`, `withdrawn`, `expired`. Preserve explicit application-channel spelling. Channel describes where the application originated; contact method describes how it was submitted. Record supplied contact name, details, method, and submission timestamp locally; never invent them or store credentials. Contact data is not permission to contact anyone.

## Dashboard

Update only the region between `<!-- job-application-manager:dashboard:start -->` and `<!-- job-application-manager:dashboard:end -->` in `applications.md`. Preserve surrounding manual material. If an existing dashboard lacks unambiguous markers, preserve it and resolve the boundary before replacing content.

Each row includes `record_id`, company, role, EOT, status, last activity, next action, and a relative directory link. Render EOT as `YYYY-MM-DD` only when `expires_on` contains a normalized date; leave the cell blank otherwise. Never substitute `added_at` or another date. Order active applications by earliest scheduled action, then saved leads, then terminal outcomes. Next action is the earliest scheduled interview, otherwise an explicit recorded action, otherwise a labelled status-based suggestion such as `Decide whether to apply`.

For additions, merge the new rows with the existing managed rows and order once; preserve unaffected next-action information. Rebuild from local offer/interview metadata only if the dashboard is absent or demonstrably inconsistent. Read metadata locally and emit derived rows, not complete record bodies.
