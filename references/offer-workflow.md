# Offer workflow

Read this reference for offer capture, duplicate detection, company research, status, refresh, merge, removal, and restoration.

## Choose the smallest complete mode

- **Batch:** when one prompt contains several offer URLs, IDs, or status operations, resolve them together. Scan local offer frontmatter once, run one centralized duplicate preflight, group online capture and research into one bounded task by default, reconcile all results, perform one workspace write, and rebuild `applications.md` once. Preserve a separate history entry for every affected record and return one combined summary after the batch; do not emit intermediate application lists unless the user asks.
- **Status-only:** for explicit, unambiguous status or application-channel changes, read only the target `offer.md` frontmatter, the end of its `history.md`, and the managed dashboard region. Update the requested fields and timestamps, append history, rebuild the dashboard once, and verify those exact fields, history tails, and rows. Do not load or refresh posting text, company research, or profile evidence.
- **Compact capture:** use only when the user explicitly asks for `compact_capture` or project settings select it. Create the same required `offer.md`, `company.md`, and `history.md` artifacts, use the posting plus one primary official company source unless a material fact remains missing, and keep company context brief. Preserve the captured requirements as plain facts.
- **Full capture:** use the normal workflow below when no mode applies. Missing `offer_capture_mode` means `full`.

## Resolve an offer by ID

When the user supplies an offer ID, resolve it by an exact match to `record_id` in an active offer's `offer.md`; it is the primary selector for a specific offer. Do not infer an ID from company or role, accept a partial ID, or substitute a similar record. If no active record matches, report that the ID was not found. If more than one active record matches, stop and report the conflicting paths rather than choosing one.

For an explicit restoration request, also search `trash/` by exact `record_id`. Do not treat a trashed record as an active offer for any other operation unless the user explicitly identifies it. Use the record's frontmatter as authoritative, not the directory-name suffix.

## Add an offer URL

Require complete profile setup before beginning.

1. Store the submitted URL exactly, then canonicalize it by removing ordinary tracking parameters without discarding identifiers that distinguish the vacancy.
2. Scan only locally stored `offer.md` files under both `offers/` and `trash/` before creating a directory. Do not search job sites, search engines, company sites, or other external sources for similar vacancies as part of duplicate detection.
3. Treat an identical canonical URL as an existing record and report it. Compare similar company, title, location, requisition ID, or posting content only against those local records; show a suspected match and obtain confirmation before merging.
4. Treat postings as separate when requisition IDs differ or role scope, seniority, location or remote policy, contract type, or project differs materially. Compensation-only and wording-only changes normally describe an update.
5. For a new vacancy, create the stable directory described in [project schema](project-schema.md), capture the required metadata, and store both structured facts and the available full cleaned posting text in `offer.md`.

For a batch, complete steps 1-4 for every URL before creating any directory. Reuse one local inventory and reconcile cross-offer suspected duplicates first.

Try ordinary web capture first. If it fails, returns bot verification, or omits material details, inspect an existing user browser tab for the canonical URL when browser control is available. If no matching tab exists, open the URL in a controllable user browser. Reuse the user's authenticated session, but leave CAPTCHA and interactive security verification to the user; continue capture after the user completes it. Only when browser-tab capture is unavailable or still blocked, create a partial record from available metadata, mark capture quality, and ask the user to paste or upload the missing description. Never invent requirements.

## Company preparation research

Create `company.md` automatically for a new offer. Check the company's primary website and no more than two immediately available relevant sources. Stop promptly at roughly two minutes rather than broadening the search. Include only material that helps the user demonstrate that they understand where they are applying:

- concise company, product, customer, and business-model summary;
- relevant recent developments found within the limit;
- likely role or project context and why the position plausibly exists;
- informed questions the candidate could ask.

Record direct source URLs and access dates. Mark missing sections `Not quickly verifiable`. Do not investigate interviewers. Refresh only on explicit request.

For another offer at the same company, verified facts may be reused. Keep a complete `company.md` in the new offer and link to the earlier record from which facts were reused.

## Status and history

New offers start as `saved`. Record `applied` only when the user explicitly says they applied; include date and channel. When supplied, also record the application contact method, contact name, contact details, and submission timestamp in `offer.md` using [project schema](project-schema.md). The channel says where the application originated, while the contact method says how it was submitted. Do not guess missing contact data or treat it as permission to contact anyone. Append every status or material record change to `history.md` and update the dashboard.

For a status-only request, the controlled status values are `saved`, `applied`, `screening`, `interviewing`, `offer-received`, `accepted`, `rejected`, `withdrawn`, and `expired`. Preserve an explicit application-channel spelling. Use `not-available` for application details the user did not supply. This paragraph plus the status-only mode above is self-contained; unrelated project-schema sections need not be loaded.

Allow an explicitly requested unusual transition after warning the user. Do not infer status from interview comments. Interview scheduling and explicitly reported outcomes use the mappings in [interview workflow](interview-workflow.md).

If a later operation fails after valid offer data has been written, retain the work, label incomplete sections, append unresolved work to history, update the dashboard, and report the failure. Never roll back a successfully captured offer.

## Refresh an offer

Refresh only on explicit request. Keep the initial cleaned posting in `offer.md`; store each later capture in `snapshots/<ISO-timestamp-safe-for-filename>.md`, update `latest_snapshot`, and summarize differences in history.

## Merge confirmed duplicates

Keep the oldest directory as canonical. Combine source URLs and unique captured information, retain conflicts explicitly for user resolution, and append a merge event. When two directories already exist, move the redundant one to `trash/` with a backlink to the canonical record. Never silently choose between conflicting facts.

## Remove and restore

For explicit deletion, show the exact offer and obtain confirmation, then move its complete directory to `trash/` and append the move to `trash/history.md`. Do not cancel associated Calendar events. Show them and ask separately about each external cancellation.

On explicit restoration, move the directory back under `offers/`, append restoration history, and rebuild the dashboard. Warn and ask before resolving a destination-name or record-identity conflict.
