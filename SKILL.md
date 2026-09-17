---
name: job-application-manager
description: Manage the user's configured Markdown job-application data store. Use when adding or updating an offer, recording application contact details, reviewing offer requirements against CV and LinkedIn evidence, tracking application status, researching a company, managing interview stages or confirmed Calendar changes, recording interviewers and reflections, or creating and translating interview preparation. Do not use to submit applications or contact recruiters.
---

# Job Application Manager

Manage job-search data in a user-configured data store. The installed skill, its per-user configuration, and the data store are separate.

## Resolve the data store

Read [configuration](references/configuration.md) before any other reference. Resolve the configured data-store directory and use it as the workspace for the entire invocation. Treat its `settings.md` as project settings. Until configuration resolves to an accessible directory, permit only configuration diagnosis or repair.

## Agent routing

After resolving the data store, read [agent routing](references/agent-routing.md) before any delegation or multi-step research, preparation, or workspace reconciliation. Handle a read-only application list or an unambiguous status-only update inline without loading routing. An agent explicitly assigned an orchestrator, workspace, research, or preparation role follows that role without recursively dispatching another orchestrator.

## Invariants

- Keep every managed data file in the workspace as Markdown. YAML frontmatter inside `.md` files is allowed.
- Treat `settings.md`, offer records, and append-only histories as authoritative. Treat `applications.md` as a derived dashboard.
- Preserve valid manual edits, unknown fields, unknown sections, verbatim comments, and every `Personal notes` section. Change only fields or managed regions required by the current request.
- Use ISO 8601 timestamps with an explicit offset. Interpret unspecified timezones as `Europe/Warsaw`; use `YYYY-MM-DD` in directory names.
- Make unambiguous local Markdown changes immediately. Obtain confirmation before duplicate merges, destructive actions, ambiguous status changes, and every external Calendar create, update, or cancellation.
- Keep credentials, cookies, access tokens, candidate assessments, weaknesses, preparation, and interview notes out of Calendar and settings.
- Never initialize Git, publish or sync the workspace, submit an application, or contact a recruiter. These actions require a separate explicit request outside this skill.
- Never refresh profiles, offers, company research, or shared technology material automatically.

## Route the request

The configured orchestrator owns this routing:

1. Read `<data-store>/settings.md` if it exists and verify setup rather than trusting `setup_complete`.
2. If setup is absent, incomplete, or stale, read [profile workflow](references/profile-workflow.md). Permit only setup and repair operations until its completion criteria hold.
3. For a read-only application list, read the managed region of `<data-store>/applications.md` and return it without loading offer records. Inspect only the affected offer frontmatter if the dashboard is missing or demonstrably inconsistent.
4. For an offer URL or ID, duplicate handling, company research, status, refresh, merge, removal, or restoration, read [offer workflow](references/offer-workflow.md). Use its batch, status-only, or compact-capture mode when applicable.
5. For application contacts or submission details, interviews, Calendar, preparation, technology knowledge, interviewer details, reflections, comments, results, or translations, read [interview workflow](references/interview-workflow.md). Read [offer workflow](references/offer-workflow.md) too when changing application status or its `offer.md` metadata.
6. Whenever creating or updating records, follow [project schema](references/project-schema.md). A status-only update may use the self-contained fast path in the offer workflow without loading unrelated schema sections.

If a request spans branches, read each applicable reference before changing files. Treat multiple offer URLs, IDs, or status operations in one prompt as one batch. A Calendar failure must not roll back valid local work or prevent preparation.

## Finish

Report only a compact operational summary: files created or updated, current status, next action, Calendar outcome, and skipped or incomplete work. Link directly to relevant Markdown files.
