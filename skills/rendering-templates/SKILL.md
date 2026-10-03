---
name: rendering-templates
description: Use when a flow must compose human-readable text from data — an email body, a Slack message, a Markdown summary, a plain-text notice. NOT for building JSON or API payloads (pass objects through step outputs or a CODE step instead).
---

# Rendering templates

`@hegl-ai/piece-template`, action `render`, is built into Hegl's AP image. No connection, no install. Props: `template` (Liquid source), `data` (the variables object), `format` (`html`, `markdown`, `slack`, `text`). Output: `{ text }`.

## Delimiters

AP consumes every `{{ … }}` in a string prop before the piece runs, so output tags are `[[ … ]]`. Logic tags stay `{% … %}`.

```json
{
  "template": "<p>Hello [[ customer.name ]],</p>{% for o in orders %}<li>[[ o.id ]]: [[ o.total ]]</li>{% endfor %}",
  "data": "{{trigger.output.body}}",
  "format": "html"
}
```

Put everything the template needs into `data` and reference it with `[[ ]]`. Loops, filters, and escaping only work on values that arrive that way.

## Formats

Every `[[ ]]` value is escaped for the chosen format; a customer-supplied string can never inject markup. Escaping covers text and attribute values, not URL schemes.

- `html`: `& < > " '` become entities. Use for `htmlBody` fragments (see `composing-email-html`).
- `markdown`: formatting, link, heading, table, and HTML characters are backslash-escaped.
- `slack`: `& < >` become entities, Slack's rule for mrkdwn. Slack has no escape for `*`, `_`, `~`, `` ` ``, so those stay live inside values.
- `text`: no escaping.

Append `| raw` as the LAST filter to insert a value you know is already safe markup: `[[ snippet | raw ]]`. A `capture`d or `assign`ed string is escaped again when output; emit it with `| raw`.

## Failure behavior

The step fails, with line and column, on a syntax error, a variable not present in `data`, an unknown filter, or a template that runs too long. There is no partial output. Smoke-test a template once with `trigger_flow` before publishing.

## Not for JSON

Build payloads as objects: a `Property.Json` prop or a CODE step return. Render only the human-readable string, then reference the step's `text` inside the payload.
