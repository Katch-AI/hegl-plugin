---
name: fetching-data-via-pieces
description: Use when you need records from an external system the organization has a connection for — pulling past examples for an eval set, checking what a connection returns, any ad-hoc read through a piece action (Salesforce, Gmail, JIRA, HubSpot…).
---

# Fetching data via pieces

Read records by running one piece action on the agent's scratch flow. Every call takes `agent_id`; the calls below omit it. Step JSON and run shapes: the `activepieces` skill.

## The loop

1. `get_agent` → `scratchActivepiecesFlowId`, the `flow_id` below. `get_activepieces_flow(flow_id)` → `versionId`, the draft you sample.
2. Build the step: `list_activepieces_connections(piece_name)` → the connection's `externalId`; `get_activepieces_piece(piece_name, action: "<action>")` → `version` and `actions[<action>].props` (never guess prop names); `get_activepieces_piece_options(…)` for a dropdown's values.
3. `apply_activepieces_flow_operation(flow_id, "ADD_ACTION", request)`: one `PIECE` step named `inv_<uuid>` with `parentStep: "trigger"`, the action's props in `settings.input` plus `auth: "{{connections['<externalId>']}}"`, and one `{"type": "MANUAL"}` `propertySettings` entry per input key. An unknown `parentStep` still answers 200; check the step is in the returned tree.
4. `sample_activepieces_step(flow_version_id, step_name)` → a run id. Poll `get_activepieces_flow_run(flow_run_id)` until `SUCCEEDED`, `FAILED`, `TIMEOUT` or `STOPPED`, then read `steps.inv_<uuid>.output` (`.errorMessage` on failure). An output over 512KB comes back as `{fileId, size, url}`: fetch the `url` directly.
5. `apply_activepieces_flow_operation(flow_id, "DELETE_ACTION", {"names": ["inv_<uuid>"]})`, also after a failure, and re-fetch the flow to confirm it is gone.

Side effects fire: sample read actions only (list, search, query, get). The scratch flow is one draft, so sample one step at a time, never from parallel subagents. Sampling runs are `TESTING` and never appear in `list_activepieces_flow_runs`.

Make the first sample a handful of rows: it confirms the connection, the account and the field names before you commit to a dataset shape. On a runtime 401 the user reauthorizes the connection in the dashboard.

## Pagination

One sample per page: `UPDATE_ACTION` the same step with its full action body (the call replaces the whole action) and the next offset, cursor or row window in `input`, sample, read, repeat. Stop on an empty page or once you have the count the eval set needs. Per-piece props and ceilings (Salesforce's 2 000-row `OFFSET`; Airtable and HubSpot return one page only): `references/pagination-patterns.md`. A labeled pull with an 80/20 split, a two-source join, and a connection check: `references/example-ingestions.md`.

## Keep the rows out of your context

Run the loop in a subagent if your harness has one: it writes each page's output to a local file and returns a summary (row count, fields, two or three examples). Otherwise keep each step's `input` tight (page size, field list) and write every output to a file as you go.

## Limits

Only pieces with a list, search, query or get action work. Labeling and joining happen in your own code over the saved files. If no piece action can read what you need, or the source has no labels and no join can derive them, tell the user.
