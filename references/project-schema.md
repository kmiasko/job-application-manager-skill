# Project schema

Use for settings, profile, interview, and translation structure. Offer records and dashboard rules live in [offer schema](offer-schema.md); ordinary capture loads that smaller reference directly.

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
google_calendar_id: "<required for Calendar operations: Google Calendar ID>"
timezone: "Europe/Warsaw"
technical_analysis_language: "pl"
default_interview_language: "pl"
offer_capture_mode: "compact"
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

Visible placeholder values are missing values only for tasks that require those fields. `setup_complete` describes profile setup and never gates offer capture or local record operations. `offer_capture_mode` is optional; its values and default are defined in [offer capture](offer-capture.md#scope-and-mode). Preserve an explicitly configured mode. `agent_routing` is optional and does not determine whether profile setup is complete. Each runtime key may contain only the delegation options that runtime supports. The orchestrator role may also contain `delegate: true`; without that explicit flag, the entry agent orchestrates inline. Preserve a legacy direct role map; [agent routing](agent-routing.md) applies it only when its values are accepted by the live runtime. The body explains that Polish is the primary language, routing changes take effect on the next invocation, and Calendar credentials are held by the connected integration, never this file.

## Offer records

Read [offer schema](offer-schema.md) when touching offer identity, frontmatter, capture evidence, history, application contacts, or dashboard rows.

## Interview values

Suggested interview stages are `recruiter`, `hiring-manager`, `technical`, `live-coding`, `system-design`, `team`, and `final`. Preserve arbitrary recruiter-provided stage names.

Interview results are `pending`, `advanced`, `rejected`, `offer-received`, `cancelled`, and `unknown`.

Each interview-stage frontmatter may also contain an `interviewers` YAML list. Each item uses `name` and, when available, `position`, `contact_email`, `contact_number`, `contact_method`, and `contact_details`. Synchronization metadata is optional: `google_contact_resource_name`, `google_contact_sync_state`, and `google_contact_synced_at`. Sync state values are `pending`, `blocked`, `previewed`, `synced`, `noop`, and `failed`; set the timestamp only after `synced` or `noop`. `position` is the person's function in the process or job title, such as `HR`, `recruiter`, `developer`, or `engineering manager`. Preserve legacy `role`, all manual fields, and existing interviewers; use `position` for newly supplied values, and only add or update the people and fields the user identifies. When creating or rescheduling a Calendar event, include every available interviewer name, position, and contact field in the event description; omit unavailable fields without placeholders.

## Translations and staleness

Polish is authoritative and uses the unsuffixed filename. A translated file records the source file and source fingerprint in frontmatter. When the Polish managed content changes, set `stale: true` in existing translations. Refresh a translation only on explicit request.
