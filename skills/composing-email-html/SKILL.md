---
name: composing-email-html
description: Use when authoring the htmlBody of any send_email step — during Execute when building flow steps that send email, and during Plan when sketching email content. Covers the fragment contract (Hegl wraps every email in a branded layout), what styling comes free, the palette, and copy-paste snippet patterns for stat rows, item cards, tables, callouts, and CTAs.
---

# Composing Email HTML

Every email an agent sends is wrapped server-side in a branded layout: blue
header band carrying Hegl's name, white card on a slate page
background, footer note. You compose only the **content fragment** that goes
inside the card.

## The contract

- `htmlBody` is a **fragment** — never a full `<html>` document. A full
  document bypasses the branded layout entirely; use that only when the user
  explicitly asks for a fully custom email they control end-to-end.
- Hegl CSS-inlines everything at send time, including any `<style>`
  block you put at the top of the fragment, then removes the block. Media
  queries and other non-inlinable CSS do not survive — no responsive tricks.
- Always provide `textBody` alongside `htmlBody`, carrying the same content
  in plain text.
- No webfonts (the layout sets the font stack), no external CSS or JS, no
  images unless the user supplied hosted assets with absolute URLs.
- Render the fragment with `@hegl-ai/piece-template` (`format: html`, see
  `rendering-templates`) rather than string-building it in a CODE step, so
  every value is escaped.

## What you get free (bare markup, no classes)

`p`, `h1`, `h2`, `h3`, `ul`/`ol`/`li`, `table`/`th`/`td`, `hr`, `strong`,
`em`, `a` are all styled by the layout — body text 14px slate, muted
uppercase table headers, hairline row borders, spaced list items. Prefer
bare markup; reach for classes only when a pattern below needs them.

Layout-provided classes: `p.eyebrow` (small caps blue kicker),
`p.meta` (muted small print), `.quote` (border-left quote block),
`a.btn` (primary button).

## Palette

Text `#1e293b` (strong) / `#334155` (body); muted `#64748b` / `#94a3b8`;
borders `#e2e8f0` (default) / `#f1f5f9` (hairline); neutral tint `#f8fafc`; primary blue `#2563eb`
(tints `#dbeafe`, `#eff6ff`); teal `#0d9488` (tints `#ccfbf1`, `#f0fdfa`);
warning `#d97706` on `#fffbeb`. Use nothing outside this set.

## Rules

- Flat: no gradients, no shadows; separate with 1px borders.
- 4px border radius on boxes; pill radius (999px) only on chips.
- Sentence case everywhere. No emoji. No exclamation marks.
- Blue sparingly: at most one `a.btn` per email; links carry the rest.
- Custom classes MUST be scoped under `.em-body` with the element name
  (e.g. `.em-body p.mail-item-title`) — unscoped classes lose the cascade
  to the layout's base rules and inherit wrong margins.

## Snippet patterns

Put one `<style>` block at the top of the fragment containing only the
rules for the patterns you actually use.

### Header (no classes needed beyond layout's)

```html
<p class="eyebrow">Job board monitor &middot; daily digest</p>
<h1>6 new postings, 2 boards unreachable</h1>
<p class="meta">Monday, August 10 &middot; 40 boards checked</p>
```

### Stat row

```html
<style>
  .em-body table.mail-stats { border-collapse:collapse; width:100%; margin:0 0 16px; }
  .em-body table.mail-stats td { border:1px solid #e2e8f0; padding:10px 12px; text-align:center; }
  .em-body div.mail-stat-n { font-size:22px; font-weight:700; color:#1e293b; line-height:1.2; }
  .em-body div.mail-stat-l { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; color:#64748b; }
</style>
<table class="mail-stats"><tr>
  <td><div class="mail-stat-n">6</div><div class="mail-stat-l">New postings</div></td>
  <td><div class="mail-stat-n">38</div><div class="mail-stat-l">Boards OK</div></td>
  <td><div class="mail-stat-n">2</div><div class="mail-stat-l">Unreachable</div></td>
</tr></table>
```

### Item cards (linked results)

```html
<style>
  .em-body div.mail-item { border:1px solid #e2e8f0; border-radius:4px; padding:10px 12px; margin:0 0 8px; }
  .em-body p.mail-item-title { font-size:14px; font-weight:600; margin:0 0 2px; }
  .em-body p.mail-item-meta { font-size:12px; color:#64748b; margin:0; }
  .em-body span.mail-chip { display:inline-block; font-size:10px; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; color:#2563eb; background:#dbeafe; padding:2px 8px; border-radius:999px; }
  .em-body span.mail-chip.teal { color:#0d9488; background:#ccfbf1; }
</style>
<div class="mail-item">
  <p class="mail-item-title"><a href="https://example.com/posting">Research associate, modern history</a> <span class="mail-chip teal">New</span></p>
  <p class="mail-item-meta">Example University &middot; deadline August 31</p>
</div>
```

### Plain list and data table (no classes)

```html
<ul>
  <li><strong>Uni Leipzig</strong> &mdash; <em>failed to load</em></li>
</ul>

<table>
  <tr><th>Board</th><th>Status</th><th>Postings</th></tr>
  <tr><td>FU Berlin</td><td>OK</td><td>3</td></tr>
</table>
```

### Callouts

```html
<style>
  .em-body div.mail-callout { border-left:3px solid #d97706; background:#fffbeb; border-radius:0 4px 4px 0; padding:10px 14px; font-size:13.5px; color:#334155; margin:0 0 16px; }
  .em-body div.mail-callout.info { border-left-color:#2563eb; background:#eff6ff; }
  .em-body div.mail-callout.success { border-left-color:#0d9488; background:#f0fdfa; }
</style>
<div class="mail-callout"><strong>Warning:</strong> all 40 job boards were unreachable today.</div>
<div class="mail-callout info">This is the first run &mdash; 516 open postings recorded as the baseline.</div>
<div class="mail-callout success">Backfill complete.</div>
```

### Call to action (layout's button)

```html
<p style="text-align:center; margin:20px 0 4px;"><a class="btn" href="https://app.example.com/...">Review postings</a></p>
<p class="meta" style="text-align:center;">Or reply to this email to tell the agent what to change.</p>
```

## Full example

A daily digest assembling header + callout + items + CTA:

```html
<style>
  .em-body div.mail-item { border:1px solid #e2e8f0; border-radius:4px; padding:10px 12px; margin:0 0 8px; }
  .em-body p.mail-item-title { font-size:14px; font-weight:600; margin:0 0 2px; }
  .em-body p.mail-item-meta { font-size:12px; color:#64748b; margin:0; }
  .em-body div.mail-callout { border-left:3px solid #d97706; background:#fffbeb; border-radius:0 4px 4px 0; padding:10px 14px; font-size:13.5px; color:#334155; margin:0 0 16px; }
</style>
<p class="eyebrow">Job board monitor &middot; daily digest</p>
<h1>2 new postings</h1>
<p class="meta">Monday, August 10 &middot; 40 boards checked</p>
<div class="mail-item">
  <p class="mail-item-title"><a href="https://example.com/1">Research associate, modern history</a></p>
  <p class="mail-item-meta">Example University &middot; deadline August 31</p>
</div>
<div class="mail-item">
  <p class="mail-item-title"><a href="https://example.com/2">Lecturer in public history</a></p>
  <p class="mail-item-meta">Another University &middot; deadline September 15</p>
</div>
<div class="mail-callout"><strong>Warning:</strong> Uni Leipzig failed to load today.</div>
<p style="text-align:center; margin:20px 0 4px;"><a class="btn" href="https://app.example.com/postings">Review postings</a></p>
<p class="meta" style="text-align:center;">Or reply to this email to tell the agent what to change.</p>
```
