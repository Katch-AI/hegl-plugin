# Experiment backlog

A per-box, prioritized list of hypotheses you intend to test. You own it; the user only reads it.

## Tools

- `create_experiment(decision_box_id, title, hypothesis, expected_gain?, basis?, cost_to_test?, run_cost_impact?, prerequisites?)`
  Appends to the box's backlog (`status: BACKLOG`, next `position`). `number` is a stable per-box label (EXP-NN) — it never changes on reorder.
  - `title` — a short label for the experiment (the EXP-NN row heading).
  - `hypothesis` — the claim you're testing and *why* you expect it to work, in prose (`"few-shot anchors on borderline refunds should lift precision — the model keeps mislabeling the edge cases"`). This is the **reasoning**, distinct from `expected_gain`: `hypothesis` is the argument, `expected_gain` is the predicted magnitude.

  The structured planning fields are all optional:
  - `expected_gain` — predicted payoff, free text in whatever unit fits (`"+5pp precision"`, `"−30% run cost"`) — the *size* of the win you expect, not the reasoning (that's `hypothesis`).
  - `basis` — `MEASURED | ANALOGOUS | HUNCH`, how much to trust `expected_gain`. Only valid alongside an `expected_gain` (a confidence label qualifying nothing is rejected).
  - `cost_to_test` — the **one-time** cost to run the experiment and learn the answer. Your best estimate from the eval setup: rows × tokens/row × model price for a scoring pass, or the human time to build a new labeled set. E.g. `"one eval run over the 40-row set, ~3 credits"`, `"~2h to build the alternate prompt"`.
  - `run_cost_impact` — the **ongoing, per-production-run** cost delta **if adopted**. Read it off the candidate-flow change you're proposing: did you add a model call / retrieval hop / longer prompt, or just swap prompts? E.g. `"+1 model call/run, ~+0.02 credits"`, `"none — similar-length prompt swap"`, `"−30% tokens/run"`.
  - `prerequisites` — what must be true or done first (`"needs the CRM connection"`, `"blocked on EXP-03 landing"`).

  These cost/gain values are **estimates you derive from the change you're proposing**, not figures read from a meter — a run's credits show on `get_flow_run`'s `llmUsage` only after it has run. Ground them in the diff, the dataset size, and the box's measured `cost` metric; always in credits, never dollars.
- `update_experiment(id, title?, hypothesis?, status?, result?, expected_gain?, basis?, cost_to_test?, run_cost_impact?, prerequisites?)`
  Move status explicitly: `BACKLOG → IN_PROGRESS → DONE` or `ABANDONED`. Nothing auto-transitions it. Only the fields you pass are changed; the rest are left as-is.
  **Record the outcome in `result`, never by rewriting `hypothesis`** — `hypothesis` is the original prediction and stays immutable, so a reader can compare "expected +5pp" against "measured +1pp". Set `result` (and usually the final `cost_to_test`/`run_cost_impact` actuals-as-estimated) when you move the experiment to `DONE`/`ABANDONED`. `basis` still requires an `expected_gain` (supplied here or already on the record).
- `reorder_experiments(decision_box_id, ordered_ids)`
  `ordered_ids` MUST list every experiment on the box exactly once, in priority order (highest priority first). A partial or foreign list is rejected.

## Linking an iteration to its hypothesis

`start_decision_box_iteration(improvement_run_id, decision_box_id, number, title, experiment_id?)` — pass `experiment_id` so the iteration records which hypothesis it tested. One experiment can have many iterations; "the resulting iteration" is derived, not stored.

## Reads

- `get_experiment(id)` — one experiment (`exp-…`) with the iterations that tested it.
- The whole backlog through `graphql`: `node(id: <decision box id>) { ... on DecisionBox { experiments { id number title hypothesis status position result expectedGain basis costToTest runCostImpact prerequisites iterations { id number } } } }` — ordered by priority (`position` ascending).
- `get_decision_box_iteration` returns the experiment an iteration tested, or `null`.
