# Improvement runs

An **improvement run** is the implementation-phase episode: you build out (or later improve) a candidate flow's decision boxes and report progress to Hegl. Hegl records the run and exposes it as the read model for the user-facing dashboard; it never orchestrates the work.

The procedure that uses these tools is the `implementing-decision-boxes` skill — this file is the signature reference.

The human gate (publish / request changes / cancel) is driven by the **user in the dashboard**, not by you, and is not part of this surface. You observe the gate's outcome by reading the run's `status`.

## start_improvement_run(candidate_flow_id, kind, base_flow_id?)

Opens a run against an existing candidate flow, in status `RUNNING`. The run never creates the flow.

- `kind` — `INITIAL_BUILD` (first build-out, no published flow yet) or `IMPROVEMENT` (improving a published flow).
- `base_flow_id` — the published flow this run improves from. Omit for `INITIAL_BUILD`.
- `triggeredBy` is set automatically (`USER` when started through this server).
- "Candidate flow not found" / "Base flow not found" come back as errors if an id doesn't resolve to a flow on the agent.
- A flow can carry only one open run. Starting a second while one is `RUNNING`, `PAUSED_ON_QUESTION` or `AWAITING_REVIEW` is refused, naming the open run — use `reopen_improvement_run` on it instead.

## finish_improvement_run(id, publish_narrative, result_justification?, base_flow_id?)

Submits the candidate for the user's review: `RUNNING` → `AWAITING_REVIEW`, storing the publish narrative.

- `publish_narrative` — markdown summary of the experiments run and their results. The user reads this when deciding whether to publish.
- `result_justification` — optional-but-gated — **required whenever any pinned box's primary metric is below its `targetValue`, has no VALIDATION value while a target is set, or is worse than the base version's pinned value** (all direction-aware; meeting the bar exactly passes). Explain why finishing anyway is the right call (e.g. label noise makes the target unreachable, or an apparent regression is dataset drift). Shown prominently to the user at publish review next to the shortfall numbers.
- `base_flow_id` — the live flow, after another version went live while the run was open (a `candidate_stale` event). Rebuild the candidate on it first. Finishing a candidate not built on the live version is refused, and the error names the id to pass.

### The result gate

Before calling finish, compare each pinned iteration's primary-metric VALIDATION value against (a) the metric's `targetValue` and (b) the same box's pinned value in the base flow. If anything falls short, supply `result_justification` **on the first call** — don't probe for the rejection. If you skip it, finish fails with a validation error itemizing every shortfall (box name, trigger, value, bar); fix by re-calling with the justification. This gate is soft: it never blocks a knowing below-target ship, it blocks a *silent* one.

### Notes

- Only a `RUNNING` run can be finished; any other status returns a status-guard error.
- **Wiring gate:** `AWAITING_REVIEW` is refused until every decision box wired into the candidate flow has a pinned iteration (via `pin_flow_iteration`) and `status = READY`. The error lists the unfinished boxes by name. Use `pin_best_iteration` + `pin_flow_iteration` on each box first. If the published flow has trigger flows, call `set_supported_triggers` first.
- After review the user either publishes (run → `COMPLETED`), requests changes (run → `RUNNING` — iterate and call `finish_improvement_run` again), or cancels (run → `CANCELLED`). Publishing any version sends every other open candidate back to `RUNNING` to be rebuilt on it. You observe this via the run's `status`; you do not call the gate.

## reopen_improvement_run(id)

Takes back a submission already sent for review: `AWAITING_REVIEW` → `RUNNING`, and the candidate flow back to `BUILDING`. Call it when you change the candidate after finishing — the user asked a follow-up that led to more work, say — then `finish_improvement_run` again with a narrative covering everything.

- Only an `AWAITING_REVIEW` run can be reopened; anything else returns a status-guard error.
- The candidate's stored narrative survives until the next finish overwrites it.

## Reads

- `get_improvement_run(id)` — one run with its status, the reviewer's change requests, and the trigger flows publishing would enable or disable.
- Through `graphql`: `findAgent(id:) { improvementRuns { … } }` spans every run on the agent; `flows { improvementRuns { … } }` is scoped to one flow. Newest first. Use these to locate the active run after the user sends one back to `RUNNING`.
- `Flow` lifecycle fields (`get_agent` returns `lifecycleStatus`; the rest through `graphql`): `lifecycleStatus`, `versionNumber` (monotonic per agent), `versionLabel` (e.g. "v4"), `publishNarrative` (from the run that produced this version).

ImprovementRun fields: `id`, `agentId`, `candidateFlowId`, `baseFlowId` (nullable), `kind`, `status`, `triggeredBy`, `startedAt`, `finishedAt` (nullable), `createdAt`, `updatedAt`.

## Enums

- Run status — `RUNNING`, `PAUSED_ON_QUESTION`, `AWAITING_REVIEW`, `COMPLETED`, `CANCELLED`. `PAUSED_ON_QUESTION` is set while a question card for the run is open in the dashboard; the run flips back to `RUNNING` once the last one is answered or dismissed.
- Kind — `INITIAL_BUILD`, `IMPROVEMENT`, `ERROR_FIX` (a fix Hegl started for an error incident; you read these, you never start one).
- Triggered by — `ADMIN`, `SCHEDULE`, `CODING_AGENT`, `USER`, `INCIDENT` (Hegl, for an error incident), `FEEDBACK_THRESHOLD` (Hegl, once enough feedback accumulated).
- `FlowLifecycleStatusEnum` — `BUILDING`, `CANDIDATE`, `READY`, `DORMANT`.

## Idempotency

| Tool | Idempotent? | What happens on re-call |
|---|---|---|
| `start_improvement_run` | No | Errors while the flow has an open run. Don't re-call to "resume" — read `improvementRuns` to find the existing run. |
| `reopen_improvement_run` | Yes | Reopening an already-`RUNNING` run returns a status-guard error; the run stays as it was. |
| `finish_improvement_run` | Re-callable by design | Calling again on a run the user sent back to `RUNNING` re-submits it for review with a fresh narrative. Calling on a non-`RUNNING` run returns a status-guard error. Subject to the wiring gate. |

Errors: see `SKILL.md` → "Errors and idempotency".
