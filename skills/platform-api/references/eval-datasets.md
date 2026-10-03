# Eval datasets

A **box-level, reusable** record of the data a decision box is built and scored against. A box's input/output schemas are immutable, so every dataset stays applicable to every later iteration: **record a dataset once, then reference it from many iterations.** Datasets are append-only and versioned (`version` is your free-text label; `derived_from` notes lineage). "The latest set" = the newest `VALIDATION` dataset on the box. You own these; the user only reads them.

Rows are **not** stored on Hegl. `source_ref` points at the artifact (git / workspace pointer); `sample_identifiers` lets you rebuild the exact set if the artifact is lost.

**Clean the data before you record it.** An auto-derived label (a CRM stage, a subject-line heuristic, a joined field) is a *guess* — directly inspect a handful of samples, verify each label is actually correct, note any quirks, and re-label with subagents if inconsistencies show up, before you trust the set. Garbage in, garbage out: a dirty eval set silently wastes every downstream hour of optimization. Capture what you found in `composition_notes`. Procedure: `implementing-decision-boxes` → "Eval set".

**Represent every class.** Rare outcomes need enough rows to score: record how you got them (`sampling: STRATIFIED | OVERSAMPLED`, per-class counts in `classes`) and mark rows you wrote yourself with `provenance: "synthetic"` in the annotations.

## Tools

- `record_eval_dataset(decision_box_id, split, row_count, version, source_ref, sampling, classes?, composition_notes?, sample_identifiers?, derived_from?)`
  Records one dataset on the box. `split` is `TRAINING | VALIDATION`. `sampling`: `PROPORTIONAL | OVERSAMPLED | UNDERSAMPLED | STRATIFIED | SYNTHETIC | OTHER` (use `OTHER` + `composition_notes` when none fit). `classes` is an array of `{name, count, notes?}`; counts need **not** sum to `row_count` (multi-label / multi-class sets). `sample_identifiers` is one stable string per row.
- `record_eval_dataset_annotations(eval_dataset_id, annotations: [{ sample_identifier, known_target_defect?, confidence?, provenance?, note? }])`
  Per-row annotations on one eval-dataset version, keyed by `sample_identifier` (must match an entry in that dataset's `sample_identifiers`). **Bulk upsert**: re-recording a `sample_identifier` replaces that row's fields; rows you don't send are left untouched — flag defects incrementally as you find them. The array is written as one atomic statement; a single bad row rejects the whole batch and writes nothing. Each `sample_identifier` may appear **at most once per call** (a repeat is rejected rather than silently taking the last value) — dedupe before you send.
  - `known_target_defect` — the row's *target* (label) is wrong, so the candidate "failing" it is target-side noise, not model error. This is the flag the dashboard counts to lower the ceiling.
  - `confidence` — `HIGH | MEDIUM | LOW`, how sure you are the row is a genuine target defect. **Only valid when `known_target_defect: true`** (a confidence qualifying no defect is rejected).
  - `provenance` — where/how the row was sourced or labeled (free text).
  - `note` — why the target is defective (free text).
  Annotations are per **dataset version**: when you grow the eval set (re-pull → new `record_eval_dataset`), re-record the flags for the rows still present.

## Linking an iteration to the dataset it used

`record_decision_box_iteration(iteration_id, narrative, …, eval_dataset_id?)` — pass `eval_dataset_id` (an `eds-…` from a prior `record_eval_dataset`) to record which dataset the iteration was evaluated on. The dataset must belong to the same box, else the error is "Eval dataset not found". One dataset is reused across many iterations.

Per-metric split values still ride on `record_decision_box_iteration(metrics:)`, each entry being `{metric_definition_id, split, value}` — `split` there says which split each *value* was measured on; `eval_dataset_id` says which dataset the iteration ran against.

## Split semantics (Hegl mechanics only)

- `TRAINING` — the set you build/tune against.
- `VALIDATION` — the held-out set you score against to guard overfitting; this is the one surfaced in the dashboard ("evaluated on the latest N-row eval set"). Size it for the effect you need to detect — significance vs iteration speed/cost is a tradeoff, not a fixed number, and it grows as gains shrink; see `implementing-decision-boxes` → "Eval set".

## Explain the plateau — annotate target defects, then record both scores

When a score plateaus below 100%, some of the "misses" are usually rows whose *target* is wrong, not model errors. Make that visible and honest:

1. During scoring, flag each defective-target row with `record_eval_dataset_annotations(…, known_target_defect: true, confidence:, note:)`.
2. Compute **two** accuracies in your eval harness: **raw** (every mismatch counts) and **defect-adjusted** (flagged target defects don't count against the candidate). These are **two separate metric definitions** — `(iteration, metric, split)` is unique, so one metric cannot hold both values. The box's existing accuracy metric **is** the raw one; leave it alone and `define_decision_box_metric` **once** for the adjusted score (same `direction`, same scale, and **omit `primary`** — `primary: true` silently re-points the box, last write wins). Then send both values in one `record_decision_box_iteration(metrics: […])` call — the dashboard charts them. Raw stays primary because primary is what the dashboard headlines and compares against `target_value`; an adjusted primary would report clearing a target the box does not clear on the data as labelled.

The dashboard reads the flags to show the **effective ceiling** (`(rowCount − knownTargetDefectCount) / rowCount`) and the flagged rows as the reason, so a sub-100 plateau reads as target-side noise instead of implied model error. Hegl stores and displays the annotations and the ceiling; **you** compute the adjusted score.

## Reads

Through `graphql`, on `node(id: <decision box id>) { ... on DecisionBox { … } }`:

- `evalDatasets { id split rowCount sampling version sourceRef knownTargetDefectCount annotations { sampleIdentifier knownTargetDefect confidence provenance note } classes { name count notes } }` — newest first.
- An iteration's `evalDataset { id rowCount split }` (also on `get_decision_box_iteration`) — the dataset it was evaluated on, or `null`.
