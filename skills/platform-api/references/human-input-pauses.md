# Human input pauses

A human input pause is a step in the candidate flow that pauses execution, opens a form in the user's dashboard, and resumes when the user submits — or when the pause is cancelled / expired out-of-band. Use one whenever the workflow needs a human decision, approval, correction, or answer that no AP integration can produce.

## When

A pause is for what only the user can decide: approve or correct an output before it goes out, pick between candidates the model cannot tell apart, supply a value no system holds, confirm a high-stakes action. If the model could plausibly decide from its inputs, it is a decision box. If the answer arrives after the run is over, it is feedback.

## Form DSL

The `formShape` input on the `await_user_input` step is a JSON document describing the form. It is **not JSON Schema** — it is a Hegl-specific DSL.

### Top-level shape

```jsonc
{
  "title":       "string?",                              // ≤ 200 chars
  "description": "string?",                              // ≤ 2000 chars; plain text
  "rows":        [ { "columns": [ <column> ] }, ... ],
  "buttons":     [ <button>, ... ]
}
```

### Columns

Each row contains one or more columns. Each column has a `span` (1–12, integer) and **exactly one** of `field`, `alert` or `markdown`. The sum of spans per row must be ≤ 12; columns stack vertically on narrow viewports.

```jsonc
// Field column:
{
  "span": 6,
  "field": {
    "type":        "<one of the types below>",
    "name":        "snake_case",                          // unique within form; regex \A[a-z][a-z0-9_]{0,63}\z
    "label":       "string",                              // required, ≤ 500 chars
    "helper":      "string?",                             // ≤ 1000 chars; plain text
    "placeholder": "string?",                             // ≤ 500 chars
    "default":     <typed value>,                         // matches field type; for option types, must be a declared option value
    "required":    false,
    "options":     [ {"value":"...","label":"..."} ],     // select | radio | checkbox-group ONLY; values free-form, see below
    "validations": {                                       // optional, per-type
      "minLength":      int,
      "maxLength":      int,
      "min":            number,
      "max":            number,
      "step":           number,
      "pattern":        "regex",                          // ≤ 200 chars
      "patternMessage": "string"                          // ≤ 200 chars
    }
  }
}

// Alert column (highlighted note shown between fields):
{
  "span": 6,
  "alert": {
    "variant": "info" | "warning" | "success" | "plain",
    "content": "string"                                   // non-blank, ≤ 2000 chars; CommonMark, rendered as markdown
  }
}

// Markdown column (standalone rich-text block, no alert chrome):
{
  "span": 12,
  "markdown": "## Before you approve\nCheck the **lease terms** below…"   // non-blank, ≤ 10000 chars; CommonMark
}
```

Option `value`s are **arbitrary strings**, echoed back verbatim in the resume envelope's `values` — non-blank, ≤ 500 chars, unique within the field. Natural language is encouraged (`{"value": "Credit Card", "label": "Credit Card"}`); `label` is what the user sees, `value` is what downstream steps read. The snake_case rule applies to `field.name` / `button.name` only (regex unchanged) — never to option values.

`options` is only legal on `select` / `radio` / `checkbox-group`. On those types a declared `default` must match a declared option value — a single value for `select` / `radio`, an array of values for `checkbox-group`.

Reserved `field.name` / `button.name` values rejected by the parser: `form_button`, `authenticity_token`, `_method`, `commit`, `source`.

`helper` and `description` are **plain text only** — no markdown, no HTML; Phlex escapes them. `markdown` columns and `alert.content` render as CommonMark, sanitized server-side (raw HTML in the source is stripped, never rendered).

### Supported field types

| Type | Renders as | Use |
|---|---|---|
| `text` | `<input type=text>` | single-line free text |
| `email` | `<input type=email>` | HTML5 email |
| `url` | `<input type=url>` | HTML5 URL |
| `tel` | `<input type=tel>` | phone number |
| `password` | `<input type=password>` | obscured single-line |
| `number` | `<input type=number>` | numeric (min/max/step) |
| `textarea` | `<textarea>` | multi-line |
| `select` | `<select>` | dropdown, single |
| `radio` | radio group | one-of-N |
| `checkbox` | `<input type=checkbox>` | single boolean |
| `checkbox-group` | multiple checkboxes | multi-select, value is array |
| `toggle` | daisyUI toggle | boolean, cosmetic variant of checkbox |
| `date` | `<input type=date>` | calendar date |
| `time` | `<input type=time>` | time of day |
| `datetime` | `<input type=datetime-local>` | date + time |
| `month` | `<input type=month>` | month picker |
| `week` | `<input type=week>` | week picker |
| `range` | `<input type=range>` | slider |
| `color` | `<input type=color>` | color picker |
| `rating` | daisyUI rating stars | 1–N stars |

### Optional selects

A `select` with no `default` renders a blank placeholder as the first option — labelled with the field's `placeholder`, or "Select…" when none. The semantics depend on `required`:

- **Optional** select left on the placeholder → the field is **absent** from the resume envelope's `values` (not `""`). Downstream checks for "no choice made" test for absence.
- **Required** select → the placeholder renders disabled, so the user must actively pick a real option.

A declared `default` suppresses the placeholder entirely — the form opens on the default and always submits a real option value.

### Buttons

```jsonc
{
  "name":  "snake_case",          // unique within form; same regex as field.name
  "label": "string",
  "role":  "primary" | "secondary" | "cancel"
}
```

- At least one button is required; at most one with `role: "primary"`.
- Cancel-role buttons get HTML `formnovalidate` (the browser skips required-field checks) and the server skips value validation when one is clicked.
- A cancel-role button press still produces `outcome: "submitted"`. Downstream branches on `button` to know which button was clicked. The only `outcome: "cancelled"` is out-of-band (admin force-cancel).

### Worked example — approve/correct an outreach draft

```jsonc
{
  "title": "Approve outreach draft",
  "description": "The agent drafted an outreach email. Approve as-is, edit and approve, or skip.",
  "rows": [
    { "columns": [
      { "span": 12, "field": {
          "type": "textarea", "name": "draft",
          "label": "Draft", "required": true,
          "helper": "Edit before sending if needed."
      }}
    ]},
    { "columns": [
      { "span": 12, "field": {
          "type": "text", "name": "reason",
          "label": "If you edited, why? (optional)",
          "placeholder": "Tone too formal; added SSO mention; etc."
      }}
    ]}
  ],
  "buttons": [
    { "name": "approve_unchanged", "label": "Approve & send",        "role": "primary"   },
    { "name": "approve_edited",    "label": "Approve edited & send", "role": "secondary" },
    { "name": "skip",              "label": "Skip this lead",        "role": "cancel"    }
  ]
}
```

### Prefill

The `prefill` step input is a flat `{ field_name: value }` map computed by upstream steps. At render time, prefill overrides each field's `default`. Field names not in prefill use their declared `default`; field names not declared in `formShape` are ignored. Use prefill to seed run-specific values (the upstream draft, the extracted candidate SKUs, etc.) — keep `default` for schema-level "always start on Friendly tone" type defaults.

## Validating the shape

`validate_form_shape(agent_id, form_shape)` runs a form shape through the parser without persisting anything — the build-time feedback loop for the DSL, mirroring `validate_artifact` for artifact bodies. Call it at scaffold time, before wiring the `await_user_input` step, so DSL mistakes surface immediately instead of as a runtime failure.

- Returns `{valid, validationErrors}`; `validationErrors` is empty when valid.
- Each error is a `"<path>: <message>"` string pointing into the document, e.g. `/rows/0/columns/1/field/options/2/value: duplicate option value 'Credit Card'`.
- The parser **accumulates**: every violation in the document comes back in one call, not just the first. Fix them all, re-validate, then wire the step.

## The AP step

`await_user_input` is an action on the Hegl piece (`@marcus-ai/piece-marcus`, pre-installed; auth via the auto-provisioned connection at `{{connections['<platform connection external id>']}}`). Add it as a normal `PIECE` step.

```jsonc
{
  "type": "ADD_ACTION",
  "request": {
    "parentStep": "<upstream step name>",
    "action": {
      "type": "PIECE",
      "name": "await_outreach_approval",                  // your step name; downstream refs use this
      "settings": {
        "pieceName": "@marcus-ai/piece-marcus",
        "actionName": "await_user_input",
        "input": {
          "auth":      "{{connections['<platform connection external id>']}}",
          "flowRunId": "{{ step_start.output.flowRunId }}",       // from start_flow_run
          "stepName":  "await_outreach_approval",          // human-readable; shown in dashboard
          "formShape": { /* the JSON DSL from above */ },
          "prefill":   { "draft": "{{ compose_draft.output.outputs.draft }}" }
        }
      }
    }
  }
}
```

`{{ step_start.output.flowRunId }}` is the prefixed `fr-...` returned by the Hegl piece's `start_flow_run` action earlier in the flow. The step has no other auth or config beyond the auto-provisioned Hegl connection.

The pause cap is set by `AP_PAUSED_FLOW_TIMEOUT_DAYS` (30 days on the AP side); Hegl expires reviews ~1 day before that to avoid AP firing its own timeout.

## The resume envelope

The step's output (what downstream `{{ <step>.output.* }}` references read) is the resume body:

| Terminal | Step output |
|---|---|
| User submitted (non-cancel-role button) | `{ "outcome": "submitted", "button": "<button.name>", "values": { ...field values... } }` |
| User submitted (cancel-role button) | `{ "outcome": "submitted", "button": "<button.name>", "values": {} }` |

An out-of-band cancel (admin / system) or sweeper expiry (≈ 29 days after
creation) does **not** resume the step — it force-cancels the whole AP run, so
downstream steps never execute and no envelope is produced. The only envelope a
downstream step can ever read is `outcome: "submitted"`.

Downstream access patterns:

- `{{ <pause_step>.output.button }}` — which button the user clicked. Branch here for in-form choices.
- `{{ <pause_step>.output.values.<field_name> }}` — individual answers.
- `{{ <pause_step>.output.outcome }}` — always `"submitted"` when a downstream step runs; nothing to branch on.

Convention: branch on `button` for user choices. Every button press (including cancel-role) is `outcome: "submitted"` — a cancel-role button still resumes the flow; only out-of-band cancel/expiry kills it.

## Approve / correct chains to feedback

When the pause asks the user to approve or correct an agent output, the user's correction is also feedback. Chain a `record_feedback` step after a ROUTER on `button`: when the user clicked an approve-with-edits-style button (`approve_edited` in the worked example above; other forms may use different button names), post `record_feedback` with `payload.original`, `payload.corrected`, and `payload.reason`; confidence `DIRECT` (human-driven, no AI judgement in the loop).

Full pattern: `feedback.md`.

## Introspection

`get_human_review(id)` reads a pending or completed pause (`hrv-…`) for debugging. Not needed for runtime flow logic — the step output is the source of truth for downstream steps. For batch lookups use `node(id:)` with a `HumanReview` inline fragment through `graphql`.
