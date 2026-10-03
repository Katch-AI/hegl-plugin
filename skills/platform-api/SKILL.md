---
name: platform-api
description: Use when deciding which Hegl tool performs an operation (agent documents, decision boxes, flows, trigger flows, connections and config, piece installs, improvement runs, experiments, eval datasets, iterations, metrics, feedback, email, sandboxes, artifacts, platform issues), when a step has no tool and needs the graphql escape hatch, or when composing Hegl-piece actions into flow JSON. Domain reference, not a workflow.
---

# The Hegl API

Tools that create or search under an agent take `agent_id` (from `list_organizations`); tools that act on an existing record take that record's id. Every tool returns the record it touched; errors come back as the tool's error text. `graphql(query, variables)` runs any query or mutation as the signed-in user: arguments are flat (no `input:` wrapper), id variables use the per-type scalar (`DecisionBoxId!`, never `ID!`; `MetricValueInput.metricDefinitionId` is `PrefixedId!`), introspection works (`{ __type(name: "FlowRun") { fields { name } } }`), and `findX(id:)` returns `null` for anything you cannot see. There is no `findFlow` root: reach a flow via `findAgent(id:) { flows { … } }` or `node(id:)`.

## What to call when

**Documents.** `update_agent_documents(requirements?, flow_description?)`. Markdown; send the whole document each time.

**Scaffolding:**

- `create_decision_box(name, description, input_schema, output_schema)`. Schemas are immutable afterwards. `update_decision_box` for name and description.
- `install_activepieces_piece(piece_name, piece_version)` (exact semver), then poll `get_activepieces_piece_install` every 2s up to 60s until `ready`.
- `request_connection(piece_name, purpose, requested_display_name?, allowed_auth_types?, scopes?)`. Once per piece with auth. Not idempotent: a second call adds a second card. Never for the Hegl pieces. `dismiss_connection_requirement` for one no longer needed.
- `request_config(title, fields, connection_requirement_id? | config_requirement_id?)` for tenant settings (base URL, cutoff time); `get_config_requirement` to read it back. At runtime read `{{trigger.output.body.config.connection_requirements['<cr_id>'].<key>}}` or `{{trigger.output.body.config.requirements['<cfg_id>'].<key>}}` (everything Hegl dispatches sits under `trigger.output.body`).
- `create_trigger_flow(name, description?, trigger_key?)`, poll `get_trigger_flow` until `ready`. `update_trigger_flow(id, name?, description?)`.
- `create_flow(name, description?)`, poll `get_agent` until the flow's `activepiecesStatus` is `ready`. `update_flow(id, name?, description?, version_label?)`. Writing `description` opts the flow out of the automatic first-publish description.
- `wire_decision_box(flow_id, decision_box_id, external_id)`; read `findAgent(id:) { flows { id flowDecisionBoxes { externalId decisionBoxId } } }` through `graphql` first rather than catching the duplicate error.
- `set_supported_triggers(flow_id, trigger_flow_ids)` replaces the whole set in one call. Applied when the user publishes: listed trigger flows are enabled, all others disabled. Call it on every new candidate flow.
- `trigger_flow(trigger, inputs?, flow_id?)` for smoke tests and for runs the user asks for (there is no Run button; omit `flow_id` to hit the published flow). Dispatch is asynchronous: poll `findFlowTrigger(id:) { dispatchedAt dispatchError flowRuns { id } }` through `graphql`.

**Activepieces** (`activepieces` skill): flows are listed with `list_activepieces_flows`; the flow JSON itself is read with `get_activepieces_flow` and written with `apply_activepieces_flow_operation` (`IMPORT_FLOW`, `LOCK_AND_PUBLISH`, …); pieces with `list_activepieces_pieces`, `get_activepieces_piece` (`action:` / `trigger:` for one props schema), `get_activepieces_piece_options`; connections with `list_activepieces_connections`; runs with `list_activepieces_flow_runs`, `get_activepieces_flow_run`, `retry_activepieces_flow_run`; sampling with `sample_activepieces_step` and `get_activepieces_sample_data`; webhooks with `trigger_activepieces_webhook` (a webhook POST through `activepieces_request` is unsigned); anything else on the allowlist with `activepieces_request`.

**Improvement runs** (`references/improvement-runs.md`, `iterations.md`, `experiments.md`, `eval-datasets.md`): `start_improvement_run`, `create_experiment` / `update_experiment` / `reorder_experiments` / `get_experiment`, `record_eval_dataset` / `record_eval_dataset_annotations`, `define_decision_box_metric` / `update_decision_box_metric` / `set_primary_decision_box_metric`, `start_decision_box_iteration` / `record_decision_box_iteration` / `add_iteration_metrics` / `get_decision_box_iteration`, `pin_best_iteration`, `pin_flow_iteration`, `finish_improvement_run` / `reopen_improvement_run` / `get_improvement_run`. Reads of a box's status, iterations, experiments, datasets and metrics: `graphql` on `node(id:)`.

**Evals from your own process.** `issue_llm_proxy_credentials(agent_id, session_key, title?)` returns a 24-hour key for Hegl's LLM proxy, OpenAI-compatible at `{proxyUrl}/v1`; spend is attributed to the agent and shown on the usage page. Model ids are provider-namespaced; the response's `x-litellm-response-cost` header is the cost in credits.

**Sandboxes** (`activepieces/references/sandbox-environments.md`): `create_sandbox`, `get_sandbox`, `run_sandbox_command`, `write_sandbox_files`, `execute_sandbox_command`, `snapshot_sandbox`, `get_sandbox_snapshot`, `execute_snapshot_command`, `delete_sandbox`, `delete_sandbox_snapshot`.

**Artifacts.** `validate_artifact(body)` at build time returns `{valid, validationErrors, warnings, renderedHtmlPreview}`; iterate until clean. `record_artifact` runs inside the flow via the Hegl piece's action after a formatter CODE step. Body format: the `asciidoc` skill.

**Human input pauses.** `references/human-input-pauses.md`: the form DSL, `validate_form_shape`, the `await_user_input` step, the `{outcome, button, values}` result; `get_human_review(id)` reads one pause and its answer.

**Feedback.** `references/feedback.md`. **Email.** `references/email.md` (`create_agent_inbox`, `update_agent_inbox`, `discard_agent_inbox`). **Agent notes.** `references/agent-notes.md` (`create_agent_note`, `update_agent_note_status`; change requests, distinct from feedback).

**Operating.** `search_flow_runs(query, status?, since?)`, `get_flow_run`, `annotate_flow_run(id, note, outcome?)` (reclassifies a run as `FINISHED` / `FAILED` in lists and search without touching its reported status; each call replaces the previous annotation), `search_decision_box_executions(query, since?)`, `search_feedbacks(query, sentiment?, source?, confidence?, decision_box_id?, flow_id?, since?)`. `since` defaults to 7 days (30 for feedback).

**Platform issues.** `report_platform_issue(title, category, severity, body)` when a skill, tool, piece or API is missing, wrong or awkward. `category`: `MISSING_SKILL | MISSING_API | BUG | INCONSISTENCY | TOOLING | OTHER`; `severity`: `BLOCKER | FRICTION | IDEA`; `body`: what you were doing, what happened, what you tried, a suggested fix. `list_platform_issues` first to avoid duplicates; `update_platform_issue`, `discard_platform_issue`.

**Hosted agent files.** `list_workspace_files`, `read_workspace_file`, `write_workspace_file` reach the files Hegl's hosted coding agent produced for the agent.

## Runtime actions in flow JSON

Runtime mutations are never called from a CODE step. Use the Hegl piece's typed actions with `auth: "{{connections['<platform connection external id>']}}"` (the id is `platformConnectionExternalId` on `get_agent`, alongside `platformLlmConnectionExternalId` for the Hegl LLM piece): `trigger_flow`, `schedule_flow`, `start_flow_run`, `finish_flow_run`, `fail_flow_run`, `set_flow_run_tagline`, `record_decision_box_execution`, `record_artifact`, `validate_artifact`, `send_email`, `record_feedback`, `await_user_input`, `execute_snapshot_command`. Shape data in a formatting-only CODE step first and read `{{ <step>.output.* }}` from the action. Lifecycle: `references/observability.md`.

`schedule_flow` re-arms the published flow later (`at` or `delay`); it stops after ~100 generations, so "run every hour forever" is a cron trigger flow, not self-scheduling.

## Errors and idempotency

- A tool error naming a field or argument: fix the call. A `graphql` top-level error: auth or malformed query.
- A business-rule error (the payload's `errors`): surface it and stop.
- Transport failures: retry 3 times at 2s, 4s, 8s.
- Safe to repeat: `update_agent_documents`, `update_flow`, `set_supported_triggers`, `install_activepieces_piece`, `pin_best_iteration`, `pin_flow_iteration`, `finish_improvement_run` (on a run sent back to `RUNNING`). Creates a duplicate or errors: `create_decision_box`, `create_flow`, `create_trigger_flow`, `wire_decision_box`, `request_connection`, `start_improvement_run`, `start_decision_box_iteration`, `define_decision_box_metric`, `create_experiment`, `record_eval_dataset`.
