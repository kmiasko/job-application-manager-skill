# Agent routing

Read this reference at the start of every skill invocation after resolving the data store. The data store's `settings.md` may select runtime-specific delegation options for each role. The embedded Codex defaults are:

| Role         | Model           | Reasoning effort | Responsibility                                                                                                                                                             |
| ------------ | --------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Orchestrator | `gpt-5.6-terra` | `high`           | Own the plan, analysis, delegation, reconciliation, user approvals, Calendar operations, and completion check. Use this model only for explicitly delegated orchestration. |
| Workspace    | `gpt-5.5`       | `high`           | Inspect and update local Markdown records. This is the only role allowed to write project files.                                                                           |
| Research     | `gpt-5.6-terra` | `medium`         | Gather online offer, LinkedIn, company, and current technology evidence with sources. Remain read-only.                                                                    |
| Preparation  | `gpt-5.6-sol`   | `medium`         | Draft Polish interview preparation, technology explanations, and requested translations. Remain read-only.                                                                 |

`xhigh` is a Codex reasoning-effort value. Other runtimes use their closest supported setting or their runtime default.

## Resolve configuration

Determine the current runtime from the live environment. Resolve routing in this order:

1. `agent_routing.<runtime>.<role>`, when present.
2. The legacy `agent_routing.<role>` map, but only when its fields and values are accepted by the live delegation tool.
3. The embedded defaults on Codex, or the current runtime's defaults elsewhere.

Runtime identifiers are lowercase product names such as `codex` and `claude`. Pass only options supported by the live delegation tool; for example, a runtime without a reasoning-effort option receives no `reasoning_effort` argument. The orchestrator role may additionally contain the skill-specific Boolean `delegate`; consume that field locally and never pass it to the delegation tool. A malformed configuration for the current runtime is a settings error: report its exact field and permit only repair. A legacy map whose values belong to another runtime is foreign configuration, not a setup failure; report the fallback and use current-runtime defaults. Never silently replace an applicable configured value.

When the data store's `settings.md` is absent, use current-runtime defaults so initialization can proceed. User configuration takes effect on the next invocation.

## Entry agent

If the current prompt does not explicitly assign one of the roles below, assume the orchestrator role inline. Dispatch the bounded research, preparation, and workspace tasks described below directly; this leaves maximum capacity for useful workers.

Use the offer workflow's inline fast path for a read-only list or unambiguous status-only update. Do not delegate those operations.

Spawn exactly one orchestrator for the complete request only when the applicable `agent_routing.<runtime>.orchestrator.delegate` value is explicitly `true`. Resolve its other configured options, fall back to the embedded orchestrator model only for omitted supported options, and pass no `delegate` argument to the delegation tool. If delegation or capacity is unavailable, continue as orchestrator inline and report the fallback.

An entry agent that dispatched an orchestrator waits for it, relays required user approval or missing input, and returns its verified result. It does not independently research, prepare content, mutate Calendar, or write project files.

## Orchestrator

If explicitly assigned the orchestrator role, own the operation to completion and do not spawn another orchestrator.

- Read only the workflow references needed for the request.
- Delegate online lookups and browser captures to one or more research agents when suitable subagents are available. This includes job postings, LinkedIn, company background, and current technology facts. Otherwise perform the bounded research directly and keep it read-only.
- Delegate independent preparation packs, shared technology explanations, and translations to one or more preparation agents when available. Supply each with research results and the minimum relevant local evidence. Otherwise prepare them directly.
- Delegate project-file creation, edit, move, merge, dashboard rebuild, and local fingerprint updates to one workspace role when available. Otherwise perform those writes directly, serially, after read-only work is reconciled.
- Perform profile analysis, conflict resolution, status decisions, and final synthesis when they are not preparation or online-research tasks.
- Perform confirmed Calendar operations directly after the required preview and approval. Calendar changes are external operations, not workspace file updates.
- Keep only one workspace writer active at a time. Use available capacity for independent read-only work, but do not create a subagent when its handoff is likely to cost more than the bounded task.
- After delegated work, inspect the relevant results and have the workspace agent repair any incomplete or inconsistent record before reporting completion.

## Bounded handoffs

Batch same-role work into one handoff when the tasks share sources and an output shape. Every handoff must be self-contained: include the assigned role, resolved data-store path, exact URLs or record IDs, permitted actions, required output, and a checkable completion criterion.

When the runtime controls inherited conversation history, pass no history by default. In Codex use `fork_turns: "none"`; use a small positive turn count only when essential user-provided material cannot be restated safely in the brief. Inherit the full conversation only when the worker has a concrete dependency on most of it.

For token efficiency, prefer one research worker for a batch of offers and one reconciled workspace handoff. Fan out per offer only when the user prioritizes latency or one worker cannot complete the batch reliably. After the write, validate the touched frontmatter, newest history entries, and affected dashboard rows; broaden inspection only when those checks reveal a discrepancy.

## Dispatch graph

Fan out only after the stated inputs are stable, and join every result before the single workspace writer commits dependent files:

- **Profile setup:** capture LinkedIn in a research agent while the orchestrator or workspace agent extracts and normalizes the CV. Join both normalized sources before profile analysis and interview-story generation.
- **One new offer:** complete canonical-URL duplicate preflight and capture enough posting data to identify the company and requirements. Then run company research in a research agent. Join posting and company results before the workspace write.
- **Several offer URLs:** perform one centralized duplicate preflight, then capture and research the URLs as one bounded batch by default. Reconcile cross-offer duplicates before any record is created. Fan out independent URLs only under the bounded-handoff rule. Once all inputs are stable, send one reconciled workspace request and rebuild the dashboard once.
- **Interview scheduling:** once the offer, stage, and local schedule details are unambiguous, preparation may begin independently of Calendar synchronization. After the user confirms the external operation, perform the Calendar mutation directly while independent preparation continues. Join both outcomes before the workspace agent records final synchronization state.
- **Technology material:** research independent missing technologies concurrently within capacity. After evidence is available, draft independent technology documents concurrently when capacity remains. Reconcile shared terminology and sources before the workspace writer creates the files.
- **Translations:** after the Polish managed content and its fingerprint are final, translate requested languages concurrently, one bounded task per language. Join all translations before the workspace writer creates them.

Keep configuration resolution, setup validation, duplicate and merge decisions, status transitions, history appends, dashboard writes, file moves, Calendar mutations, and final reconciliation serialized under the orchestrator and single-writer rules.

For several unambiguous status changes, resolve all exact IDs first, apply the changes in one inline batch, append one history entry per affected record, and rebuild the dashboard once.

When an external action needs user confirmation, return the exact preview to the entry agent and pause that action. Local state must make the pending action safely resumable on the next invocation.

## Workspace agent

If explicitly assigned the workspace role, complete only the bounded local-data task supplied by the orchestrator. Read the applicable schema and workflow reference, preserve manual content, perform the requested Markdown changes, verify the resulting files, and return paths plus a concise change summary. Do not browse, create preparation prose, mutate Calendar, or spawn agents.

## Research agent

If explicitly assigned the research role, complete only the bounded online evidence task. Return structured facts, direct source URLs, access dates, quoted uncertainty, and missing information to the orchestrator. Apply the offer workflow's research limits. Do not write project files, create preparation prose, mutate Calendar, or spawn agents.

## Preparation agent

If explicitly assigned the preparation role, complete only the bounded content task using the evidence supplied by the orchestrator. Return finished managed sections and source links for the workspace agent to write. Reuse existing shared technology knowledge as instructed by the interview workflow. Do not write project files, perform fresh online research, mutate Calendar, or spawn agents.

## Completion

The orchestrator finishes only after every required role result is reconciled, all intended file writes are verified, external actions have a definite outcome, and the user-facing summary identifies any degraded or blocked routing.
