# Interview workflow

Read this reference for application-contact details, interview records, interviewers, post-interview reflections, Google Calendar, preparation, shared technology knowledge, comments, outcomes, and translations.

## Application contact details

When the user reports how they submitted an application, update the associated `offer.md` fields defined in [offer schema](offer-schema.md): application channel, contact method, contact name, contact details, and submission time. Capture only supplied information and preserve `not-available` for unknown values. A contact method (for example, a web form, email, LinkedIn message, phone, referral, or recruiter) is not itself authorization to send a message or submit an application.

## Create an interview stage

Resolve the offer unambiguously; local scheduling and interview records do not require profile setup or Calendar configuration. Number stages sequentially and preserve a free-form recruiter-provided stage name; suggest the controlled stage names in [project schema](project-schema.md) when useful.

For a requested external Calendar operation, require a non-placeholder target Calendar ID from the request or project settings and validate the schedule/timezone. Missing Calendar configuration blocks only synchronization; record local logistics and report what is needed. Before a write, resolve every material field and show a preview containing:

- target Calendar ID;
- title `Interview — Company — Role — Stage`;
- start, end, duration, and timezone;
- user-provided participants;
- meeting link or location;
- minimal description and source-offer URL;
- whether the operation creates, reschedules, or cancels an event.

Default duration to 60 minutes. Use `Europe/Warsaw` only when no other timezone is stated. Ask about ambiguous dates, times, stages, or timezones. Omit reminder fields so the Calendar's existing defaults remain unchanged.

Calendar descriptions may contain only company, role, stage, source URL, meeting link or location, and user-provided participant names. Keep profile analysis, weaknesses, company research, preparation, and interview notes local.

Obtain confirmation immediately before every Calendar create, reschedule, or cancellation. Test authorization at the first Calendar operation and allow the user to authorize the connected Google Calendar integration when necessary. Store the returned event ID in the interview file.

For retries, search by stored event ID first, then exact company, role, stage, and time. If the earlier result remains uncertain, ask before creating anything that could duplicate the event.

Record local interview data even when Calendar creation fails. Mark synchronization failure, retain enough identity to retry safely, append history, and continue with preparation. Reschedules and cancellations update the interview record and append offer history.

Scheduling a recruiter screening changes offer status to `screening`; scheduling any other interview stage changes it to `interviewing`. Record this automatic transition in history because the scheduling request is explicit evidence.

## Interview file

The stage file frontmatter contains stage number and name, offer ID, scheduled start/end, timezone, duration, participants, interviewers, location or meeting link, Calendar ID, Calendar event ID, Calendar synchronization state, result, preparation files, created time, and updated time. Store each interviewer as a YAML mapping with `name` plus optional `role`, `contact_method`, and `contact_details`, as defined in [project schema](project-schema.md). Keep this local interview metadata distinct from Calendar participants.

The body contains agenda, logistics, verbatim comments, structured summary, commitments, expected next step, post-interview reflections, and `Personal notes`. Append each new verbatim comment with its timestamp. Record each supplied reflection under `## Post-interview reflections` with an explicit-offset timestamp, preserving the user's wording and earlier entries; add a correction as a new dated entry rather than rewriting the original. Update the structured summary without editing earlier raw comments or reflections.

## Preparation pack

Once the offer, stage, and local schedule details are resolved, generate the unsuffixed Polish preparation file independently of Calendar synchronization. Before drafting candidate-specific claims, use [profile workflow](profile-workflow.md#validate-evidence-for-the-task) to validate the evidence those sections need. Missing or stale evidence leaves those sections explicitly incomplete; still produce logistics, company/role briefing, technical questions, and other independent sections. Calendar success or failure must not delay or suppress preparation. Include:

- logistics checklist;
- concise company and role briefing;
- tailored introduction aligned with the offer requirements;
- likely behavioral and technical questions;
- evidence-based answer outlines linked to interview stories;
- weak areas to revise;
- questions for interviewers;
- final rehearsal checklist.

Use only technologies relevant to the offer. When a needed shared technology file is missing, create `knowledge/technologies/<technology>.md` in Polish using current authoritative sources. Cover purpose, strengths, limitations, alternatives, trade-offs, likely interview questions, version-specific details, and probable scaling, ownership, integration, deployment, testing, observability, and multi-team coordination problems.

Keep one document per technology with labeled version sections. If it exists, read and link it instead of regenerating or copying it. Add offer-specific application and challenges only to the stage preparation file. Refresh shared technology material only on explicit request.

When regenerating a preparation pack, update its managed content and generation timestamp. Preserve `Personal notes`. If managed Polish content changes, mark every existing translation stale.

## Translation

Translate preparation only on explicit request. Keep Polish in the unsuffixed file and write each requested language to a separate ISO-suffixed file, such as `01-technical.en.md`. Record the Polish source fingerprint and `stale: false` in translated frontmatter. Do not implicitly translate `Personal notes`.

## Outcomes

Use result values from [project schema](project-schema.md). Change pipeline status only after the user explicitly reports the outcome:

- `advanced` -> `interviewing`
- `rejected` -> `rejected`
- `offer-received` -> `offer-received`
- `pending`, `unknown`, or `cancelled` -> no pipeline-status change

Append the result, status mapping, and expected next step to history. Never infer an outcome from tone, comments, post-interview reflections, or a cancelled Calendar event.
