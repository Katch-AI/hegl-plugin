---
name: building-the-automation
description: Use when asked to build the user's automation and no candidate flow exists yet. Covers learning the job, the design decisions a flow needs, the plan documents, the build order, and the smoke test. Hands off to implementing-decision-boxes.
---

# Building the automation

Load `platform-api` and `activepieces` alongside this skill.

## What you are building

- **Trigger flows**, one per event source (a schedule, a Salesforce event, a Gmail label, inbound email). Each is an AP flow: the production trigger, then the Hegl piece's `trigger_flow` action. Piece triggers that poll (most non-webhook ones) run every 5 minutes, so a run appears up to 5 minutes after the event; tell the user.
- **The candidate flow**, one AP flow that does the job for one run: `marcus_triggered` trigger → `start_flow_run` → the work → `finish_flow_run` (or `fail_flow_run` on the error edge). Only Hegl can fire it; it checks a signature.
- **Decision boxes**: the judgment calls inside the run. Each is a CODE step (returning `{ inputs, outputs, durationMs }`) or a sandbox step, followed by `record_decision_box_execution`. They start as stubs returning fixed output; `implementing-decision-boxes` makes them real.
- **Human input pauses** for judgments only the user can make (approve a draft, pick between candidates). `await_user_input` opens a form in the dashboard and resumes on submit. See `platform-api/references/human-input-pauses.md`.
- **Artifacts**: a short AsciiDoc document per run the user can open ("what happened and why"). Default to one per run.
- **Feedback**: how real outcomes get back to Hegl (`record_feedback`). See `platform-api/references/feedback.md`.
- **Email**: every agent has an inbox; it can send, receive as a trigger, and get replies classified as feedback for free. See `platform-api/references/email.md`.

## 1. Learn the job

Start from the agent's name and description (`get_agent`). Play back what you understood and ask about what is missing. You need to know:

- What starts the job, the steps, what comes out, and who does it today.
- How the process is documented today: a standard operating procedure, checklist, onboarding doc, training video, or recorded walkthrough. Ask for it when it likely exists; a link, pasted text, or a transcript saves many questions.
- Which systems hold the data, read or write, and where exactly (which inbox, table, channel).
- Where past examples of the job live. You will grade the agent against them.
- How the team finds out today when the job was done wrong (a corrected record, a reply, a complaint). That becomes the feedback source.

Propose an answer with each question; the user corrects a guess more easily than they fill a blank. Sample real data through a subagent if your harness has one (`fetching-data-via-pieces`) rather than asking the user to describe field shapes.

Write `spec.md` and push it (`update_agent_documents(requirements:)`). Plain language throughout; technical detail goes under a clearly labelled "Implementation detail" heading. When you ask the user to review it, open the agent's `dashboardUrl` (from `get_agent`) for them.

## 2. Decide what the flow needs

Settle these, in this order, and add them to `spec.md`:

1. **Integrations.** Map each system to a piece (`activepieces/references/pieces-catalog.md`). Plain HTTP API with no piece → `calling-custom-apis`. Composed text (email body, Slack message, Markdown) → `rendering-templates`. A client library or SDK but no piece → a sandbox step (`activepieces`). Nothing else works → write `missing-pieces/<name>.md` (operations, auth, docs link) and tell the user this part must be built first.
2. **Decision boxes.** Name (snake_case), intent, input schema, output schema (JSON Schema). **Schemas are immutable once created**, so get them right on paper first: ranges, enums, and required keys go in the output schema, and the cross-field invariants (totals add up, values appear in the source) are listed beside it for `implementing-decision-boxes` to enforce. Prefer a few well-bounded boxes. If the user, not the model, must decide, it is a pause, not a box.
3. **Grading per box.** Where the past examples are, roughly how many, and how they split across outcomes. Which mistake costs more, a false yes or a false no. That picks the primary metric (precision, recall, F1, or error size for numbers) and a target value. Explain the trade-off in the user's terms and record the metric under implementation detail.
4. **Feedback.** Never skip this: without feedback the agent cannot improve after launch. Propose a mechanism, your recommendation first and two or three alternatives from `platform-api/references/feedback.md`, each described in the user's terms ("I read the Outcome field you already fill in"). Prefer outcomes the team already records in their system (poll a CRM field). Replies to Hegl-sent email are classified automatically. Every source needs a way to tie the signal back to the run (a hidden run id on the record or message is best).
5. **Email.** Skip unless the job has email in it. If the agent sends, decide who receives (reply to sender, fixed list, a box's output, a looked-up field).
6. **Artifacts.** One run summary per run unless the user declines.

## 3. Plan

Write `plan.md` and push it (`update_agent_documents(flow_description:)`):

- **Trigger**: source, event, and a table of the fields downstream steps read.
- **One run, step by step**: a numbered plain-language walkthrough naming every box, pause, side effect, and what happens on failure.
- **Diagram**: a Mermaid flowchart with every box, branch, and the finish and fail ends. Follow the `mermaid` skill; a diagram that fails to parse shows as a code block, so check the rendered Flow description on the agent page after pushing.

Keep command-level detail (step JSON, prop names, sampled output shapes, stub bodies, the smoke-test payload) in a local `implementation.md`. Sample every piece output you will reference (`activepieces` → "Discovering a piece's I/O"); a wrong field name resolves to an empty string with no error.

## 4. Build

Work through the list in order:

1. `install_activepieces_piece` per piece, poll `get_activepieces_piece_install` until `ready`. Never for the Hegl pieces; they are built in.
2. `request_connection` per piece with auth (never for the Hegl pieces; LLM calls go through the Hegl LLM piece and need none). `request_config` for tenant settings such as a base URL; poll `get_config_requirement` for the values. Then open the requirement's `dashboardUrl` for the user, say in plain words what to connect, and poll `get_agent` until the requirement's `status` is `SATISFIED`. Its `connection.externalId` goes into every `auth` slot as `{{connections['<externalId>']}}`.
3. `create_decision_box` per box. Schemas lock here.
4. `create_trigger_flow` per event source, poll `get_trigger_flow` until its `activepiecesStatus` is `ready`, then fill its AP flow (`activepiecesFlowId`; production trigger + `trigger_flow`) with `apply_activepieces_flow_operation` and `LOCK_AND_PUBLISH` with `"status": "DISABLED"` (Hegl enables it on publish; `ENABLED` makes the trigger fire now, and every event fails with no published flow). For inbound email pass `trigger_key: "inbound_email"` and do not fill it; Hegl provisions the body.
5. `create_flow` for the candidate, poll `get_agent` until its `activepiecesStatus` is `ready`, then `apply_activepieces_flow_operation(type: IMPORT_FLOW)` the full tree into its AP flow (`activepiecesFlowId`; `activepieces/references/flow-json-shape.md`). Re-fetch with `get_activepieces_flow` and check no step is `valid: false`.
6. `wire_decision_box` per box with the CODE step's name as `external_id`.
7. `LOCK_AND_PUBLISH` the candidate. An unpublished flow answers 410.
8. `set_supported_triggers(flow_id, trigger_flow_ids)` with **every** trigger flow this version supports, in one call. Publishing enables exactly the listed trigger flows and disables all others. Every new candidate flow needs its own call; the list does not carry over from the previous version, and publishing without it silently switches the automation off.

Give every run a `tagline` (under 100 characters, derived from the trigger payload) on `start_flow_run` so runs are findable in a table.

## 5. Review the structure

The smoke test checks the happy path only. Before it, check each authored step:

- **Routers**: `conditions` is `[[AND], [AND]]`, outer array is OR. One inner group testing a field for two different exact values never fires. `FALLBACK` must be the real catch-all and be last. Failure edges branch on the success-only field being absent (`DOES_NOT_EXIST` on `{{ <step>.output.outputs }}`), never on `status == "FAILED"`. A branch does not end the run (execution resumes at the router's `nextAction`) and `fail_flow_run` does not stop AP (a later `finish_flow_run` overwrites it); to end a run early, throw in a CODE step. Inside a loop, count errors and fail once afterwards.
- **`piece-http` with `failureMode: continue_all`**: a non-2xx does not fail the step, but its output becomes `{response: {status, body}, request}` while 2xx stays `{status, headers, body}`. Normalise in the next CODE step (`const r = raw.response ?? raw`).
- **References**: every `{{ step.output.field }}` matches a sampled output or code you wrote. A loop's result is `{ item, index, iterations }`.
- **Telemetry**: `record_decision_box_execution` gets the full `inputs` and `outputs`. Never truncate them; evals depend on them.

## 6. Smoke test

Trigger through Hegl, never by POSTing to the AP webhook (that skips the `FlowTrigger` row and the signature, so nothing runs):

`trigger_flow(trigger: "smoke_test", flow_id: "flw-…", inputs: { … })` returns `flowTrigger.id`. Poll `graphql` `findFlowTrigger(id:) { dispatchedAt dispatchError flowRuns { id } }` every 2s for up to 30s until `dispatchedAt` is set or `dispatchError` is not null. Then `get_flow_run(id)` on the run from `flowRuns`: `status` is `finished`, one `decisionBoxExecutions` entry per box with `errorMessage: null` and the payload values in `inputs` (empty strings mean a wrong `{{ }}` path or stacked `['output']` wraps from a re-imported tree), every expected artifact present, `tagline` set.

| Symptom | Likely cause |
|---|---|
| `dispatchError` set | candidate not `ENABLED` (410), or AP unreachable |
| dispatched but no AP run | the trigger's `auth` is not the Hegl connection, so the signature check failed |
| dispatched, `flowRuns: []` | `start_flow_run` failed inside AP (usually `flowTriggerId` resolving to `""`); `list_activepieces_flow_runs` with the candidate's `activepiecesFlowId` and read `steps.<name>.errorMessage` with `get_activepieces_flow_run` |
| first step failed | wrong `auth` on `start_flow_run`, or the Hegl connection was never provisioned (`get_agent` shows `platformConnectionExternalId` null) |
| record step failed | wrong `decisionBoxId` or `flowId` |
| `record_artifact` failed | body failed AsciiDoc validation; fix the formatter |

On failure, say which step failed, the likely cause, and what the user needs to do, in plain words. Do not auto-retry.

## 7. Next

Load `implementing-decision-boxes` and start the improvement run.
