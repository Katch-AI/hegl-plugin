# AP endpoints — the `activepieces_request` allowlist

`activepieces_request(method, path, query?, body?)` reaches exactly these paths (relative to `/api/v1`, no query string in `path`) in the organization's project; `projectId` is injected where AP needs it, and AP's own status and body come back even on a refusal. Every path also has a dedicated tool; prefer it.

| Endpoint | Tool |
|---|---|
| `GET /pieces` | `list_activepieces_pieces` |
| `GET /pieces/{name}`, `GET /pieces/{scope}/{name}` | `get_activepieces_piece(piece_name, version?)` (`action:` / `trigger:` narrow to one) |
| `POST /pieces/options` | `get_activepieces_piece_options` |
| `GET /app-connections` | `list_activepieces_connections(piece_name?)` |
| `GET /flows` | `list_activepieces_flows` |
| `GET /flows/{id}` | `get_activepieces_flow(flow_id)` |
| `POST /flows/{id}` | `apply_activepieces_flow_operation(flow_id, type, request)` |
| `GET /flow-runs` | `list_activepieces_flow_runs(flow_id?)` |
| `GET /flow-runs/{id}` | `get_activepieces_flow_run(flow_run_id)` |
| `POST /flow-runs/{id}/retry` | `retry_activepieces_flow_run(flow_run_id, strategy)` |
| `POST /sample-data/test-step` | `sample_activepieces_step(flow_version_id, step_name)` |
| `GET /sample-data` | `get_activepieces_sample_data(flow_id, flow_version_id, step_name, type)` |
| `POST /webhooks/{id}` | `trigger_activepieces_webhook(flow_id, body)` (signed); through `activepieces_request` the POST is unsigned |

Installing a piece is `install_activepieces_piece`; creating a flow is `create_flow` / `create_trigger_flow`. Connections are read-only: Hegl owns writes (`request_connection`; the user creates and reauthorizes them in the dashboard). List tools return one page (AP defaults to 10); pass `limit` and the previous page's `page.next` as `cursor`.

---

## Pieces

`list_activepieces_pieces`: `{name, displayName, version}` per installed piece, built-in and custom.

`get_activepieces_piece`: `{name, displayName, version, auth, triggers, actions}` with every prop schema. `version` is an exact semver; omit it for the latest installed.

`get_activepieces_piece_options`: resolves a dropdown or dependent prop whose options come from a `refreshers` closure (auth, another prop); needed only when the static `props` describe a refreshing dropdown. Put `auth` (`{{connections['<externalId>']}}`) and the refresher props in `input`; use the returned option `value` verbatim.

## Connections

`list_activepieces_connections`: `{id, externalId, displayName, pieceName, status}` per connection.

## Flows

`get_activepieces_flow`: `{id, displayName, status, publishedVersionId, versionId, schemaVersion, stepsValid, raw}`; the step tree is `raw.version.trigger`.

`apply_activepieces_flow_operation` types: `IMPORT_FLOW` (whole tree; preferred for greenfield), `UPDATE_TRIGGER`, `ADD_ACTION`, `UPDATE_ACTION`, `DELETE_ACTION`, `MOVE_ACTION`, `CHANGE_STATUS` (`{status: "ENABLED" | "DISABLED"}` without republishing), `LOCK_AND_PUBLISH` (publish the draft and apply a status), `SAVE_SAMPLE_DATA`. Request shapes: `flow-json-shape.md`. There is no enable/disable endpoint; use `LOCK_AND_PUBLISH` or `CHANGE_STATUS`.

## Flow runs

`get_activepieces_flow_run`: `{id, status, steps, failedStepMessage, raw}`. `steps` is an object **keyed by step name** (`steps.<stepName>.output` / `.errorMessage` / `.status`), not an array. `status`: `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `TIMEOUT`, `PAUSED`, `STOPPED`; poll until `SUCCEEDED` / `FAILED` / `TIMEOUT` / `STOPPED`. A step output over 512KB serialised is stored as `{fileId, size, url}`: fetch the signed `url` directly to read it (its `/step-files` path is not on the `activepieces_request` allowlist); downstream `{{ step.output.x }}` refs still resolve. Step outputs are purged after 30 days (`steps: {}`).

`list_activepieces_flow_runs`: newest first, PRODUCTION runs only; a sampling run is TESTING and is read by id.

`retry_activepieces_flow_run`: `ON_LATEST_VERSION` starts again from step 1, so a late failure repeats every earlier write; prefer `FROM_FAILED_STEP`, or fix and republish.

## Webhooks

`trigger_activepieces_webhook`: body is whatever the flow's webhook trigger expects. The flow must be `ENABLED`, otherwise AP answers 410 Gone. No run id comes back (the `x-webhook-id` header is a request id); find the run with `list_activepieces_flow_runs`.

## Sample data — piece I/O discovery

`sample_activepieces_step` runs one step of a flow version against the live service. **Asynchronous**: it returns a run in `QUEUED`, not the output. Poll `get_activepieces_flow_run` to a terminal status and read `steps.<stepName>.output` (errors at `steps.<stepName>.errorMessage`).

- **Target the scratch flow** (`scratchActivepiecesFlowId` on `get_agent`). It is pre-provisioned per org, DISABLED, with a never-firing cron placeholder; sampling works on its draft regardless of status. Name the step `inv_<uuid>` — an underscore, **not** a hyphen (the step-name regex `^[a-zA-Z_][a-zA-Z0-9_]*$` forbids `-`) — so the weekly sweep can remove stragglers. `DELETE_ACTION` after sampling and re-fetch the flow to confirm the step is gone.
- Requires a satisfied connection for the piece. Reference it by **`externalId`** (`{{connections['<externalId>']}}`): AP resolves connections only by externalId, everywhere.
- Side effects fire. `send_message` posts a real message; `send_email` sends a real email. Prefer side-effect-free actions, or target a sandbox channel/inbox.
- On failure, the run's top-level failure summary is capped (~700 chars) and step `input` fields are truncated (~2 KB each); read `steps.<name>.errorMessage` for the fuller error.
- The output is **not** saved as sample data; it lives only on the run.

`get_activepieces_sample_data` reads sample data saved by a `SAVE_SAMPLE_DATA` operation (`type`: `OUTPUT` for the action's return value, `INPUT` for props resolved at run time); `{}` when none was saved. Sampling output never appears here.

## Error semantics

| Status | Meaning |
|---|---|
| 404 | Resource not found. |
| 410 | Webhook called on a disabled flow. |
