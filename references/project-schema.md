# Project schema

Use this reference whenever reading or writing the job-search workspace.

## Layout

```text
settings.md
cv.md
linkedin.md
profile-analysis.md
applications.md
knowledge/
  interview-stories.md
  technologies/
    <technology>.md
offers/
  YYYY-MM-DD-company-role-short-id/
    offer.md
    company.md
    history.md
    snapshots/
      <timestamp>.md
    interviews/
      01-<stage>.md
    preparation/
      01-<stage>.md
      01-<stage>.en.md
trash/
  history.md
  <removed-offer-directories>/
```

Create directories and files only when their workflow needs them. Treat files outside this layout as user-owned and leave them untouched unless the user explicitly requests an operation on them.

## Markdown conventions

- Put stable machine-readable fields in YAML frontmatter and explanatory or source content in Markdown sections.
- Write timestamps as ISO 8601 with an explicit UTC offset. Interpret an unstated timezone as `Europe/Warsaw` and use `YYYY-MM-DD` for directory dates.
- Quote free-form strings in frontmatter. Use YAML lists for URLs and technologies.
- Represent unavailable captured values as `not-available` and explain material omissions in the body.
- Use lowercase hyphenated slugs for directories and generated filenames. Keep Polish preparation filenames unsuffixed; append an ISO language suffix to translations, such as `.en.md`.
- Use relative Markdown links within the project.
- Preserve manual material. A `## Personal notes` section is user-owned. Never replace or translate it implicitly.
- For generated regions inside a mixed manual file, delimit only the generated region with matching HTML comments such as `<!-- job-application-manager:dashboard:start -->` and `<!-- job-application-manager:dashboard:end -->`.

## Settings schema

`settings.md` begins with:

```yaml
---
schema_version: 1
setup_complete: false
cv_file: "<required: absolute file path>"
linkedin_profile_url: "<required: LinkedIn profile URL>"
google_calendar_id: "<required: Google Calendar ID>"
timezone: "Europe/Warsaw"
technical_analysis_language: "pl"
default_interview_language: "pl"
offer_capture_mode: "full"
agent_routing:
  codex:
    workspace:
      model: "gpt-5.6-luna"
      reasoning_effort: "medium"
    research:
      model: "gpt-5.6-terra"
      reasoning_effort: "medium"
    preparation:
      model: "gpt-5.6-sol"
      reasoning_effort: "high"
---
```

Visible placeholder values are missing values. `offer_capture_mode` is optional and accepts `full` or `compact`; missing means `full`, and an explicit request for the current invocation overrides it. `agent_routing` is optional and does not determine whether profile setup is complete. Each runtime key may contain only the delegation options that runtime supports. The orchestrator role may also contain `delegate: true`; without that explicit flag, the entry agent orchestrates inline. Preserve a legacy direct role map; [agent routing](agent-routing.md) applies it only when its values are accepted by the live runtime. The body explains that Polish is the primary language, routing changes take effect on the next invocation, and Calendar credentials are held by the connected integration, never this file.

## Offer directory identity

Build a directory name from the local capture date, normalized company, normalized role, and the first eight hexadecimal characters of SHA-256 over the first canonical offer URL. Strip tracking parameters when canonicalizing but store both original and canonical URLs. Keep the directory name and short ID unchanged when sources or titles change.

`record_id` is that stable short ID and is the user-facing selector for an offer. It must be unique among active offers. Use an exact `record_id` match when the user targets an offer by ID; never treat a prefix, a directory suffix, or a similar company/role as a match.

## Offer files

`offer.md` frontmatter contains at least:

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

Allowed `capture_quality` values are `complete`, `partial`, and `materially-incomplete`. The body contains responsibilities, mandatory requirements, preferred requirements, benefits, unavailable fields, and the full cleaned posting text available at initial capture.

`company.md` contains the concise company preparation research, source URLs, access dates, reused-fact attribution, and `Not quickly verifiable` markers.

`history.md` is append-only. Each entry contains an ISO timestamp, action, before/after values when applicable, source or reason, and unresolved work. Corrections are new entries, not rewrites of prior events.

## Controlled values

Offer statuses are:

- `saved`
- `applied`
- `screening`
- `interviewing`
- `offer-received`
- `accepted`
- `rejected`
- `withdrawn`
- `expired`

Suggested application channels are `company-site`, `LinkedIn`, `Pracuj.pl`, `Just Join IT`, `No Fluff Jobs`, `referral`, `recruiter`, and `other`. Preserve any explicit user-provided channel. `application_channel` identifies where the vacancy or application originated; it is distinct from the contact method used to submit the application.

For an application the user has submitted, record `application_contact_method`, `application_contact_name`, `application_contact_details`, and `application_submitted_at` when supplied. Suggested contact methods are `web-form`, `email`, `linkedin-message`, `phone`, `referral`, `recruiter`, and `other`; preserve the user's wording. Details may hold a portal URL, recipient address, confirmation reference, or other user-provided context, but never a password, cookie, access token, or other credential. Leave unavailable values as `not-available`; do not invent, search for, or require them.

Suggested interview stages are `recruiter`, `hiring-manager`, `technical`, `live-coding`, `system-design`, `team`, and `final`. Preserve arbitrary recruiter-provided stage names.

Interview results are `pending`, `advanced`, `rejected`, `offer-received`, `cancelled`, and `unknown`.

Each interview-stage frontmatter may also contain an `interviewers` YAML list. Each item uses `name` and, when available, `role`, `contact_method`, and `contact_details`. Preserve interviewers that are already captured; only add or update the people and fields the user identifies. Contact details remain local and are never copied to Calendar unless the user separately supplies the corresponding participant data for that event.

## Dashboard

`applications.md` is a derived index. Replace only its managed dashboard region. List active offers first, ordered by earliest scheduled action; then saved leads; then terminal outcomes. Include the offer's `record_id`, company, role, status, last activity, next action, and a relative directory link. Show the ID in every dashboard row so the user can target that offer in a later request.

Prefer the earliest scheduled interview as next action. Otherwise use an explicitly recorded action. If neither exists, show a conservative status-based suggestion such as `Decide whether to apply` and label it as a suggestion.

## Translations and staleness

Polish is authoritative and uses the unsuffixed filename. A translated file records the source file and source fingerprint in frontmatter. When the Polish managed content changes, set `stale: true` in existing translations. Refresh a translation only on explicit request.
