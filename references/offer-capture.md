# Offer capture

Use for adding one or several offers and requested company research. Require an accessible configured data store and valid capture settings only. Absent project settings use compact capture and the default timezone; do not initialize profile settings or check CV, LinkedIn, profile analysis, interview stories, or Calendar. Read [offer schema](offer-schema.md) for writes; other workflow and routing references are unnecessary for ordinary capture.

## Scope and mode

Complete capture inline by default, including research and local writes. For several URLs, use one duplicate inventory, reconcile results together, and update the dashboard once. Delegate only under the entrypoint's routing conditions; a delegated research task should cover posting capture and company context together.

An explicit request overrides `settings.md`'s `offer_capture_mode` (`compact` or `full`); missing means `compact`. Accept `compact_capture` as a request for compact mode. Report invalid configured values rather than silently replacing them.

- **Compact:** capture the complete available posting and brief company context from one official company source, or reuse existing sourced company facts. Include business/product context and sources; mark unverified information. Deeper company preparation is deferred until requested.
- **Full:** additionally gather relevant recent developments, likely role/project context (label inferences), and useful candidate questions. Use the primary company site plus at most two relevant sources, stopping at roughly two minutes. Explicit research requests can set a different scope.

Both modes create `offer.md`, `company.md`, and `history.md`. Neither triggers profile analysis, interview preparation, or refresh of existing records.

Company research excludes investigating interviewers.

## Capture and duplicates

1. Preserve each submitted URL exactly. Canonicalize only ordinary tracking parameters; retain vacancy identifiers and meaningful URL components.
2. Inspect frontmatter under `offers/` and `trash/` once. Return only paths, IDs, canonical URLs, company, role, location, requisition ID, and fields needed for comparison. An identical canonical URL is an existing record, including in trash: report it without recreating or restoring it. Duplicate discovery is local-only.
3. Capture the posting. Compare company, role, location, and requisition ID against the inventory. Read the bodies of plausible matches only when needed. Different requisition IDs or materially different role scope, seniority, remote policy, contract, or project mean separate vacancies; compensation-only or wording-only changes normally mean updates. Ask before resolving a suspected duplicate or merging; use [offer workflow](offer-workflow.md) for a confirmed merge. Reconcile every URL and cross-offer match before creating batch directories.
4. Gather company context within the selected mode's budget. Reuse verified facts from an existing company record, retaining its source dates and backlink; do not imply fresh verification.
5. Create records using [offer schema](offer-schema.md), append capture history, and update the managed dashboard region once. Status starts as `saved`; record `applied` only when the user explicitly says they applied, with supplied date/channel/contact details.

## Capture budget and evidence

Try one ordinary web capture per URL. If blocked or materially incomplete, make one browser attempt: reuse a matching tab, otherwise open the canonical URL. Leave CAPTCHA and interactive security verification to the user. Resume once after the user completes verification or supplies new evidence; do not loop on unchanged failures. If capture remains blocked, save available facts as a partial record and ask for the missing description. Never invent requirements.

Extract the posting container and relevant company text rather than full page chrome or repeated browser snapshots. Prefer file-backed extraction where supported. Keep auxiliary search/navigation output to about 2,000 words per offer and company summaries to about 200 words compact / 500 words full; these budgets exclude the full posting and required facts. When a budget is reached, mark remaining company facts `Not quickly verifiable`. Missing material posting details require a partial capture marker, not silent truncation.

Keep the full cleaned posting once as source evidence; structured sections summarize it without repeating long passages. In delegated capture, research may write only an explicitly scoped temporary evidence file outside the data store when supported. Return its path plus facts, sources, dates, and omissions. Pass that path to the writer rather than copying the posting through handoff messages. Otherwise return the posting once; subsequent handoffs reference the existing result. Only the writer persists managed records.

## Completion

Verify created files, required frontmatter, capture omissions, the newest history entry, and affected dashboard rows. Read full output bodies again only if checks reveal a discrepancy. Preserve valid captured data after a later failure; record unresolved work and report it. Return a compact summary with file links, status, and missing information.
