---
name: job-application-manager
description: Manage the user's configured Markdown job-application data store. Use when adding or updating an offer, recording application contact details, reviewing offer requirements against CV and LinkedIn evidence, tracking application status, researching a company, managing interview stages or confirmed Calendar changes, recording interviewers and reflections, or creating and translating interview preparation. Do not use to submit applications or contact recruiters.
---

# Job Application Manager

Manage job-search data in a user-configured data store. The installed skill, its per-user configuration, and the data store are separate.

## Resolve the data store

Read [configuration](references/configuration.md) before any other reference. Resolve the configured data-store directory and use it as the workspace for the entire invocation. Treat its `settings.md` as project settings. Until configuration resolves to an accessible directory, permit only configuration diagnosis or repair.

## Agent routing

Handle offer capture, read-only lists, and unambiguous status-only updates inline. Read [agent routing](references/agent-routing.md) only when delegation is requested, an applicable orchestrator setting has `delegate: true`, or independent work justifies its handoff cost. Model preferences alone do not request delegation. An explicitly assigned worker follows its bounded role without dispatching another orchestrator.

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

The entry agent, or explicitly delegated orchestrator, owns this routing:

1. Read `<data-store>/settings.md` if present and validate only settings used by this task. Missing project settings use workflow defaults; missing or invalid task-required values block only dependent work. Offer capture, lists, status/contact updates, company research, and local interview records need no profile-completeness check. Do not read profile files, compute profile hashes, or inspect Calendar configuration for those operations.
2. For explicit profile setup/repair, fit assessment, or candidate-specific interview preparation, read [profile workflow](references/profile-workflow.md) and validate only the evidence needed. For Calendar operations, validate Calendar settings and authorization through the interview workflow. In mixed requests, complete independent work and report any blocked portion; `setup_complete` is never a global gate.
3. For a read-only application list, read the managed region of `<data-store>/applications.md` and return only active offers without loading offer records. Show the normalized end-of-term date (EOT) when the dashboard row contains one; omit it for that offer otherwise. Exclude terminal statuses: `rejected`, `withdrawn`, and `expired`. Inspect only the affected offer frontmatter if the dashboard is missing or demonstrably inconsistent.
4. For adding offers or company research, read [offer capture](references/offer-capture.md). For existing-record status, refresh, merge, removal, restoration, or ID resolution, read [offer workflow](references/offer-workflow.md).
5. For application contacts or submission details, interviews, Calendar, preparation, technology knowledge, interviewer details, reflections, comments, results, or translations, read [interview workflow](references/interview-workflow.md). When an interviewer gains an email address or phone number, also read [Google Contacts synchronization](references/google-contacts.md). Read [offer workflow](references/offer-workflow.md) too when changing application status or its `offer.md` metadata.
6. Offer capture uses only [offer schema](references/offer-schema.md). Other record creation or updates use [project schema](references/project-schema.md); status-only changes use the self-contained offer-workflow rules.

If a request spans branches, read each applicable reference before changing files. Treat multiple offer URLs, IDs, or status operations in one prompt as one batch. A Calendar failure must not roll back valid local work or prevent preparation.

## Finish

Report only a compact operational summary: files created or updated, current status, next action, Calendar outcome, and skipped or incomplete work. Link directly to relevant Markdown files.
