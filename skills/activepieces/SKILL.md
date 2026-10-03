---
name: activepieces
description: Use when building or editing any Activepieces flow — trigger flows, the candidate flow, piece steps, CODE steps, sandbox steps, routers, loops — when installing or referencing a piece, when sampling a piece action's output, when reading flow JSON shapes or calling the `activepieces_*` tools, or when debugging a runtime mismatch between a piece's declared schema and its actual output. Domain reference.
---

# Activepieces

Activepieces (AP) runs the flows. Hegl sits above it: it owns agents, decision boxes, and run records, and dispatches the candidate flow.

## Mental model

- **Project**: one per organization. The tools for flows, runs, pieces, connections, sampling and webhooks, and `activepieces_request`, take `agent_id` and run in that agent's organization project; the calls below omit it. Their `flow_id` is the AP flow id (`activepiecesFlowId` on `get_agent`), not `flw-…`.
- **Flow**: a versioned tree of steps with a root **trigger**. A flow must be `ENABLED` (`LOCK_AND_PUBLISH`) before it accepts calls; otherwise webhooks answer 410.
- **Steps**: `PIECE` (a piece action), `CODE` (TypeScript), `ROUTER`, `LOOP_ON_ITEMS`. Names match `^[a-zA-Z_][a-zA-Z0-9_]*$`; no hyphens.
- **Sandbox step**: the Hegl piece's `execute_snapshot_command` runs your command in a container you set up yourself (root; `pip`, `npm`, `apt`, any language). Use it wherever a CODE step's bare isolate is too small: a library, another language, an integration with an SDK but no piece. `references/sandbox-environments.md`.
- **Piece**: an integration package (`@activepieces/piece-slack`) with actions and triggers, pinned by exact version. `list_activepieces_pieces` is the authoritative list of installed versions; `references/pieces-catalog.md` is a snapshot for discovery, not for pinning. Most pieces also expose `custom_api_call`, which reuses the connection's auth against the vendor API and returns `{status, headers, body}`; reach for it when the piece lacks an action, before `calling-custom-apis`.
- **Connection**: a credential the user creates in the dashboard. A step references it as `"{{connections['<externalId>']}}"` (AP resolves by `externalId`, never by display name); read it back from `get_agent` (`connectionRequirements[].connection.externalId`) or `list_activepieces_connections(piece_name)`. `status: ACTIVE` only means no refresh has failed yet; on a runtime 401 the user must reauthorize it in the dashboard — never borrow another connection instead. Never write or upsert the managed Hegl connections, even to fix an outage.
- **Trigger flows** hand external events to Hegl (`trigger_flow` action). **The candidate flow** starts with the Hegl piece's `marcus_triggered` trigger, which verifies Hegl's signature, then `start_flow_run` → work → `finish_flow_run` / `fail_flow_run`.

## The Hegl pieces

`@marcus-ai/piece-marcus` is built into the image and its connection is provisioned per agent. Never install it, never `request_connection` for it, never put a token or URL in flow JSON. Every step that uses it, including the `marcus_triggered` trigger, takes `auth: "{{connections['<platform connection external id>']}}"`; the id is `platformConnectionExternalId` on `get_agent`. Same for `@marcus-ai/piece-marcus-llm`, the way to call an LLM from a flow, with `platformLlmConnectionExternalId` from `get_agent`. `@marcus-ai/piece-marcus-custom-api` calls HTTP APIs with no piece (`calling-custom-apis`). `@hegl-ai/piece-template` renders Liquid templates into HTML, Markdown, Slack, or plain text with escaping (`rendering-templates`).

Use the piece actions for every Hegl call. A CODE step cannot call Hegl anyway: in production it runs in a bare V8 isolate with no `fetch`, `require`, `console`, timers, or npm packages. CODE steps are for pure computation over `inputs`; `references/code-step-authoring.md` has the contract and gotchas.

## Discovering a piece's inputs and outputs

Use the tools, not the AP source tree, and do it in a subagent (the payloads are large).

- **Inputs**: `get_activepieces_piece(piece_name, version?, action?, trigger?)` → `actions[<name>].props` / `triggers[<name>].props`, with `type`, `required`, defaults; `action:` or `trigger:` returns just that one props schema, and the full piece can exceed the harness's tool-result limit, so pass the filter when you know the action. Never guess prop names. `auth` is one object or, on multi-auth pieces (GitHub, Slack), an array. A `DROPDOWN` or `DYNAMIC` prop with a refresher needs `get_activepieces_piece_options(piece_name, piece_version, action_or_trigger_name, property_name, flow_id, flow_version_id, input)`; wire the returned values, not the labels — Google Sheets `insert_row.values` is keyed by column letter (`A`, `B`…), and header-name keys silently append an empty row.
- **Outputs are undeclared; sample them.** On the scratch flow (`scratchActivepiecesFlowId` on `get_agent`, disabled, never fires): `apply_activepieces_flow_operation(flow_id, "ADD_ACTION", request)` a step named `inv_<uuid>` (underscore, so the weekly sweep can find it) with `auth: "{{connections['<externalId>']}}"` (sampling resolves by external id, not display name), then `sample_activepieces_step(flow_version_id, step_name)` with the draft's `versionId` from `get_activepieces_flow(flow_id)`. It is async: poll `get_activepieces_flow_run(flow_run_id)` to a terminal status and read `steps.inv_<uuid>.output`. `DELETE_ACTION` afterwards and re-fetch the flow to confirm. `get_activepieces_sample_data` reads only samples saved with `SAVE_SAMPLE_DATA`. Side effects fire, so sample read actions or a sandbox channel.
- Triggers have no sample endpoint. Document the expected payload from the piece's semantics and check it against the first real run.

## Pitfalls

- Every reference is `{{ <step>.output.<field> }}` (flow schema 22). A wrong path, including the bare `{{ <step>.<field> }}` form, resolves to an empty string with no error. Anchor every reference to a sampled output.
- `{{ }}` is full JavaScript. A whole-value template keeps the native type; a template embedded in text is spliced raw, so never build a JSON body by templating into a JSON-shaped string. Pass an object with templated leaves.
- No env-var expansion in `input`; pass real strings.
- Hegl creates every AP flow (`create_flow`, `create_trigger_flow`, the scratch flow); there is no tool to create one yourself.
- `IMPORT_FLOW` at `schemaVersion: "22"` rejects the whole tree with `400 Invalid input` unless every step carries `lastUpdatedDate`. A 200 does not mean every step is valid either; re-fetch with `get_activepieces_flow` and check `stepsValid`.
- `DYNAMIC` props take an object keyed by the inner prop name (`"url": { "url": "/path" }`, `"body": { "data": {…} }` plus `body_type`), not a string. On GET/HEAD omit `body` or set `body_type: "none"`.
- The http piece rebuilds the query string, so `%20` arrives as `+`; if the target tells them apart, send the URL in a POST body instead.
- After a publish, every step operation edits a new draft; runs keep using `publishedVersionId` until you `LOCK_AND_PUBLISH` again.
- A run is killed after 30 minutes (`TIMEOUT`) with no failure branch; cap long loops by elapsed time and carry the remainder to the next run.
- AP normalizes `pieceVersion` and drops `propertySettings` from non-piece steps on write; compare specific fields, not whole blobs.

## Debugging with the AP source

Only when the API was followed and the flow still misbehaves at runtime. Clone once with `git clone --depth 1 https://github.com/activepieces/activepieces.git ./activepieces` and have a subagent read `packages/pieces/{core,community}/<piece>/src/lib/{actions,triggers}/<name>.ts` (http, store, schedule, webhook are under `core/`), returning one answer with a file and line range. Never commit the checkout or paste it into documents.

## References

- `references/flow-json-shape.md` — step JSON, the trigger and candidate flow examples, operations (`IMPORT_FLOW`, `ADD_ACTION`, `LOCK_AND_PUBLISH`…), router and loop semantics, `execute_snapshot_command`.
- `references/code-step-authoring.md` — the CODE step contract, the isolate's limits, the decision-box pair.
- `references/api-endpoints.md` — the `activepieces_request` allowlist, the tool for each path, response shapes.
- `references/sandbox-environments.md` — sandbox steps: build → test → snapshot → wire.
- `references/pieces-catalog.md`, `references/piece-schedule.md`, `references/piece-slack.md`, `references/piece-store.md`, `references/piece-webhook.md`.

Still stuck: fetch the page at https://www.activepieces.com/docs/endpoints/<endpoint>, then probe the live API with a `GET` through `activepieces_request`.
