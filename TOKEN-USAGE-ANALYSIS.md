# Token usage when adding an offer

Implementation update: the skill now captures inline by default, defaults to compact company research when no mode is configured, and loads dedicated capture/schema references. Explicit full mode remains supported. Capture retries and auxiliary output are bounded, duplicate checks use frontmatter, setup validation uses metadata/hashes, and delegated evidence can travel through scoped temporary files. The full posting and record fields are preserved. Skill validation, local reference checks, and diff whitespace checks pass. The instruction path fell from 32,136 to approximately 15,000 bytes (about 53%); runtime token savings have not been measured. Live job records and settings were not changed. Dedicated deterministic helper scripts remain a possible follow-up; this implementation changes the instruction workflow.

Follow-up: setup validation is now task-specific. Capture and local record operations skip profile reads/hashes and Calendar checks entirely, including when project settings are absent. Profile-dependent assessments validate only needed evidence; Calendar operations validate Calendar requirements. Missing evidence or settings block only dependent portions of mixed requests.

The audit below describes the pre-optimization version.

Adding an offer is expensive because the skill defines it as a coordinated capture-and-research workflow, with substantial instructions and multiple transfers of the resulting content. The largest likely improvements are reducing delegation for a single offer, narrowing reference loading, and making lightweight capture the default.

This is a static audit of the current skill and the configured store on 2026-09-19. No offer was added, no workflow was replayed, and no runtime token trace was supplied or measured. Byte counts below are measured; token estimates and causal rankings are approximations. The diagnosing-bugs reproduction and fix phases were skipped because this request is an instruction-cost analysis, not authorization to execute or change the capture workflow.

## Measured baseline

| Instruction file | Bytes |
| --- | ---: |
| `SKILL.md` | 4,545 |
| `references/configuration.md` | 1,133 |
| `references/agent-routing.md` | 10,586 |
| `references/offer-workflow.md` | 7,808 |
| `references/project-schema.md` | 8,064 |
| **Normal new-offer reference path** | **32,136** |

That is roughly **8,000 tokens**, using a rough four-bytes-per-token heuristic, before runtime instructions, settings, local records, web results, reasoning, or generated files. All seven skill Markdown files total 42,199 bytes. Profile-workflow instructions add 3,880 bytes if setup validation requires that reference; interview-workflow instructions are unnecessary for a plain offer addition.

The configured store has 12 offer records across active and trash directories: 53,110 bytes in complete `offer.md` files versus 15,987 bytes in their frontmatter. Loading complete records would expose about 3.3 times as much text as loading frontmatter alone. These are possible read costs, not evidence that previous runs loaded all records.

## Main contributors

1. **Mandatory delegation adds coordination and repeated reads.** [Agent routing](references/agent-routing.md#orchestrator) assigns online lookup to research workers and file updates to a workspace worker when available. The one-offer dispatch graph sequences posting identification, company research, reconciliation, and writing. The workspace worker must read the applicable schema and workflow again (line 76), potentially repeating another 15,872 bytes, roughly 4,000 tokens. Research results also pass through the orchestrator before writing. Separate posting and company workers are possible, but not inevitable. No inline capture exception exists comparable to the status-only exception.

2. **“Add” includes company preparation research by default.** [Offer workflow](references/offer-workflow.md#company-preparation-research), lines 32–43, requires a company file with business context, recent developments, likely role context, and candidate questions. Full mode permits the primary company website plus up to two relevant sources and roughly two minutes of research. This is bounded, but time and source limits do not bound returned text or reasoning tokens. Your settings omit `offer_capture_mode`, so the effective mode is `full`.

3. **Full posting text is carried alongside structured summaries.** Offer-workflow line 26 and project-schema line 119 require both structured requirements and the available full cleaned posting. That preserves useful evidence, but creates repeated content in research results, write instructions, and generated Markdown. Compact capture currently reduces company research; it does not explicitly waive the full-posting requirement or delegation.

4. **The references mix capture with unrelated operations.** Routing is the largest file and includes setup, preparation, translation, Calendar, runtime compatibility, and several role contracts. The schema includes settings and interview-related material. A plain addition loads a broad operating manual instead of a small capture contract.

5. **Every addition depends on profile setup validation.** `SKILL.md` lines 33–34 and offer-workflow line 20 require verified profile setup. Profile-workflow line 9 includes normalized sources, fingerprints, profile analysis, and interview stories. The local CV, LinkedIn, and profile-analysis files total 14,612 bytes. Validation can operate on metadata and locally computed hashes; the skill does not require emitting all of that prose or performing fresh profile analysis for each valid addition. An implementation that rereads or reanalyses everything would incur avoidable cost.

6. **Capture fallback can create expensive outliers.** Offer-workflow line 30 requires ordinary web capture, then a matching browser tab or a newly opened tab when capture fails or lacks details. Blocked sites can therefore cause repeated attempts and large browser outputs. There is no explicit attempt or returned-content budget. This is a plausible explanation for unusually expensive individual additions, not a confirmed occurrence in a prior run.

## What is already optimized

Routing lines 51–55 specify self-contained handoffs, `fork_turns: "none"` by default, grouped batch research, one reconciled write, and targeted verification. The current skill therefore does **not** justify blaming automatic full-conversation forks or mandatory per-offer fan-out. Duplicate detection is local-only; company facts may be reused; automatic refreshes are prohibited.

Your actual workspace routing is `gpt-5.6-luna` / `medium`, and research is `gpt-5.6-terra` / `medium`. The embedded workspace default of `gpt-5.5` / `high` is not the applicable setting here. Your orchestrator entry specifies `gpt-5.6-sol` / `xhigh`, but lacks `delegate: true`; the skill says orchestration stays in the entry agent in that case. That configuration alone does not establish that an extra high-reasoning orchestrator was launched.

## Recommended changes, in priority order

1. Add an inline single-offer path: resolve settings, validate setup metadata, inspect duplicate keys, capture, write, and verify in one agent. Retain delegation for genuinely independent or larger work.
2. Split out a short capture contract and capture-only schema. Load role-routing instructions only when delegating; keep interview, translation, and Calendar rules out of this path.
3. Make lightweight capture the default if it matches your intended product behavior. Request deeper company preparation separately. Merely selecting today's `compact` setting helps research volume but leaves the other costs intact.
4. Use deterministic helpers for URL normalization, local duplicate inventory, fingerprint validation, and dashboard updates. Return decisions and small summaries instead of raw records.
5. Transfer cleaned posting text once through a scoped artifact or equivalent handoff mechanism. Changing which role may persist that artifact requires adjusting the current research-read-only rule.
6. Give capture explicit attempt and output budgets, and verify only changed fields and managed regions as the skill already directs.

To establish the actual dominant cause, inspect one existing capture trace and separate instruction reads, tool-result content, generated output, reasoning, and worker usage. Avoid predicting a percentage saving from this static audit: a clean posting and a blocked browser capture can have very different cost profiles.
