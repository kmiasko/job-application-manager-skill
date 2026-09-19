# Agent routing

Read only when the entrypoint selects delegation. Inline capture, lists, and status updates do not need these instructions. The data store's `settings.md` may select runtime-specific delegation options for each role. The embedded Codex defaults are:

| Role         | Model           | Reasoning effort | Responsibility                                                                                                                                                             |
| ------------ | --------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Orchestrator | `gpt-5.6-terra` | `high`           | Own the plan, analysis, delegation, reconciliation, user approvals, Calendar operations, and completion check. Use this model only for explicitly delegated orchestration. |
| Workspace    | `gpt-5.6-luna`  | `medium`         | Inspect and update local Markdown records. In delegated work this is the only worker role allowed to write project files.                                                  |
| Research     | `gpt-5.6-terra` | `medium`         | Gather sourced online evidence. Managed records remain read-only; scoped temporary capture evidence is permitted.                                                       |
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

If the current prompt does not explicitly assign one of the roles below, assume the orchestrator role inline. Delegate only bounded independent work whose benefit exceeds the handoff cost; otherwise perform it inline, including local writes.

Use the entrypoint's inline paths for offer capture, a read-only list, or an unambiguous status-only update unless delegation was explicitly requested or configured with `delegate: true`.

Spawn exactly one orchestrator for the complete request only when the applicable `agent_routing.<runtime>.orchestrator.delegate` value is explicitly `true`. Resolve its other configured options, fall back to the embedded orchestrator model only for omitted supported options, and pass no `delegate` argument to the delegation tool. If delegation or capacity is unavailable, continue as orchestrator inline and report the fallback.

An entry agent that dispatched an orchestrator waits for it, relays required user approval or missing input, and returns its verified result. It does not independently research, prepare content, mutate Calendar, or write project files.

## Orchestrator

If explicitly assigned the orchestrator role, own the operation to completion and do not spawn another orchestrator.

- Read only the workflow references needed for the request.
- When independent research justifies delegation, assign bounded online lookups and browser captures to research agents. Otherwise perform the research directly.
- Delegate independent preparation packs, shared technology explanations, and translations to one or more preparation agents when available. Supply each with research results and the minimum relevant local evidence. Otherwise prepare them directly.
- Perform local writes inline unless a workspace handoff materially reduces work or is explicitly requested. When delegating writes, use one workspace role; reconcile research first and keep only one writer active, including the orchestrator.
- Perform profile analysis, conflict resolution, status decisions, and final synthesis when they are not preparation or online-research tasks.
- Perform confirmed Calendar operations directly after the required preview and approval. Calendar changes are external operations, not workspace file updates.
- Keep only one workspace writer active at a time. Use available capacity for independent read-only work, but do not create a subagent when its handoff is likely to cost more than the bounded task.
- After delegated work, inspect the relevant results and repair incomplete records through the active writer before reporting completion.

## Bounded handoffs

Batch same-role work into one handoff when the tasks share sources and an output shape. Every handoff must be self-contained: include the assigned role, resolved data-store path, exact URLs or record IDs, permitted actions, required output, and a checkable completion criterion.

When the runtime controls inherited conversation history, pass no history by default. In Codex use `fork_turns: "none"`; use a small positive turn count only when essential user-provided material cannot be restated safely in the brief. Inherit the full conversation only when the worker has a concrete dependency on most of it.

For delegated capture, prefer one research worker per batch and inline persistence; use a workspace handoff only when justified above. Pass scoped evidence-file paths instead of repeating posting text. Fan out per offer only when the user prioritizes latency or one worker cannot complete the batch reliably. After the write, validate touched frontmatter, newest history entries, and affected dashboard rows; broaden inspection only on discrepancies.

## Dispatch graph

Fan out only after the stated inputs are stable, and join every result before the single workspace writer commits dependent files:

- **Profile setup:** capture LinkedIn in a research agent while the orchestrator or workspace agent extracts and normalizes the CV. Join both normalized sources before profile analysis and interview-story generation.
- **Offer capture:** follow [offer capture](offer-capture.md) inline by default. If delegation is selected, finish local duplicate preflight, assign posting and company capture together, reconcile results and cross-offer duplicates, then persist through one writer and update the dashboard once.
- **Interview scheduling:** once the offer, stage, and local schedule details are unambiguous, preparation may begin independently of Calendar synchronization. After the user confirms the external operation, perform the Calendar mutation directly while independent preparation continues. Join both outcomes before the workspace agent records final synchronization state.
- **Technology material:** research independent missing technologies concurrently within capacity. After evidence is available, draft independent technology documents concurrently when capacity remains. Reconcile shared terminology and sources before the workspace writer creates the files.
- **Translations:** after the Polish managed content and its fingerprint are final, translate requested languages concurrently, one bounded task per language. Join all translations before the workspace writer creates them.

Keep configuration resolution, setup validation, duplicate and merge decisions, status transitions, history appends, dashboard writes, file moves, Calendar mutations, and final reconciliation serialized under the orchestrator and single-writer rules.

For several unambiguous status changes, resolve all exact IDs first, apply the changes in one inline batch, append one history entry per affected record, and rebuild the dashboard once.

When an external action needs user confirmation, return the exact preview to the entry agent and pause that action. Local state must make the pending action safely resumable on the next invocation.

## Workspace agent

If explicitly assigned the workspace role, complete only the bounded local-data task supplied by the orchestrator. For capture, read only [offer schema](offer-schema.md) and the supplied reconciled facts/evidence; other tasks load their applicable schema and workflow. Preserve manual content, perform the requested Markdown changes, verify the resulting files, and return paths plus a concise change summary. Do not browse, create preparation prose, mutate Calendar, or spawn agents.

## Research agent

If explicitly assigned the research role, complete only the bounded online evidence task. Return structured facts, direct source URLs, access dates, uncertainty, and missing information. Apply [offer capture](offer-capture.md)'s research limits and temporary evidence-file handoff when capturing offers. A specifically scoped temporary evidence file is permitted; managed project files remain writer-owned. Do not create preparation prose, mutate Calendar, or spawn agents.

## Preparation agent

If explicitly assigned the preparation role, complete only the bounded content task using the evidence supplied by the orchestrator. Return finished managed sections and source links for the workspace agent to write. Reuse existing shared technology knowledge as instructed by the interview workflow. Do not write project files, perform fresh online research, mutate Calendar, or spawn agents.

## Completion

The orchestrator finishes only after every required role result is reconciled, all intended file writes are verified, external actions have a definite outcome, and the user-facing summary identifies any degraded or blocked routing.
