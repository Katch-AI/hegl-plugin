# AP Flow JSON Shape — annotated reference

Snapshot date: 2026-09-11 (AP 0.86.0, flow schema 22)
Sources: `activepieces/packages/server/api/test/integration/ce/flows/flow/flow-operations.test.ts`,
         `activepieces/packages/core/execution/src/lib/flows/` type definitions,
         Hegl's dashboard GraphQL mutations.

---

## Overview — operations on the flow endpoint

A flow is a tree of steps. You build it via `apply_activepieces_flow_operation(flow_id, type, request)` —
each call carries a `type` (operation name) and a `request` (the operation's payload). Every
`Body: { "type": …, "request": … }` below is passed as those two arguments.
The response to every operation is the full updated `PopulatedFlow` object.

**Recommended path: `IMPORT_FLOW`** — set the entire trigger + action tree in one call.
Hegl's own http_client uses this for greenfield builds. See the `IMPORT_FLOW` section
below.

Alternate path: build incrementally with `UPDATE_TRIGGER` + `ADD_ACTION` per step. Useful
when editing an existing flow; verbose for greenfield.

Typical build sequence (greenfield, using `IMPORT_FLOW`):

1. Hegl creates the AP flow: `create_flow` / `create_trigger_flow`, poll until `activepiecesFlowId`
   is set. There is no tool to create an AP flow yourself.
2. `apply_activepieces_flow_operation` with `IMPORT_FLOW` — set the full trigger + action tree.
3. `apply_activepieces_flow_operation` with `LOCK_AND_PUBLISH` — publish the draft with `status`
   `DISABLED` for a trigger flow, `ENABLED` for the candidate. **The candidate must be published
   before its webhook accepts inbound requests.**

---

## Step structure (fields common to trigger and actions)

```json
{
  "name": "step_1",
  "displayName": "Human-readable label",
  "type": "CODE",
  "valid": true,
  "skip": false,
  "lastUpdatedDate": "2026-09-11T00:00:00.000Z",
  "settings": { ... },
  "nextAction": { ... }
}
```

| Field | Notes |
|---|---|
| `lastUpdatedDate` | ISO-8601 string. **Required on every step in `IMPORT_FLOW`** (trigger, CODE, PIECE, LOOP_ON_ITEMS, ROUTER, and every nested loop body / router child) — missing it anywhere is `400 Invalid input` for the whole import. Omit it for `ADD_ACTION` / `UPDATE_ACTION` / `UPDATE_TRIGGER`; AP stamps it. |
| `name` | Machine name, must match `^[a-zA-Z_][a-zA-Z0-9_]*$` — letters, digits, underscores. **No hyphens.** Always `"trigger"` for the trigger; `"step_1"`, `"step_2"`, … for actions. AP returns a generic HTTP 400 on violations; the error message doesn't always make the constraint obvious. |
| `displayName` | Free-form label shown in the AP UI. |
| `type` | `"CODE"` / `"PIECE"` / `"LOOP_ON_ITEMS"` / `"ROUTER"` for actions; `"PIECE_TRIGGER"` or `"EMPTY"` for triggers. |
| `valid` | Whether AP considers the step fully configured. Set `true` to avoid editor warnings. |
| `skip` | `false` to run the step; `true` to skip it (treated as a no-op pass-through). |
| `settings` | Shape varies by `type` — see sections below. |
| `nextAction` | The next step object (nested). Omit or `null` for the last step. |

### CODE step `settings`

```json
{
  "sourceCode": {
    "code": "export const code = async (inputs) => { ... }",
    "packageJson": "{}"
  },
  "input": {
    "someKey": "static value or {{ step_name.output }}"
  },
  "errorHandlingOptions": {
    "continueOnFailure": { "value": false },
    "retryOnFailure": { "value": false }
  }
}
```

**Gotcha:** the field is `sourceCode.code`, NOT `sourceCode.body`. The code string is the
full TypeScript module — it must export a named function `code`. `packageJson` is a JSON
string (usually `"{}"`); add npm deps here only if they are needed (most AP CODE steps don't).

The `input` object is key-value pairs. Values can be:

- Static strings / numbers.
- AP template expressions, resolved at runtime. Since flow schema 22 a step variable is the
  step *record*, so every reference goes through `.output`: `{{ trigger.output.body.someField }}`,
  `{{ step_1.output.total }}`. The bare `{{ <step>.<field> }}` form resolves to an empty string
  with no error (`start_flow_run` then receives an empty `flowTriggerId`). The only other
  top-level key is `.error` (`{{ step_1.error.message }}`).

### PIECE_TRIGGER settings (schedule example)

```json
{
  "pieceName": "@activepieces/piece-schedule",
  "pieceVersion": "~0.1.17",
  "triggerName": "every_hour",
  "input": { "run_on_weekends": false },
  "propertySettings": {
    "run_on_weekends": { "type": "MANUAL" }
  }
}
```

### PIECE_TRIGGER settings (webhook — built-in `@activepieces/piece-webhook`)

A "webhook trigger" is just `FlowTriggerType.PIECE` configured with `@activepieces/piece-webhook`
(trigger name `catch_webhook`). Used by Hegl for inbound-email and other genuinely external
webhook sources only. **The candidate flow's root trigger is NOT this** — it's the Hegl piece's
`marcus_triggered` trigger, which HMAC-validates incoming calls against the agent's Hegl
connection. See the "Candidate flow example" section below for the candidate-flow trigger shape.

### PIECE action `settings`

PIECE actions look like the trigger settings above, with the analogous fields:

```json
{
  "pieceName": "@activepieces/piece-store",
  "pieceVersion": "~0.6.14",
  "actionName": "put",
  "input": {
    "key": "seen_postings",
    "value": "{{ JSON.stringify(step_3.output) }}",
    "store_scope": "COLLECTION"
  },
  "propertySettings": {
    "key": { "type": "MANUAL" },
    "value": { "type": "MANUAL" },
    "store_scope": { "type": "MANUAL" }
  }
}
```

- **`propertySettings` is structurally required by AP's zod schema** but its *content* is not validated. AP accepts `propertySettings: {}` and accepts spare keys. The safest mirror of what the AP UI emits is one entry per populated prop, each `{ "type": "MANUAL" }`. (`MANUAL` is AP's form-mode for "literal value entered as text"; other modes are for dropdowns / dynamic prop dependencies.)
- **`pieceVersion` should use a tilde prefix** like `~0.6.14` — this matches what the AP UI generates and is what the validator accepts as a semver range. Bare `0.6.14` also works empirically.
- **CODE actions have no `propertySettings` field** — their `settings` is `{ sourceCode, input, errorHandlingOptions }` only.

### DYNAMIC props — the value is an object, not a string

Some piece props are typed `DYNAMIC` (AP's `Property.DynamicProperties`). A DYNAMIC prop's value is an **object keyed by the inner property name** (`Record<innerPropName, value>`), never a bare string.

The canonical trap is the shared **Custom API Call** action's `url` prop (Salesforce, HubSpot, and other pieces that expose `custom_api_call`). `url` is a DYNAMIC prop whose single inner field is also named `url`, so the value must be nested:

```json
"input": {
  "url": { "url": "/services/data/v58.0/query?q=SELECT+Id+FROM+Lead" }
}
```

Passing a bare string (`"url": "/services/data/..."`) passes build-time validation but throws at **runtime**: the action reads `url['url']` (→ `undefined`) and calls `.startsWith(...)` on it — `Cannot read properties of undefined (reading 'startsWith')`. Whenever a prop's metadata (`get_activepieces_piece`) types it `DYNAMIC`, wrap the value as an object keyed by the inner prop name.

### LOOP_ON_ITEMS action `settings`

```json
{
  "items": "{{ step_3.output.html_sources }}",
  "propertySettings": {
    "items": { "type": "MANUAL" }
  }
}
```

- `items` accepts either a JSON-encoded array string (`"[\"a\", \"b\"]"`) or a template that resolves to an array (`"{{ step_3.output.things }}"`). The latter is what's typically wanted for pipeline steps.
- Inside the body, the current iteration is `{{ <loop_step_name>.output.item }}` and the index is `{{ <loop_step_name>.output.index }}`.
- After the loop, `{{ <loop_step_name>.output }}` is **not** a flat array of body return values — it is an object `{ item, index, iterations }`: `item` is the final iteration's item, `index` is the final (1-based) index, and `iterations` is a **0-indexed array with one entry per iteration**, each entry a map keyed by inner step name → that iteration's step-output record `{status, input, output?, errorMessage?}` (`output` is absent when the step failed; `errorMessage` is set instead). To read a specific iteration's inner-step output, index in: `{{ <loop_step_name>.output.iterations[<i>].<inner_step_name> }}`. `{{ <loop_step_name>.output }}` alone does **not** aggregate the per-iteration inner outputs into a single list — you must walk `iterations[]`.
- The body subtree attaches to the LOOP_ON_ITEMS node's `firstLoopAction` (set by `ADD_ACTION` with `stepLocationRelativeToParent: "INSIDE_LOOP"` — see `ADD_ACTION` below). Subsequent actions inside the loop chain via `.nextAction` off `firstLoopAction`.

### ROUTER action `settings`

```json
{
  "executionType": "EXECUTE_FIRST_MATCH",
  "branches": [
    {
      "branchName": "high-priority",
      "branchType": "CONDITION",
      "conditions": [[
        { "operator": "NUMBER_IS_GREATER_THAN", "firstValue": "{{ step_2.output.score }}", "secondValue": "5", "caseSensitive": false }
      ]]
    },
    {
      "branchName": "default",
      "branchType": "FALLBACK"
    }
  ]
}
```

- **`branchType` is required on every branch.** A condition branch is `"branchType": "CONDITION"` and carries a `conditions` array; the catch-all is `"branchType": "FALLBACK"` and carries **no `conditions` key** at all. AP's `RouterBranchesSchema` is a union of exactly these two shapes (`BranchExecutionType` = `CONDITION` | `FALLBACK`), so a branch with no `branchType`, or a FALLBACK branch that still carries `conditions`, is rejected. Put the FALLBACK branch **last**: with `executionType: "EXECUTE_FIRST_MATCH"` it fires only when no earlier CONDITION branch matched. (A bare `conditions: [[]]` with no `branchType` is **not** a valid catch-all — use FALLBACK.)
- `conditions` is `[[ Condition ]]` — **inner array is an AND group, outer array ORs the groups.** `[[A, B]]` = `A AND B`; `[[A], [B]]` = `A OR B`. So **"any of these values" is separate outer groups**: `[[A], [B], [C]]`. A single inner group testing one field against two different exact values (`[[A, B]]`, both `TEXT_EXACTLY_MATCHES` on the same field) is **unsatisfiable** — it can never match. (Verified against `evaluateConditions` in AP's `router-executor.ts`: ANDs within each inner group, ORs across groups.) Before relying on a router, write out its truth table.
- **Condition `operator` values (exact wire strings).** Two-value operators (need `firstValue` **and** `secondValue`; the text ones also accept `caseSensitive`): text — `TEXT_CONTAINS`, `TEXT_DOES_NOT_CONTAIN`, `TEXT_EXACTLY_MATCHES`, `TEXT_DOES_NOT_EXACTLY_MATCH`, `TEXT_START_WITH`, `TEXT_DOES_NOT_START_WITH`, `TEXT_ENDS_WITH`, `TEXT_DOES_NOT_END_WITH`, `LIST_CONTAINS`, `LIST_DOES_NOT_CONTAIN`; number — `NUMBER_IS_GREATER_THAN`, `NUMBER_IS_LESS_THAN`, `NUMBER_IS_EQUAL_TO`; date — `DATE_IS_BEFORE`, `DATE_IS_EQUAL`, `DATE_IS_AFTER`. Single-value operators (only `firstValue`, **no** `secondValue`): `EXISTS`, `DOES_NOT_EXIST`, `BOOLEAN_IS_TRUE`, `BOOLEAN_IS_FALSE`, `LIST_IS_EMPTY`, `LIST_IS_NOT_EMPTY`. **Gotchas:** there is **no bare `GREATER_THAN`** — the number comparison is `NUMBER_IS_GREATER_THAN`; and "starts with" is the singular **`TEXT_START_WITH`** on the wire (the schema key is `TEXT_STARTS_WITH`, but the value string drops the `S`). `EXISTS` / `DOES_NOT_EXIST` treat `null` / `undefined` / `''` as absent — the basis for the continueOnFailure failure-detection pattern (see "fail edges" below).
- `children[]` is a flat array on the ROUTER node, **index-aligned with `settings.branches`**. Each entry is a single action (which can chain via `.nextAction`) or `null` for branches with no body. Children are attached via `ADD_ACTION` with `stepLocationRelativeToParent: "INSIDE_BRANCH"` and `branchIndex: <0-based>` (see `ADD_ACTION` below).

---

## Trigger flow example (SCHEDULE trigger → the Hegl piece `trigger_flow` action)

A trigger flow fires on a schedule and calls Hegl's `triggerFlow` mutation — via the
Hegl piece's `trigger_flow` action — to record that the trigger fired and dispatch the
candidate flow.

**Step 1 — the flow.** Use the `activepiecesFlowId` from `get_trigger_flow` / `get_agent`.

**Step 2 — set the SCHEDULE trigger.** Body:

```json
{
  "type": "UPDATE_TRIGGER",
  "request": {
    "type": "PIECE_TRIGGER",
    "name": "trigger",
    "displayName": "Every Hour",
    "valid": true,
    "settings": {
      "pieceName": "@activepieces/piece-schedule",
      "pieceVersion": "~0.1.17",
      "triggerName": "every_hour",
      "input": { "run_on_weekends": false },
      "propertySettings": {
        "run_on_weekends": { "type": "MANUAL" }
      }
    }
  }
}
```

**Step 3 — add the Hegl piece `trigger_flow` action.** Body:

```json
{
  "type": "ADD_ACTION",
  "request": {
    "parentStep": "trigger",
    "action": {
      "type": "PIECE",
      "name": "step_1",
      "displayName": "Trigger the Hegl flow",
      "valid": true,
      "skip": false,
      "settings": {
        "pieceName": "@marcus-ai/piece-marcus",
        "pieceVersion": "~0.2.0",
        "actionName": "trigger_flow",
        "input": {
          "auth": "{{connections['<platform connection external id>']}}",
          "trigger": "every_hour"
        },
        "propertySettings": {
          "auth": { "type": "MANUAL" },
          "trigger": { "type": "MANUAL" }
        },
        "errorHandlingOptions": {
          "continueOnFailure": { "value": false },
          "retryOnFailure": { "value": false }
        }
      }
    }
  }
}
```

The action's `inputs` prop (optional JSON) forwards a payload verbatim to the candidate flow's
webhook body — wire it from the production trigger's output when the candidate needs event data
(e.g. `"inputs": { "messageId": "{{ trigger.output.body.message_id }}" }`). If the payload needs real
shaping, put a formatting-only CODE step between the trigger and this action and read
`{{ <format_step>.output }}`. Omit `flowId` — the override is rejected for the connection's
`flow_execution` scope; Hegl selects the published flow.

**Gotcha — env substitution in `input`:** when a step prop genuinely needs a literal value from
your environment (rare now that Hegl's auth + URL come from the connection), write the resolved
string into the request you pass to `apply_activepieces_flow_operation`. Do NOT put raw environment
variable syntax (`${VAR}`) into the AP `input` — AP does not expand shell variables. Pass the
real strings.

**Step 4 — publish.** Body: `{ "type": "LOCK_AND_PUBLISH", "request": { "status": "DISABLED" } }`
(`DISABLED`, not `ENABLED`: see `LOCK_AND_PUBLISH` below).

---

## Candidate flow example (the Hegl piece `marcus_triggered` trigger → start_flow_run → decision boxes → finish_flow_run)

The candidate flow's root trigger AND every lifecycle step (`start_flow_run`, decision-box recording, `finish_flow_run`, `fail_flow_run`, `record_artifact`, `send_email`) come from the **Hegl piece (`@marcus-ai/piece-marcus`)**, NOT hand-rolled CODE steps or the generic webhook piece. The piece is pre-installed and its connection is auto-provisioned per agent — see the `activepieces` skill's "The Hegl pieces" section. Every Hegl piece step and the trigger reference the connection in `settings.input.auth` as `"{{connections['<platform connection external id>']}}"`; the id is `findAgent(id:) { platformConnectionExternalId }` through `graphql`.

Hegl dispatches the candidate flow with a POST to its webhook, body:

```json
{
  "flow_trigger_id": "ft_abc123",
  "trigger": "every_hour",
  "inputs": { "run_on_weekends": false }
}
```

and an `X-Marcus-Signature: sha256=<hex>` header that the `marcus_triggered` trigger HMAC-verifies against the connection's `marcusWebhookSecret` prop before firing the flow. The signing is handled inside Hegl's `DispatchFlowTriggerJob` (and by `trigger_activepieces_webhook`); you never compute a signature yourself.

### Full candidate flow build sequence

**The flow.** Use the `activepiecesFlowId` from `get_agent` (after `create_flow`).

**Set the `marcus_triggered` trigger.** Body:

```json
{
  "type": "UPDATE_TRIGGER",
  "request": {
    "type": "PIECE_TRIGGER",
    "name": "trigger",
    "displayName": "Triggered by Hegl",
    "valid": true,
    "settings": {
      "pieceName": "@marcus-ai/piece-marcus",
      "pieceVersion": "~0.2.0",
      "triggerName": "marcus_triggered",
      "input": {
        "auth": "{{connections['<platform connection external id>']}}"
      },
      "propertySettings": {
        "auth": { "type": "MANUAL" }
      }
    }
  }
}
```

Once enabled, this flow accepts webhook POSTs. The trigger HMAC-verifies each call against the connection's `marcusWebhookSecret` — Hegl's `DispatchFlowTriggerJob` and `trigger_activepieces_webhook` sign every call; an unsigned POST (including one through `activepieces_request`) is rejected by the trigger (the flow does not fire and the trigger writes an error to AP's container logs). The (signed and accepted) webhook body is available in subsequent steps as `{{ trigger.output.body }}`.

**Add step_start — the Hegl piece `start_flow_run` action.** Body:

```json
{
  "type": "ADD_ACTION",
  "request": {
    "parentStep": "trigger",
    "action": {
      "type": "PIECE",
      "name": "step_start",
      "displayName": "Start flow run",
      "valid": true,
      "skip": false,
      "settings": {
        "pieceName": "@marcus-ai/piece-marcus",
        "pieceVersion": "~0.2.0",
        "actionName": "start_flow_run",
        "input": {
          "auth": "{{connections['<platform connection external id>']}}",
          "flowTriggerId": "{{ trigger.output.body.flow_trigger_id }}"
        },
        "propertySettings": {
          "auth": { "type": "MANUAL" },
          "flowTriggerId": { "type": "MANUAL" }
        },
        "errorHandlingOptions": {
          "continueOnFailure": { "value": false },
          "retryOnFailure": { "value": false }
        }
      }
    }
  }
}
```

The action returns `{ runId, flowRunId }`:

- `runId` is a UUID v4 the piece synthesizes internally and passes to `startFlowRun(activepiecesFlowRunId:)`. AP does NOT expose its own flow-run UUID to action/CODE steps (no `{{ run.id }}`, no `globalThis` injection, no env var); the piece preserves the synth approach. Downstream lifecycle steps wire `activepiecesFlowRunId: "{{ step_start.output.runId }}"`.
- `flowRunId` is the prefixed `fr-...` returned from Hegl's `startFlowRun` payload — use it for `record_artifact` and `send_email` props that take a prefixed flow-run id: `flowRunId: "{{ step_start.output.flowRunId }}"`.

`flow_trigger_id` (in the webhook body) is a different thing — the `FlowTrigger.id` (Hegl's prefixed id) the trigger flow caused — passed as `flowTriggerId` to the action.

**Add decision-box stub steps (one CODE step + one Hegl piece record step per decision box in the flow).**

Each decision box becomes **two consecutive steps**: (1) a CODE step that runs the (stub or real) pure function and returns its output; (2) the Hegl piece `record_decision_box_execution` action that posts telemetry to Hegl, reading `inputs` / `outputs` / `durationMs` off the CODE step's output. The CODE step is set `continueOnFailure: true` so the record step always runs — including on throw — and a downstream ROUTER routes the failure into `fail_flow_run` afterwards (see "fail edges" below).

Step 1 of the pair — the decision-box CODE step (the stub):

```json
{
  "type": "ADD_ACTION",
  "request": {
    "parentStep": "step_start",
    "action": {
      "type": "CODE",
      "name": "step_decide_classify_lead",
      "displayName": "decision: classify_lead",
      "valid": true,
      "skip": false,
      "settings": {
        "input": {
          "boxInputs": { "lead": "{{ trigger.output.body.inputs.lead }}" }
        },
        "sourceCode": {
          "packageJson": "{}",
          "code": "export const code = async (inputs) => {\n  const startTime = Date.now();\n  // === Decision box: classify_lead ===\n  // Expected output schema: { category: string, confidence: number }\n  // STUB — replace with real implementation; a downstream agent fills it in.\n  const outputs = { category: 'hot', confidence: 0.9 };\n  return { inputs: inputs.boxInputs, outputs, durationMs: Date.now() - startTime };\n}"
        },
        "errorHandlingOptions": {
          "continueOnFailure": { "value": true },
          "retryOnFailure": { "value": false }
        }
      }
    }
  }
}
```

Step 2 of the pair — the Hegl piece `record_decision_box_execution` action:

```json
{
  "type": "ADD_ACTION",
  "request": {
    "parentStep": "step_decide_classify_lead",
    "action": {
      "type": "PIECE",
      "name": "step_record_classify_lead",
      "displayName": "record: classify_lead",
      "valid": true,
      "skip": false,
      "settings": {
        "pieceName": "@marcus-ai/piece-marcus",
        "pieceVersion": "~0.2.0",
        "actionName": "record_decision_box_execution",
        "input": {
          "auth": "{{connections['<platform connection external id>']}}",
          "decisionBoxId": "db-<from create_decision_box>",
          "flowId": "flw-<from create_flow>",
          "activepiecesFlowRunId": "{{ step_start.output.runId }}",
          "inputs": "{{ step_decide_classify_lead.output.inputs }}",
          "outputs": "{{ step_decide_classify_lead.output.outputs }}",
          "durationMs": "{{ step_decide_classify_lead.output.durationMs }}"
        },
        "propertySettings": {
          "auth": { "type": "MANUAL" },
          "decisionBoxId": { "type": "MANUAL" },
          "flowId": { "type": "MANUAL" },
          "activepiecesFlowRunId": { "type": "MANUAL" },
          "inputs": { "type": "MANUAL" },
          "outputs": { "type": "MANUAL" },
          "durationMs": { "type": "MANUAL" }
        }
      }
    }
  }
}
```

The pairing is non-negotiable — a decision-box CODE step without its companion `record_decision_box_execution` step produces no telemetry, and the dashboard cannot show what the box decided. If the agent scaffolds a "bare" stub with no follow-up record step, the pairing has been forgotten. Add it.

**fail edges.** When the decision-box CODE step throws, `continueOnFailure: true` lets the flow proceed to the record step. To route the failure afterward, add a ROUTER — but **do not** branch on `{{ step_decide_classify_lead.output.status }} == "FAILED"`: a `continueOnFailure`'d step's status is not reliably exposed to the condition evaluator, so that branch may never fire. Instead branch on the **absence of a field the step produces only on success**. The decision-box CODE step returns `{ inputs, outputs, durationMs }`, so a `CONDITION` branch with `firstValue: "{{ step_decide_classify_lead.output.outputs }}"` and operator `DOES_NOT_EXIST` means the step threw → route to `fail_flow_run`; the `FALLBACK` branch continues to the next box. (For a piece step, test a field present in that action's sampled success output: `.output.status` on the http piece or Salesforce `run_query`, but `.output.id` on Salesforce `create_record` and `.output.success` on `update_record`, which return flat bodies. A field the action never emits fires the fail branch on every success.) Wire the `fail_flow_run` step's optional `errorMessage` / `errorType` / `stackTrace` props from `{{ step_decide_classify_lead.error.* }}` (AP's failure-output convention).

**Failure detection ≠ empty result.** A step that *fails* has its success-only field absent (`DOES_NOT_EXIST` fires). A step that *succeeds but finds nothing* — a Salesforce SOQL / HTTP query returning HTTP 200 with `totalSize: 0` and an empty `records` array — did **not** fail: its success field is present, just empty, so `DOES_NOT_EXIST` does not fire. To branch on "succeeded but empty", test the count or list explicitly (`NUMBER_IS_EQUAL_TO 0` on `totalSize`, or `LIST_IS_EMPTY` on the records), never a failure operator.

**Add last step — the Hegl piece `finish_flow_run` action (or `fail_flow_run` on the error edge).** Body:

```json
{
  "type": "ADD_ACTION",
  "request": {
    "parentStep": "step_record_classify_lead",
    "action": {
      "type": "PIECE",
      "name": "step_finish",
      "displayName": "Finish flow run",
      "valid": true,
      "skip": false,
      "settings": {
        "pieceName": "@marcus-ai/piece-marcus",
        "pieceVersion": "~0.2.0",
        "actionName": "finish_flow_run",
        "input": {
          "auth": "{{connections['<platform connection external id>']}}",
          "activepiecesFlowRunId": "{{ step_start.output.runId }}",
          "metadata": null
        },
        "propertySettings": {
          "auth": { "type": "MANUAL" },
          "activepiecesFlowRunId": { "type": "MANUAL" },
          "metadata": { "type": "MANUAL" }
        }
      }
    }
  }
}
```

For the `fail_flow_run` path, swap `actionName: "fail_flow_run"` and replace the `metadata` prop with `errorMessage` (a string, optional). Both actions take `activepiecesFlowRunId` matching the `runId` the `start_flow_run` action returned.

**Publish the candidate flow.** Body: `{ "type": "LOCK_AND_PUBLISH", "request": { "status": "ENABLED" } }`

After publishing, a signed webhook call (`trigger_flow` or `trigger_activepieces_webhook`) starts a new run.

---

## `execute_snapshot_command` step example

A sandbox step (`sandbox-environments.md`) goes anywhere a CODE step would. As a decision box it replaces the CODE-step half of the pair and still runs *before* `record_decision_box_execution`, which reads its output.

```json
{
  "type": "ADD_ACTION",
  "request": {
    "parentStep": "step_start",
    "action": {
      "type": "PIECE",
      "name": "step_decide_classify_lead",
      "displayName": "decision: classify_lead (sandbox)",
      "valid": true,
      "skip": false,
      "settings": {
        "pieceName": "@marcus-ai/piece-marcus",
        "pieceVersion": "~0.2.0",
        "actionName": "execute_snapshot_command",
        "input": {
          "auth": "{{connections['<platform connection external id>']}}",
          "snapshotId": "sbs-<from snapshotSandbox>",
          "command": "node classify_lead.js",
          "inputs": "{{ trigger.output.body.inputs.lead }}"
        },
        "propertySettings": {
          "auth": { "type": "MANUAL" },
          "snapshotId": { "type": "MANUAL" },
          "command": { "type": "MANUAL" },
          "inputs": { "type": "MANUAL" }
        },
        "errorHandlingOptions": {
          "continueOnFailure": { "value": true },
          "retryOnFailure": { "value": false }
        }
      }
    }
  }
}
```

- **`snapshotId` is the published snapshot's `sbs-…` id, never the build sandbox's `sbx-…` id.** Wiring the sandbox id in by mistake fails the mutation's lookup with `"Snapshot not found"`.
- **Leave the `Timeout (seconds)` prop unset for the server default (60s, capped at 300s) — do not wire an explicit `null`.** This is a pinned regression (`dashboard/spec/system/sandbox_execution_smoke_spec.rb`): the piece must *omit* `timeoutSeconds` from the GraphQL variables when the prop is empty, because graphql-ruby only applies its `default_value` to an *absent* argument, and the underlying operation rejects an explicit nil timeout outright. If you're hand-assembling `input` (rather than going through the AP UI, which already omits empty optional props), simply don't include a `timeoutSeconds` key at all when you want the default.
- The action throws on a non-zero exit (surfacing the combined output in the error), so `continueOnFailure: true` here plays the same role it does for a CODE-step decision box: it lets the flow proceed to the `record_decision_box_execution` step even when the box's implementation fails, so telemetry is still recorded. The same fail-edge ROUTER pattern documented in the candidate flow example above applies — branch on the absence of the step's success-only output (`outputJson`), not on a `status` check.
- The action's returned `outputJson` is what the box's `record_decision_box_execution` step should read as `outputs` — same wiring pattern as reading a CODE step's return value, just off a different upstream step name. **The action does not return `durationMs`** — it returns only `{ exitCode, output, outputJson }` (the piece TS deliberately drops the mutation's `durationMs` field before returning to the flow), so don't wire `record_decision_box_execution`'s `durationMs` prop to `{{ step_decide_classify_lead.output.durationMs }}` — that path is only for a CODE-step decision box, whose stub computes its own `Date.now()` delta and returns it. A sandbox-backed box can leave `durationMs` unset.
- **`command` must be the bare command — no `<`/`>` redirects.** The production wrapper already runs it as `cd ~ && ( <command> ) < /tmp/run/input.json > /tmp/run/output.json`. Adding your own redirect inside `command` wins over the outer one for that inner process, so it silently reads whatever stale sample file was left in the snapshot's home directory instead of the real production input — and the outer `/tmp/run/output.json` ends up empty, which surfaces downstream as a misleading JSON-parse error rather than the redirect mistake it actually is. See `sandbox-environments.md` → "The workflow" for the full rule, and its note on deleting the test `input.json`/`output.json` before snapshotting.

See `sandbox-environments.md` for the full build → install → write → test → snapshot workflow that produces the `sbs-…` id this step references.

---

## Operations API primer

Every operation is one call: `apply_activepieces_flow_operation(flow_id, type: "<OP>", request: { ... })`.
It returns the updated flow (`versionId`, `stepsValid`, the tree in `raw`).

### IMPORT_FLOW

Set the entire trigger + action tree in one call. Hegl's own http_client uses this for
greenfield builds — preferred over per-step `ADD_ACTION` sequences.

`schemaVersion` must be the value `get_activepieces_flow` returns in `schemaVersion`
(a string, `"22"` on AP 0.86), never `null`. AP migrates the submitted tree forward from the
version you send, so `null` re-runs every migration on an already-current tree and
`.output`-nested step references come back double-wrapped (`{{ step['output']['output'] }}`).

At schema 22 the tree must already be in its final form: **every step carries
`lastUpdatedDate`** and every reference is `.output`-nested (see "Step structure" and the CODE
step `input` notes above). Only an import at an older `schemaVersion` gets those stamped and
rewritten for you.

```json
{
  "type": "IMPORT_FLOW",
  "request": {
    "displayName": "Flow",
    "schemaVersion": "22",
    "notes": [],
    "trigger": {
      "type": "PIECE_TRIGGER",
      "name": "trigger",
      "displayName": "Webhook",
      "valid": true,
      "lastUpdatedDate": "2026-09-11T00:00:00.000Z",
      "settings": { ... },
      "nextAction": {
        "type": "CODE",
        "name": "step_1",
        "displayName": "First step",
        "valid": true,
        "skip": false,
        "lastUpdatedDate": "2026-09-11T00:00:00.000Z",
        "settings": { "input": { "body": "{{ trigger.output.body }}" }, "sourceCode": { ... } },
        "nextAction": { ... }
      }
    }
  }
}
```

`trigger` is the full step tree — the trigger object with chained `nextAction` references
forming the rest of the flow. After IMPORT_FLOW, follow up with `LOCK_AND_PUBLISH` to enable
the flow.

**IMPORT_FLOW success ≠ step validity.** A 200 from `IMPORT_FLOW` means the JSON parsed and
the tree was accepted — **not** that every step is fully configured. AP still marks individual
steps `valid: false` when their settings are incomplete (a router branch with a malformed
condition, a PIECE step missing a required prop). After IMPORT_FLOW, re-fetch the flow
(`get_activepieces_flow`; `stepsValid` is false when any step is) and find the `valid: false`
step before `LOCK_AND_PUBLISH` — a mis-wired step still publishes but fails or misbehaves at
runtime, and the smoke test won't necessarily surface it.

### UPDATE_TRIGGER

Replace the flow's trigger with a new one. Wipes any existing trigger settings.

```json
{
  "type": "UPDATE_TRIGGER",
  "request": {
    "type": "PIECE_TRIGGER",
    "name": "trigger",
    "displayName": "Every Hour",
    "valid": true,
    "settings": {
      "pieceName": "@activepieces/piece-schedule",
      "pieceVersion": "~0.1.17",
      "triggerName": "every_hour",
      "input": {},
      "propertySettings": {}
    }
  }
}
```

### ADD_ACTION

Append a new step after `parentStep`. Steps chain via `nextAction`; AP manages the linkage.

```json
{
  "type": "ADD_ACTION",
  "request": {
    "parentStep": "trigger",
    "action": {
      "type": "CODE",
      "name": "step_1",
      "displayName": "My Step",
      "valid": true,
      "skip": false,
      "settings": {
        "input": {},
        "sourceCode": {
          "code": "export const code = async (inputs) => { return true; }",
          "packageJson": "{}"
        }
      }
    }
  }
}
```

To insert between existing steps, use `parentStep: "step_N"` — AP inserts after that step
and re-links the chain automatically.

**PIECE-step `ADD_ACTION`s require a `propertySettings` block.** The CODE-step example above
has no `propertySettings`, but when the added `action` is a `PIECE` step its `settings` **must**
include one (AP's zod schema requires the field for PIECE steps; `{}` is structurally accepted,
but the faithful mirror is one `{ "type": "MANUAL" }` per populated input prop — see "PIECE
action settings" above). Omitting the field entirely on a PIECE step is rejected as
`400 Invalid input`.

#### Adding actions inside or after a LOOP_ON_ITEMS / ROUTER

`ADD_ACTION` accepts `stepLocationRelativeToParent` to disambiguate where the new step lands relative to a container parent:

- **Inside a loop:** `stepLocationRelativeToParent: "INSIDE_LOOP"` — attaches to the parent LOOP_ON_ITEMS node's `firstLoopAction`. Chains via `.nextAction` after that.
- **Inside a router branch:** `stepLocationRelativeToParent: "INSIDE_BRANCH"`, `branchIndex: <0-based>` — attaches to `children[branchIndex]`.
- **After a loop or router:** `stepLocationRelativeToParent: "AFTER"` — attaches to the container's `nextAction`. **Without this, AP throws `"Loop step parent undefined not found"`** (or the ROUTER analogue) when the parent is one of these container types.

For normal sequential under-the-trigger actions, `stepLocationRelativeToParent` can be omitted.

An unknown `parentStep` is not an error: AP answers 200 and adds nothing. Duplicate `name`s are accepted too (one `DELETE_ACTION` removes only the first). Check the returned `version.trigger` chain for the step.

### UPDATE_ACTION

Replace the settings of an existing step. You must supply all fields (not a partial patch).
The `name` field identifies which step to update.

**For nested steps (inside a LOOP's `firstLoopAction` subtree or a ROUTER's `children[]`)**, `UPDATE_ACTION` is keyed by `name` **only** — no `stepLocationRelativeToParent`, no parent reference, no path. AP resolves the action by walking the flow tree. This asymmetry with `ADD_ACTION` (which needs `stepLocationRelativeToParent`) is intentional: ADD needs to know where to insert; UPDATE just needs to find an existing step.

To safely update a single field on an existing action: `get_activepieces_flow`, locate the current action in `raw.version.trigger` (walking `nextAction`, `firstLoopAction`, and `children[]`), copy the full action body, mutate only the target field, then submit. Missing fields are silently nulled or rejected as `400 Invalid input`.

```json
{
  "type": "UPDATE_ACTION",
  "request": {
    "type": "CODE",
    "name": "step_1",
    "displayName": "My Updated Step",
    "valid": true,
    "skip": false,
    "settings": {
      "input": { "key": "new value" },
      "sourceCode": {
        "code": "export const code = async (inputs) => { return inputs.key; }",
        "packageJson": "{}"
      }
    }
  }
}
```

### DELETE_ACTION

Remove steps by name. AP re-links the chain around the deleted step.

```json
{
  "type": "DELETE_ACTION",
  "request": {
    "names": ["step_2"]
  }
}
```

**Verify cleanup by re-fetching the flow, not by HTTP status.** Every flow operation (including
`DELETE_ACTION`) returns the updated `PopulatedFlow` on a 200 — confirm the step is actually gone
by inspecting that returned tree (or a follow-up `get_activepieces_flow`) for the step `name`,
rather than trusting the status code alone. This is the check for scratch-flow sampling cleanup:
after deleting an `inv_<uuid>` step, re-fetch and confirm it is absent.

### MOVE_ACTION

Re-order a step within the chain. `newParentStep` is the step it will follow after the move.

```json
{
  "type": "MOVE_ACTION",
  "request": {
    "name": "step_3",
    "newParentStep": "trigger",
    "stepLocationRelativeToNewParent": "AFTER"
  }
}
```

### LOCK_AND_PUBLISH

Locks the draft as the published version, then applies `status` (default `ENABLED`).

```json
{
  "type": "LOCK_AND_PUBLISH",
  "request": { "status": "DISABLED" }
}
```

Trigger flows: `"DISABLED"` (Hegl enables it on publish; `ENABLED` makes the trigger fire
now, and every event fails with no published flow). The candidate flow: `"ENABLED"`.

Not atomic: if the trigger's `onEnable` throws you get 400 `TRIGGER_UPDATE_STATUS` (engine error in
`params.standardError`) with the version already locked and `status` still `DISABLED`. Fix the
trigger with `UPDATE_TRIGGER`, publish again, and confirm `status: "ENABLED"` on a GET.

### CHANGE_STATUS (enable / disable without republishing)

Toggle the flow without creating a new version. Useful for temporary disable/enable.

```json
{
  "type": "CHANGE_STATUS",
  "request": { "status": "ENABLED" }
}
```

`status` values: `"ENABLED"` or `"DISABLED"`.

---

## Naming conventions and gotchas

| Gotcha | Detail |
|---|---|
| `sourceCode.code` vs `body` | The field is always `code`, never `body`. |
| Step references are `.output`-nested | Schema 22: `{{ step_1.output.x }}`, `{{ trigger.output.body.x }}`. Bare `{{ <step>.<field> }}` resolves to an empty string, silently. `ADD_ACTION` / `UPDATE_*` never rewrite references; only `IMPORT_FLOW` at an older `schemaVersion` does. |
| `lastUpdatedDate` | Required on every step in `IMPORT_FLOW` at schema 22 (`400 Invalid input` otherwise). Omit for `ADD_ACTION` / `UPDATE_ACTION` / `UPDATE_TRIGGER`; AP stamps it. |
| Template syntax | `{{ ... }}` runs as **full JavaScript** inside AP's V8 isolate — `{{ JSON.stringify(step_2.output) }}` and `{{ Math.min(step_1.output.a, 10) }}` work. Step outputs are in scope as variables (e.g. `step_1`, `trigger`). **Type/escaping asymmetry:** when a value is *exactly one template* (`"{{ step_3.output }}"`) the resolved value keeps its **native type** (object stays object); when a template is *embedded* in surrounding text (`"pre {{ x }} post"`) the result is concatenated as a raw string with **no JSON escaping**. So never build a JSON body by templating leaves into a JSON-shaped string — pass the input as an object with templated leaf values. See `code-step-authoring.md`. |
| `input` values | Static values or `{{ }}` templates. The resolver evaluates each template against the upstream step outputs at runtime and injects the result into the `inputs` argument the CODE function receives. |
| Env vars in `input` | AP does NOT expand shell `$ENV_VAR` syntax, and `{{ env.X }}` is not a thing either. Pass resolved strings from the provisioning code. |
| Candidate flow must be published | An un-enabled flow returns 410 Gone on webhook POST. Always `LOCK_AND_PUBLISH` (or `CHANGE_STATUS ENABLED`) the candidate after building; trigger flows are published `DISABLED` and Hegl enables them on publish. |
| `valid: false` warning | AP marks a step `valid: false` if its config is incomplete. Functionally the step still runs; the flag only affects UI indicators. Set `valid: true` explicitly when building programmatically. |
| `packageJson: "{}"` | Must be a JSON **string**, not an object. AP parses it internally. npm deps go under a `dependencies` key — `"{\"dependencies\": {\"cheerio\": \"1.0.0\"}}"`; a bare `"{\"cheerio\": \"1.0.0\"}"` installs nothing (compile-time `Could not resolve "cheerio"`). **But in Hegl prod (`SANDBOX_CODE_ONLY`) npm deps are stripped from CODE steps entirely** — declaring a dep does not make its import resolve. See `code-step-authoring.md` → "CODE-step sandbox capabilities". |
| `pieceVersion` pinning | Use the tilde form (`"~0.6.14"`) — matches what AP UI emits and is what the validator accepts as a semver range. Bare `"0.6.14"` also works. **AP normalizes it on write**, so a `GET`-back won't byte-match what you sent — see "Comparing flow versions" below. |
| Step `name` regex | `^[a-zA-Z_][a-zA-Z0-9_]*$` — letters, digits, underscores. **No hyphens.** Violations return generic HTTP 400. |
| `propertySettings` required for PIECE | Every PIECE action/trigger step must include a `propertySettings` object (CODE steps must NOT). AP's zod schema requires the field structurally; content is not validated, so `{}` is accepted. The safest mirror of UI-emitted JSON is one `{ "type": "MANUAL" }` per populated input prop. |
| AP flow-run UUID not exposed | The AP runtime does NOT expose its own flow-run id to CODE/PIECE steps (no `{{ run.id }}`, no `globalThis` injection, no env var). The Hegl piece's `start_flow_run` action synthesizes a UUID v4 internally and returns it as `runId`; every downstream lifecycle step wires `activepiecesFlowRunId: "{{ step_start.output.runId }}"`. (A trigger flow's `trigger_flow` piece action has no need for an AP flow-run UUID.) |
| `retryOnFailure: { value: true }` | AP re-runs a failed step up to 3 more times (4s, 8s, 16s). Set it on Hegl-piece steps so a transient Hegl error does not fail the run. |
| No top-level `await` | CODE bodies must wrap async work inside the exported `code` function. A top-level `await fetch(...)` throws at module-eval time. |
| No native try/catch across steps | Set `continueOnFailure: { value: true }` and branch in a downstream ROUTER on the **absence of a success-only output field** — a field the step emits only when it succeeds (a CODE step's `.output.outputs`; the http piece's `.output.status`; Salesforce `create_record` is flat, so `.output.id`) tested with the `DOES_NOT_EXIST` operator. Do **not** branch on `{{ step_N.output.status }} == "FAILED"` — a `continueOnFailure`'d step's status is not reliably exposed to the evaluator. See "fail edges" in the candidate-flow example. |

---

## Comparing flow versions (round-trip normalization)

Do **not** byte-compare a flow version you submitted against what `get_activepieces_flow` returns — AP normalizes several fields on write, so an exact-string comparison reports spurious differences:

- **`pieceVersion` is normalized.** AP rewrites the version range on every add / update / import. The exact direction is **AP-version-dependent**: some versions tilde-prefix the draft (`0.2.0` → `~0.2.0`) and re-pin to an exact version on publish; current AP strips the range to the exact resolved version (`~0.2.0` → `0.2.0`). Either way, what you sent won't come back verbatim — compare the resolved semver semantically, not as a string.
- **`propertySettings` is dropped from non-PIECE steps.** Only PIECE settings carry `propertySettings`; the CODE, ROUTER, and LOOP_ON_ITEMS settings schemas don't declare it, so AP silently strips any `propertySettings` you send on those step types (their Zod schemas drop unknown keys). It will not survive the round-trip.

When you need to confirm a step is configured as intended, compare the **specific fields you care about** (operator strings, `input` values, `sourceCode.code`) — not the whole serialized version blob.
