# `@activepieces/piece-store`

Snapshot: piece-store v0.6.14. Verify against `pieces-catalog.md`; if drift is significant, re-read `./activepieces/packages/pieces/core/store/src/lib/actions/`.

## Identity

- **pieceName:** `@activepieces/piece-store`
- **pieceVersion:** `~0.6.14`
- **Connection required:** **no** — internal per-project KV store, no AP connection needed.
- **Surface:** actions only, no triggers.

## Actions

| actionName | Props | Notes |
|---|---|---|
| `get` | `key`, `defaultValue` (optional), `store_scope` | Read by key. Returns `defaultValue` when key is missing — or `null` if it is omitted or `""` (AP drops empty optional text props). |
| `put` | `key`, `value`, `store_scope` | Write by key. Overwrites. |
| `append` | `key`, `value`, `store_scope` | Append to a stored string. |
| `add_to_list` | `key`, `value`, `store_scope` | Appends the elements of `value`, an ARRAY prop — a JSON string fails validation with `Expected array`; wrap a single item: `["{{ … }}"]`. |
| `remove_from_list` | `key`, `value`, `store_scope` | Remove an element from a stored array. |
| `remove_value` | `key`, `store_scope` | Delete a key. |

### `store_scope` values

The dropdown shows three labels — the **value** sent over the wire differs from the label:

| Label (UI) | Value (wire) | Meaning |
|---|---|---|
| Project | `COLLECTION` | Scoped to the AP project — survives across flows and runs in the same project. |
| Flow | `FLOW` | Scoped to one flow — different flows in the same project have separate keyspaces. |
| Run | `RUN` | Scoped to a single run — wiped when the run ends. Internally namespaces the key with a `run_<runId>/` prefix. |

**For Hegl agents persisting state across runs of the same flow** (e.g., a Job Hunter remembering postings it has already shown), use `COLLECTION` (Project scope).

### `put` — full shape

```json
{
  "type": "PIECE",
  "name": "step_15",
  "displayName": "Persist seen postings",
  "valid": true,
  "settings": {
    "pieceName": "@activepieces/piece-store",
    "pieceVersion": "~0.6.14",
    "actionName": "put",
    "input": {
      "key": "seen_postings",
      "value": "{{ JSON.stringify(step_3.output.combined) }}",
      "store_scope": "COLLECTION"
    },
    "propertySettings": {
      "key": { "type": "MANUAL" },
      "value": { "type": "MANUAL" },
      "store_scope": { "type": "MANUAL" }
    },
    "errorHandlingOptions": {
      "continueOnFailure": { "value": false },
      "retryOnFailure": { "value": false }
    }
  }
}
```

### `get` — full shape

```json
{
  "type": "PIECE",
  "name": "step_2",
  "displayName": "Load seen postings",
  "valid": true,
  "settings": {
    "pieceName": "@activepieces/piece-store",
    "pieceVersion": "~0.6.14",
    "actionName": "get",
    "input": {
      "key": "seen_postings",
      "defaultValue": "[]",
      "store_scope": "COLLECTION"
    },
    "propertySettings": {
      "key": { "type": "MANUAL" },
      "defaultValue": { "type": "MANUAL" },
      "store_scope": { "type": "MANUAL" }
    },
    "errorHandlingOptions": {
      "continueOnFailure": { "value": false },
      "retryOnFailure": { "value": false }
    }
  }
}
```

## Type gotcha — `value` is `SHORT_TEXT` (`put`, `append`, `remove_from_list`)

`value` is `Property.ShortText` (string), so to store arrays or objects, **JSON-stringify before passing**:

```
"value": "{{ JSON.stringify(step_3.output.combined) }}"
```

AP's `{{ }}` engine runs as full JavaScript in a V8 isolate — `JSON.stringify(...)` works inline. On read, the value comes back as the string that was written; `JSON.parse({{ step_2.output }})` in a downstream CODE step recovers the structure.

`key` is constrained to ≤ 128 chars by the piece's runtime validator (zod).

## When to use

- Per-agent persistent state across runs (e.g., "what have I already processed?").
- Lightweight counters, last-seen timestamps, dedup sets.
- Not for large objects or structured queries — it's a simple KV with size limits at the AP project level.

## Source

`./activepieces/packages/pieces/core/store/src/lib/actions/`.
