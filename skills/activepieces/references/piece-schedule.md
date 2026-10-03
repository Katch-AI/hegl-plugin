# `@activepieces/piece-schedule`

Snapshot: piece-schedule v0.1.17. Verify the version in `pieces-catalog.md`; if it has drifted significantly from this file, re-read the piece source at `./activepieces/packages/pieces/core/schedule/src/`.

## Identity

- **pieceName:** `@activepieces/piece-schedule`
- **pieceVersion:** `~0.1.17` (use the tilde-pinned form in flow JSON)
- **Connection required:** no — schedule has no auth.
- **Surface:** triggers only, no actions.

## Triggers

| triggerName | Props | Notes |
|---|---|---|
| `cron_expression` | `cronExpression`, `timezone` | Most flexible — accepts any standard cron expression. |
| `every_x_minutes` | `minutes` | Fails to enable on the deployed 0.1.22 (`isValidCron` TypeError); use `cron_expression` (`*/5 * * * *`) instead. |
| `every_hour` | `run_on_weekends`, `minute_of_the_hour`, `timezone` | Polls hourly. |
| `every_day` | `run_on_weekends`, `hour_of_the_day`, `timezone` | Once per day at a specified hour. |
| `every_week` | `day_of_the_week`, `hour_of_the_day`, `timezone` | Once per week. |
| `every_month` | `day_of_the_month`, `hour_of_the_day`, `timezone` | Once per month. |

### `cron_expression` — full shape

```json
{
  "type": "PIECE_TRIGGER",
  "name": "trigger",
  "displayName": "Every 15 minutes",
  "valid": true,
  "settings": {
    "pieceName": "@activepieces/piece-schedule",
    "pieceVersion": "~0.1.17",
    "triggerName": "cron_expression",
    "input": {
      "cronExpression": "*/15 * * * *",
      "timezone": "UTC"
    },
    "propertySettings": {
      "cronExpression": { "type": "MANUAL" },
      "timezone": { "type": "MANUAL" }
    }
  }
}
```

- `cronExpression` — `ShortText`, required. Standard cron syntax. Default `0/5 * * * *`.
- `timezone` — `StaticDropdown<string>`, required. Default `UTC`. The dropdown's options come from a large IANA-tz list — pass the canonical timezone name (`"UTC"`, `"America/New_York"`, etc.).
- `propertySettings` is structurally required by the AP zod schema. `{ "type": "MANUAL" }` per populated prop mirrors what the AP UI emits. `propertySettings: {}` is also accepted (content is not validated server-side), but the explicit form is what most agents should write.

### `every_hour` — quick reference (legacy example shape)

```json
{
  "settings": {
    "pieceName": "@activepieces/piece-schedule",
    "pieceVersion": "~0.1.17",
    "triggerName": "every_hour",
    "input": {
      "run_on_weekends": false,
      "minute_of_the_hour": 0,
      "timezone": "UTC"
    },
    "propertySettings": {
      "run_on_weekends": { "type": "MANUAL" },
      "minute_of_the_hour": { "type": "MANUAL" },
      "timezone": { "type": "MANUAL" }
    }
  }
}
```

## Runtime payload

Schedule triggers produce no data of substance — `{{ trigger.output.body }}` is an empty object on each firing. Downstream steps that need a timestamp should compute one in a CODE step rather than reading it off the trigger.

## When to use

- A trigger flow's "fire every N minutes" production trigger.
- Any deterministic time-based dispatch.

For event-driven triggers (an external system pings us), use `@activepieces/piece-webhook` instead — see `piece-webhook.md`.

## Source

`./activepieces/packages/pieces/core/schedule/src/lib/triggers/cron-expression.trigger.ts` (and sibling `every-*.trigger.ts` files).
