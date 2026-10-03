---
name: implementing-decision-boxes
description: Use when the candidate flow is scaffolded and smoke-tested, to turn stub decision boxes into real implementations and improve them. Covers eval sets, the experiment backlog, iterations, metrics, porting the winner into the flow, and finishing a version for the user's review.
---

# Implementing decision boxes

Load `platform-api` (signatures) and `activepieces` (porting into the flow).

## The shape of the work

An **improvement run** is one episode of building or improving the candidate flow's boxes. You drive it; Hegl only records what you report and shows it to the user.

1. `start_improvement_run(candidate_flow_id, kind, base_flow_id?)`. `INITIAL_BUILD` for the first build, `IMPROVEMENT` (with the published flow as `base_flow_id`) afterwards.
2. For each box: eval set → backlog → experiments → pin the winner → port it into the flow. Spawn a subagent per box when boxes are independent and your harness has subagents.
   For an `IMPROVEMENT` run the candidate is a new flow: copy the tree with `IMPORT_FLOW` (`apply_activepieces_flow_operation`), replace every old `flw-`/`db-` literal with the new ids, `wire_decision_box(flow_id, decision_box_id, external_id)` each box again (wirings do not carry over), and call `set_supported_triggers(flow_id, trigger_flow_ids)` on it with every trigger flow it supports, in one call. Publishing enables exactly that list and disables the rest; a missing call switches the automation off.
3. `finish_improvement_run(id, publish_narrative, result_justification?)`. The user publishes, asks for changes, or cancels in the dashboard. Read the outcome from the run's `status` (`get_improvement_run(id)`): `COMPLETED` is done; `RUNNING` again means they asked for changes (read `changeRequests` on the run, address them, finish again); `CANCELLED` means stop.
4. Changed the candidate after submitting it — because the user asked a follow-up, say? `reopen_improvement_run(id)` puts the run back to `RUNNING`, then finish it again. Never start a second run for the same flow; Hegl refuses it, and the user would see the same version listed twice.

Write the narrative, experiment titles, hypotheses, and results in plain language. The user reads all of it.

## Eval set

The eval set is the single most important input. Nothing downstream fixes a dirty one.

- Pull real past examples with `fetching-data-via-pieces` (through a subagent if your harness has one). For an `IMPROVEMENT` run, also mine Hegl: `search_feedbacks(agent_id, query: "")` and each review's `submittedValues` (`get_flow_run(id)` lists the run's `humanReviews`, `get_human_review(id)` returns the values; a reviewer's edited fields are the corrected output; diff against the run's `decisionBoxExecutions` `outputs` to find the box that erred). Split into a training set you tune on and a validation set you score on.
- **Check the labels before trusting them.** An auto-derived label (a CRM stage, a subject-line rule) is a guess. Read a handful of rows yourself; if labels look wrong, re-label with subagents against a written rubric.
- **Represent every class, including rare ones.** Proportional sampling from a 92/5/3 source leaves a class with one or two rows, which scores nothing. Stratify or oversample until each class has enough rows to score (`sampling: STRATIFIED | OVERSAMPLED`, counts in `classes`). When the source has none of a class you know exists, write a few rows yourself and mark them `provenance: "synthetic"` in the annotations.
- **Size is a trade-off**, not a fixed number. Early on, favour a small fast set; large gains show up on small sets. As gains shrink, grow the validation set, or a 2-point lift on 40 rows is noise. Surface the trade-off to the user in their terms; do not pick silently.
- Record it: `record_eval_dataset(decision_box_id, split, row_count, version, source_ref, sampling, classes?, composition_notes?, sample_identifiers?)`. Rows stay in your workspace; Hegl stores the description. Reference it from every iteration via `eval_dataset_id`.
- **Cluster feedback and misses into named failure modes** with this skill's `scripts/cluster.py --input rows.jsonl --purpose "Which failure does this feedback report?" --out labels.jsonl --taxonomy taxonomy.json` (set `HEGL_LLM_PROXY_URL` and `HEGL_LLM_PROXY_KEY` to `proxyUrl` and `apiKey` from `issue_llm_proxy_credentials`). Jev assigns every row against the taxonomy plus `other`; only when it abstains does a frontier model add or widen a category, with contrastive criteria; a consolidation pass then merges synonyms and every row is relabelled against the final set, so arrival order does not decide the labels. Rows carry an `id` and a `text`; any other field joins the state. Seed `taxonomy.json` with categories you already know. The counts per category are the experiment backlog, ranked; the `other` rows are what the taxonomy still misses.
- **Explain a plateau instead of accepting it.** When the score stalls below the target, read every miss and sort it into a model error or a bad label. Flag bad labels with `record_eval_dataset_annotations(eval_dataset_id, annotations: [{sample_identifier, known_target_defect: true, note}])`; the dashboard then shows the real ceiling. Record two accuracies as two metrics: raw (stays primary) and defect-adjusted (defined without `primary`).

## Invariants

Before the first iteration, write down the deterministic checks a correct output always passes: line costs sum to the total, every extracted value appears verbatim in the source, numbers fall within a range. Ranges, enums, and required keys go in the output schema at design time; the rest is one validation function the eval harness and the flow both call.

- In eval, a row that still fails after the retry is a miss for the primary metric. Every box with invariants also records `invariant_failure_rate` (`%`, `LOWER_BETTER`) so the rate is visible, and experiments aim to drive it down.
- In the flow, a CODE step validates; a ROUTER sends a failing result to a second completions step whose prompt quotes the violation, then validates again. One or two extra attempts, never a loop.
- Semantic invariants (every value is grounded in the source, the draft promises nothing the policy forbids) are Jev Nouls over `{source, output}` in a `jev_decision` step (see "Jev" below); a probability over your threshold is a violation and takes the same retry edge.
- What happens when the attempts run out is the user's call, made on numbers. Once the eval gives the post-retry failure rate, ask the user, with the rate and three options: pause for a human (`await_user_input`), fail the run, or continue with the flawed output. Build what they pick.

## Metrics

- `define_decision_box_metric(decision_box_id, name, description, direction, primary?, unit?, kind?, target_value?)` once per metric; `direction` is `HIGHER_BETTER | LOWER_BETTER`. `description` is for the user. Declare only what you measure.
- **Every box records cost and latency.** Define `cost` (credits per execution, mean over the eval rows) and `latency` (ms per execution, mean), both `LOWER_BETTER`, never primary. Per-call cost is the proxy's `x-litellm-response-cost` response header (read it via `with_raw_response`); 1 dollar = 1 credit. Cost reaches the user in credits only, never dollars, including `cost_to_test` and `run_cost_impact`.
- **Keep one scale per metric across iterations.** A `%` metric is recorded 0–100, not 0–1; the dashboard appends the unit, so `0.85%` is a 100× error.
- `primary: true` re-points the box's primary metric. Last write wins, so omit it on secondary metrics.
- Values ride on `record_decision_box_iteration(metrics: [{metric_definition_id, split, value}])`; add later splits with `add_iteration_metrics(iteration_id, metrics)`. A `(metric, split)` value is write-once. Whatever you pin needs a `VALIDATION` value for the primary metric; the dashboard and the finish gate read nothing else.

## Backlog and iterations

Record ideas before trying them, so the user can see the plan:

1. `create_experiment(decision_box_id, title, hypothesis, expected_gain?, basis?, cost_to_test?, run_cost_impact?, prerequisites?)` per idea; `reorder_experiments(decision_box_id, ordered_ids)` sets priority. `hypothesis` is the reasoning, `expected_gain` the predicted size. Cost fields are your estimates from the change, not measurements.
2. `update_experiment(id, status: IN_PROGRESS)`, then `start_decision_box_iteration(improvement_run_id, decision_box_id, number, title, experiment_id)`. `number` is your own per-box counter.
3. Implement. First re-run only the rows the change should move (the last run's misses plus the class it targets); if nothing moves there, drop the idea without a full run. Then run the full set and record that run alone: `record_decision_box_iteration(iteration_id, narrative, metrics, eval_dataset_id, implementation_ref?, duration_ms?)`. Mention the probe in the narrative.
4. `update_experiment(id, status: DONE | ABANDONED, result:)`. Never rewrite `hypothesis`; the prediction stays next to the outcome.
5. `pin_best_iteration(decision_box_id, iteration_id)` when you have a winner. Re-pin freely when a later one wins. Check the box's `maxIterations` (`graphql` on `node(id:)`) before opening another.

## Running LLM calls and evals

- For evals from your own process, `issue_llm_proxy_credentials(agent_id, session_key, title?)` returns a 24-hour key for Hegl's OpenAI-compatible proxy at `{proxyUrl}/v1`; pass a stable `session_key` per working session so spend is attributed once. Run the eval loop as a script in your harness; the per-response `x-litellm-response-cost` header is the cost in credits. Use provider-namespaced model ids (`anthropic/…`, `openai/…`, `gemini/…`). Start with a frontier model to find the ceiling, then try cheaper ones, scoring cost and latency alongside accuracy. When the cheaper model loses accuracy, put both numbers in front of the user and let them accept or reject the trade-off; never pick silently either way. The proxy drops `response_format: {type: json_object}` for `anthropic/*` (only `json_schema` is honoured); strip ```json fences before parsing regardless.
- **Jev** (TypeSafe's System One model) answers typed questions about a JSON state in one pass and returns probabilities, never text, at about a hundredth of a completion's cost: `noul` gives P(yes), `choice` a distribution plus confidence, `score` a distribution over rubric levels. `POST {proxyUrl}/typesafe/v1/systemone` with the same key, body `{"model": "jev-latest", "state": …, "questions": {"<id>": {"type", "instructions", "criteria"}}}`; primitives and cookbooks at https://docs.typesafe.ai/llms.txt. The pass-through sets no cost header: cost is `usage.input_tokens` × 0.042 credits per million (output is free). It reads literally and cannot count or compare dates: compute those in code, pass only the fields the questions name, stay under 64k tokens. Use it:
  - as the cheapest tier for a closed-set box; its confidence lets the flow pause on an uncertain row instead of guessing.
  - as the judge for an open-ended box: one `score` per rubric dimension against the reference, composed in code. Before it becomes the primary metric, score the human-reviewed rows and record judge-versus-human agreement as its own metric.
  - to audit labels before recording the eval set (one `noul`: is this label consistent with the input; read the low-probability rows first) and to sort misses into model error versus label defect.
- **Run it as a script, not one model call per row.** If your harness has subagents, one runs it and returns scores and misses, not rows.
- Make the script checkpoint per row to a JSONL file and skip scored rows on restart, so a re-run after a timeout resumes instead of starting over.

## Porting the winner into the flow

Port the winning configuration **verbatim**, then smoke-test the step with sample input and assert the output, then `pin_flow_iteration(flow_id, decision_box_id, iteration_id)`. Nothing verifies the wiring for you.

- **LLM boxes** use the Hegl LLM piece's `completions` action (auth `"{{connections['<platformLlmConnectionExternalId>']}}"`, the id from `get_agent`), the same proxy contract the harness used: same model string, same messages including the system prompt, same parameters (anything without a typed field goes in `extraBody`). Read the answer from the step's `text` output in a CODE step that strips fences and parses the first balanced `{…}`; recompute derived numbers in code. Stamp `startedAt` in the prep CODE step so `durationMs` spans the completions call. Never re-implement the call in a CODE step.
- **Jev boxes and checks** use the LLM piece's `jev_decision` action with the model, state shape and questions the harness used; threshold and compose the answers in the CODE step after it.
- **Pure-computation boxes** stay CODE steps. A CODE step is a bare V8 isolate: no `fetch`, `require`, `console`, timers, or npm packages.
- **Boxes that need a package or runtime** run from a sandbox snapshot: build and test in a sandbox, `snapshot_sandbox(sandbox_id, name)`, then wire the Hegl piece's `execute_snapshot_command` with the `sbs-…` id. See `activepieces/references/sandbox-environments.md`.

## Finishing

`finish_improvement_run` refuses until every wired box has a pinned flow iteration and is `READY`. It also refuses when a pinned box's primary metric is below target, unmeasured on `VALIDATION`, or worse than the base version, unless you pass `result_justification`. Compare first and pass the justification on the first call; a knowing shortfall is fine, a silent one is not.

If you hit a decision only the user can make mid-run, ask the user and wait for the answer.
