---
name: asciidoc
description: Use when writing an artifact body (the AsciiDoc documents recorded with the Hegl piece's `record_artifact` action and validated with `validate_artifact`), or when a rendered artifact looks wrong in the dashboard.
---

# AsciiDoc artifacts

An artifact is a short AsciiDoc document attached to a run and rendered in the dashboard. A formatter CODE step turns the decision box's JSON into AsciiDoc; the Hegl piece's `record_artifact` action stores it. Standard AsciiDoc works; this file lists what Hegl changes.

## Pipeline

Asciidoctor in secure mode, then a strict HTML allowlist, then a sandboxed iframe. Consequences:

- **Stripped** (text survives, tag goes): images, audio, video, iframes, forms and inputs, `script`, `style`, `svg`, inline `style="…"`. No `include::`, no raw HTML passthrough.
- **Kept**: headings, paragraphs, lists, inline formatting, `code`/`pre`, tables (with spans and alignment), `details`/`summary`, `blockquote`, `div`/`span` with `class`/`id`, links.
- **Links**: `http(s)://` opens in a new tab; `<<id>>` / `xref:id[]` scrolls inside the artifact. Any other scheme (`mailto:`, `file:`, relative) becomes plain text.

Full allowlist and the security details: `references/rendering-pipeline.md`.

## Loop

1. Write the formatter as a deterministic function (no LLM calls).
2. `validate_artifact(agent_id, body)` → `{valid, errors, warnings, renderedHtmlPreview}`. Fix warnings too; they are usually unresolved cross-references, malformed table cells, or unclosed delimiters.
3. Ship. At runtime `record_artifact` fails the step if the body does not validate.

## Conventions

- `[%collapsible]` example blocks for long or optional detail; they render as native `<details>`.
- AsciiDoc tables for structured comparison; `[source,LANG]` blocks for machine output.
- Admonitions (`NOTE:`, `WARNING:`…) sparingly.
- No images. Link to the asset instead.
- Roles (`[.role]`) instead of inline styles.
