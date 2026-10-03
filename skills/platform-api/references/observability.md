# Runtime lifecycle

What happens on one run. You never make these calls yourself; you compose the Hegl piece actions that do.

1. A trigger flow's production trigger fires. Its `trigger_flow` action calls `triggerFlow(trigger, inputs)`; Hegl picks the published flow, inserts a `FlowTrigger`, and enqueues dispatch. Dispatch errors show up on `flowTrigger.dispatchError`, not in `errors`.
2. Dispatch POSTs `{ flow_trigger_id, trigger, inputs }` to the candidate flow's webhook with a signature header. The `marcus_triggered` trigger verifies it; unsigned calls are dropped and no run is created.
3. `start_flow_run` (`flowTriggerId: "{{ trigger.output.body.flow_trigger_id }}"`, optional `tagline`) creates the `FlowRun` and returns `{ runId, flowRunId }`. `runId` goes to every lifecycle step as `activepiecesFlowRunId`; `flowRunId` (`fr-…`) goes to `record_artifact`, `send_email`, `await_user_input`, `record_feedback`.
4. Each decision box: CODE step, then `record_decision_box_execution` with `decisionBoxId`, `flowId`, `activepiecesFlowRunId`, `inputs`, `outputs` (or `errorMessage`, `errorType`, `stackTrace`), `durationMs`. Schema violations are computed server-side and stored, never blocking. Hegl attributes the execution to the box's pinned iteration for this flow automatically.
5. `finish_flow_run` (optional `metadata`, `tagline`) or `fail_flow_run` (`errorMessage`, `tagline`) on the error edge. `set_flow_run_tagline` sets or changes the label any time, for example before a pause.

Dispatch retries up to 10 times; then `dispatchError` is set. `dispatchedAt` non-null means it went through. Only the runtime token ends a run; you cannot finish or fail one yourself. To redo a dispatch killed by a Hegl 5xx, call `trigger_flow` again with the AP run's `steps.trigger.output.body.inputs` after checking no later run exists for that record.

A finished run that failed only on bookkeeping, or one the user wants reclassified, gets `annotate_flow_run(id, note, outcome?)`: the note shows next to the status, and `outcome` decides what the run counts as everywhere without rewriting `status`.

## Credits

`get_flow_run`'s `llmUsage`, and through `graphql` `findCodingAgentSession(id:) { llmUsage { credits requests promptTokens completionTokens cacheReadTokens cacheCreationTokens syncedAt } }` for the `sessionId` that `issue_llm_proxy_credentials` returned: the LLM credits attributed to that run or session, summed by a sweep that runs every few minutes (`syncedAt` null = nothing swept yet; the token/request counts arrive as strings).
