# `@activepieces/piece-webhook`

Snapshot: piece-webhook v0.1.33. Verify against `pieces-catalog.md`; if drift is significant, re-read `./activepieces/packages/pieces/core/webhook/src/lib/triggers/catch-hook.ts`.

**Not used as the candidate flow's trigger.** Hegl candidate flows use the Hegl piece's `marcus_triggered` trigger (see `SKILL.md`'s "The Hegl pieces" section), which HMAC-validates dispatches against the agent's Hegl connection. `@activepieces/piece-webhook` survives for genuinely external webhook sources — inbound email being the main one — where there's no shared secret with the caller and the source is responsible for its own auth scheme.

## Identity

- **pieceName:** `@activepieces/piece-webhook`
- **pieceVersion:** `~0.1.33`
- **Connection required:** no — webhook has no AP-level auth (per-flow auth is configured inline as a prop, see below).
- **Surface:** triggers only, no actions.

## Triggers

| triggerName | Props | Notes |
|---|---|---|
| `catch_webhook` | `authType`, `authFields` | Generic webhook trigger. Used by Hegl only for inbound-email and any external-source flows. The candidate flow's root trigger is the Hegl piece's `marcus_triggered`, not this. |

### `catch_webhook` — minimal (no auth)

```json
{
  "type": "PIECE_TRIGGER",
  "name": "trigger",
  "displayName": "Webhook",
  "valid": true,
  "settings": {
    "pieceName": "@activepieces/piece-webhook",
    "pieceVersion": "~0.1.33",
    "triggerName": "catch_webhook",
    "input": {
      "authType": "none"
    },
    "propertySettings": {
      "authType": { "type": "MANUAL" }
    }
  }
}
```

`authType: "none"` is the right choice for the inbound-email path and other genuinely external sources where the caller cannot share a secret with Hegl. For candidate flows, use the Hegl piece's `marcus_triggered` trigger instead — `authType: "none"` on a candidate flow would leave anyone with the AP flow id able to fire it, which the HMAC trigger exists to prevent.

### `catch_webhook` — with HMAC auth

For webhooks called by an external system that signs requests:

```json
{
  "settings": {
    "pieceName": "@activepieces/piece-webhook",
    "pieceVersion": "~0.1.33",
    "triggerName": "catch_webhook",
    "input": {
      "authType": "hmac",
      "authFields": {
        "hmacHeaderName": "x-signature",
        "hmacSecret": "<shared-secret-string>",
        "hmacAlgorithm": "sha256",
        "hmacEncoding": "hex",
        "hmacSignaturePrefix": "sha256="
      }
    },
    "propertySettings": {
      "authType": { "type": "MANUAL" },
      "authFields": { "type": "MANUAL" }
    }
  }
}
```

`authType` accepts `"none"`, `"basic"`, `"header"`, `"hmac"`. `authFields` is `DynamicProperties` that refreshes when `authType` changes — pass the field set matching the selected auth type.

## Runtime payload

`{{ trigger.output.body }}` is the full POST body as parsed JSON (or `{}` for empty/non-JSON requests). Headers are available at `{{ trigger.output.headers }}`. Query string params at `{{ trigger.output.queryParams }}`. Hegl's `DispatchFlowTriggerJob` sends a body of the form `{ flow_trigger_id, trigger, inputs }` — `flow_trigger_id` is what step_1's `startFlowRun` mutation needs as `flowTriggerId`.

## URL appendages

- `<webhook_url>/sync` — synchronous mode. The webhook caller blocks until the flow returns a response (must include a "Return Response" action). Useful for request/response style integrations.
- `<webhook_url>/test` — fires the webhook in test mode (generates sample data without triggering the published flow).

## When to use

- Every candidate flow's trigger.
- Any agent flow that responds to an external POST (signed or unsigned).

## Source

`./activepieces/packages/pieces/core/webhook/src/lib/triggers/catch-hook.ts`.
