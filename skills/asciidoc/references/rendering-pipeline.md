# Hegl's rendering pipeline

How AsciiDoc artifacts move from the agent-written body to the user's screen, what each stage does to the markup, and the constraints those stages impose. 

## Pipeline

```
record_artifact action (flow runtime)
       │
       ▼
Asciidoctor.convert(safe: :secure, doctype: :article, standalone: false)
       │   produces an HTML fragment
       ▼
Artifacts::LoofahScrubber.scrub(html)
       │   strict allowlist, every disallowed tag removed (content survives),
       │   every disallowed attribute stripped
       ▼
sanitized HTML stored on the Artifact row
       │
       ▼
GET /admin/.../artifacts/:name/rendered
       │   served with X-Frame-Options: SAMEORIGIN,
       │   X-Content-Type-Options: nosniff, Referrer-Policy: no-referrer
       ▼
sandboxed <iframe sandbox="allow-same-origin"> in the dashboard
       │   the iframe is the security boundary
       ▼
dashboard user sees the rendered artifact
```

Source files (worktree-relative):

- Renderer: `dashboard/app/operations/artifacts/render.rb`
- Sanitizer: `dashboard/app/operations/artifacts/loofah_scrubber.rb`
- Validate / record: `dashboard/app/operations/artifacts/{validate,record}.rb`
- Iframe view component: `dashboard/app/components/artifacts/viewer.rb`
- Render controller: `dashboard/app/controllers/admin/artifacts/render_controller.rb`

## Asciidoctor invocation

```ruby
Asciidoctor.convert(
  body.to_s,
  safe: :secure,
  doctype: :article,
  standalone: false,
  logger: logger
)
```

What `:safe => :secure` blocks at the AsciiDoc level (before the HTML sanitizer runs):

- File `include::` directives — `include::/etc/passwd[]` resolves to nothing; the directive is not processed.
- URI `include::` directives — `include::https://attacker.example.com/leak[]` likewise blocked.
- Reading images from local file paths — `image::sunset.jpg[]` against a local-relative path resolves but the resulting `<img>` is later stripped by the sanitizer (see below). Asciidoctor itself does *not* try to read the file.
- Raw HTML passthrough blocks (`++++ … ++++`) — the block is processed but the contents are run through normal HTML rendering (then through the sanitizer, which strips anything not on the allowlist).
- The `pass:[…]` macro for arbitrary HTML — same: contents go through the sanitizer.
- Docinfo file loading — disabled.

Unaffected by `:safe => :secure`:

- Every AsciiDoc construct (sections, lists, tables, blocks, macros) that doesn't touch the filesystem or pass raw HTML.
- The full substitution chain (specialchars, quotes, attributes, replacements, macros, post-replacements) on user prose.
- The `:source-highlighter:` attribute — if set, the configured highlighter runs (Rouge, Pygments, etc.).

## Loofah allowlist (full)

The sanitizer is defined in `Artifacts::LoofahScrubber`. It walks the parsed HTML top-down. Every element that fails the allowlist is removed (its children promote into the parent — text content survives, the wrapper is gone). Every attribute that fails the per-tag allowlist is stripped.

### Allowed tags

```
h1 h2 h3 h4 h5 h6
p ul ol li dl dt dd
strong em b i u s del ins mark small sub sup
code pre kbd samp var
cite q abbr dfn time
blockquote
table thead tbody tfoot tr th td caption colgroup col
details summary
figure figcaption
div span a hr br
```

### Allowed attributes

| Scope | Attributes |
|---|---|
| Global (any allowed tag) | `class`, `id`, `title`, `lang`, `dir` |
| `<a>` | `href`, `target`, `rel` (with safety logic, see below) |
| `<time>` | `datetime` |
| `<td>` | `colspan`, `rowspan`, `headers` |
| `<th>` | `colspan`, `rowspan`, `scope`, `abbr`, `headers` |
| `<col>` | `span` |
| `<colgroup>` | `span` |
| `<ol>` | `start`, `type`, `reversed` |
| `<li>` | `value` |

Anything else is stripped — including `style="…"`, every event handler (`onclick`, `onerror`, etc.), every URL-bearing attribute on disallowed tags (`src`, `formaction`, `srcdoc`), and `cite` on `<blockquote>` / `<q>`.

### Anchor (`<a>`) safety logic

For every `<a>` in the output:

- If `href` matches **`\A#\S+\z`** (a fragment-only reference like `#section-id` or `#_footnote_1`), the anchor is kept as-is and any authored `target`/`rel` is stripped. Fragment navigation stays inside the artifact iframe. Used by internal cross-references, TOC entries, footnote markers, and bibliography references.
- If `href` matches **`\Ahttps?:\/\//i`** (case-insensitive), the anchor survives. `target` is force-set to `"_blank"` and `rel` to `"noopener noreferrer"` regardless of what the author wrote, defeating reverse-tabnabbing.
- Otherwise (absent href, or any other scheme — `javascript:`, `data:`, `file:`, `mailto:`, `ftp:`, relative paths), the anchor is replaced with a text node containing its inner text. Empty `<a id="…">` anchor targets — emitted by the `[[id]]` inline anchor — are unwrapped this way, losing the id. Block-level IDs survive because they're on the block wrapper, not on an inline anchor.

There is no http(s) domain allowlist; any well-formed external URL is accepted (and forced to open in a new tab).

### What gets stripped (categorically)

- Media elements: `<img>`, `<audio>`, `<video>`, `<iframe>`, `<embed>`, `<object>`, `<source>`, `<track>`, `<picture>`, `<svg>` (and SVG children).
- Interactive form elements: `<form>`, `<input>`, `<button>`, `<select>`, `<option>`, `<optgroup>`, `<textarea>`, `<label>`, `<fieldset>`, `<legend>`.
- Scripting and styling: `<script>`, `<style>`, `<link>`, `<meta>`, `<base>`.
- Inline `style="…"` on any tag.
- Every event handler attribute (`onclick`, `onload`, `onerror`, `onmouseover`, `onfocus`, `onblur`, `oninput`, …).

## The validate / record loop

A tool and a piece action control the build-time and runtime cycles. Both run the same renderer; they differ only in persistence.

### `validate_artifact` — build-time

```
validate_artifact(agent_id: "a-…", body: "= Title\n\nNOTE: …")
```

- No persistence.
- Returns:
  - `valid: true` iff Asciidoctor produced no `:ERROR`/`:FATAL`-severity log messages.
  - `validationErrors`: ERROR/FATAL Asciidoctor messages.
  - `warnings`: WARN/INFO Asciidoctor messages (unresolved cross-references show up here).
  - `renderedHtmlPreview`: the sanitized HTML the runtime would store.

Iterate the formatter against this in development. Treat warnings as "fix before shipping" — they usually indicate broken cross-references, stale anchors, or malformed table syntax.

### `record_artifact` — runtime

The Hegl piece's `record_artifact` action inside the flow (a flow-runtime action, not a tool).

- Props: `flowRunId` (from `start_flow_run`), `name`, `title`, `body`. Output: `{ artifactId }`.
- Persists or upserts on `(flowRunId, name)`.
- A body that fails validation makes the action throw, so the step fails loud.

The runtime steps downstream of the decision box:

1. Transform the decision box's JSON output into AsciiDoc via the deterministic formatter.
2. Run the `record_artifact` action.
3. A validation failure fails the step; fix the formatter.
