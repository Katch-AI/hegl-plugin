# Decision-box iterations

Per-box autoresearch tracking — open an iteration, record its result, pin the winner, and wire it to the candidate flow. The procedure that uses these tools is the `implementing-decision-boxes` skill; this file is the signature reference.

## start_decision_box_iteration(improvement_run_id, decision_box_id, number, title, experiment_id?)

Opens a running iteration on a decision box. Moves the box to `BUILDING`.

- `improvement_run_id` — the run this iteration belongs to. Must be `RUNNING`.
- `number` — your per-box sequence number (positive integer, unique per box). You own this counter.
- `title` — one-line description of what this experiment changes.
- `experiment_id` — the backlog experiment it tests (`experiments.md`).
- Not idempotent. Each call creates a new iteration. A duplicate `number` for the same box is a validation error.
- "Improvement run not found" / "Decision box not found" come back if the id doesn't resolve to a record on the agent.

## record_decision_box_iteration(iteration_id, narrative, implementation_ref?, duration_ms?, metrics?, eval_dataset_id?)

Completes an iteration with its learnings. Moves the iteration to `COMPLETED`.

- `narrative` — what you learned: lifted metrics, regressions, qualitative observations. Required, non-empty.
- `implementation_ref` — pointer to the winning code (commit SHA, filename, workspace path).
- `duration_ms` — wall-clock duration of the experiment.
- `metrics` — `[{metric_definition_id: <mdef-…>, split: TRAINING | VALIDATION, value}]`, default `[]`. Every `metric_definition_id` must belong to this box, else "Metric not found". Record `value` on the same scale as the metric's declared `unit` and keep it consistent across iterations — a `%` metric is 0–100, not 0–1 (see `implementing-decision-boxes` → metrics).
- `eval_dataset_id` — the eval dataset this iteration was scored against (an `eds-…` from `record_eval_dataset`); must belong to the same box, else "Eval dataset not found". See `eval-datasets.md`.
- Only a `RUNNING` iteration can be recorded; a `COMPLETED` one returns a status-guard error.

## add_iteration_metrics(iteration_id, metrics)

Appends metric values to a **completed** iteration. Use when a split is evaluated after the iteration was recorded — the canonical case: you recorded TRAINING metrics with `record_decision_box_iteration`, later ran VALIDATION on the pin candidate, and need a home for those numbers. `metrics` has the same shape as above.

Append-only: an existing `(metric_definition_id, split)` value on the iteration can never be overwritten — attempting it errors and writes nothing. Narrative, refs, duration, and state are immutable here; only metric values are added.

## pin_best_iteration(decision_box_id, iteration_id)

Pins a completed iteration as the box's current best. Moves the box to `READY`.

- The iteration must be `COMPLETED` and belong to the given box; otherwise a validation error.
- Re-calling to update the pin (a later experiment beats the previous best) is safe.

## pin_flow_iteration(flow_id, decision_box_id, iteration_id)

Records which iteration a candidate flow version ships for a box. Call it after porting the winning TypeScript into the AP custom-code piece and smoke-testing it.

- The box must already be wired into the flow (`wire_decision_box`); otherwise "decision_box is not wired into the flow".
- The iteration must be `COMPLETED` and belong to the named box.
- `finish_improvement_run` refuses until every box wired into the candidate flow has a pinned flow iteration and `status = READY`. The error lists the unfinished boxes by name.

## Reads

- `get_decision_box_iteration(id)` — one iteration (`dbi-…`) with its narrative, metric values, eval dataset and experiment.
- Box fields through `graphql`, on `node(id: <decision box id>) { ... on DecisionBox { … } }`:

| Field | Notes |
|---|---|
| `status` | `PLACEHOLDER`, `BUILDING`, or `READY`. |
| `currentBestIterationId` | The pinned best iteration, or `null`. |
| `maxIterations` | Per-box budget set in Hegl admin; `null` means no cap. Check before starting a new iteration. |
| `iterations` | All iterations, newest first. |

DecisionBoxIteration fields: `id`, `decisionBoxId`, `improvementRunId` (nullable), `number`, `title`, `state`, `narrative` (nullable), `implementationRef` (nullable), `durationMs` (nullable), `metrics { split value metricDefinition { name unit targetValue } }`, `startedAt`, `finishedAt` (nullable), `createdAt`, `updatedAt`.

## Enums

Box status:

| Value | Meaning |
|---|---|
| `PLACEHOLDER` | No iterations started; box is a stub. |
| `BUILDING` | At least one iteration is running or has run but no winner pinned. |
| `READY` | A completed iteration is pinned as the current best. |

Iteration state:

| Value | Meaning |
|---|---|
| `RUNNING` | Iteration opened; eval in progress. |
| `COMPLETED` | `record_decision_box_iteration` has been called with a narrative. |

## Idempotency

| Tool | Idempotent? | What happens on re-call |
|---|---|---|
| `start_decision_box_iteration` | No | Each call creates a new iteration. Duplicate `number` for the same box returns a validation error. |
| `record_decision_box_iteration` | No | Calling on an already-`COMPLETED` iteration returns a status-guard error. |
| `pin_best_iteration` | Re-callable | Safe to call again to update the pin when a later iteration beats the previous best. |
| `pin_flow_iteration` | Re-callable | Safe to call again to update which iteration the flow ships. |
