#!/usr/bin/env bash
# Refreshes skills/activepieces/references/pieces-catalog.md from an AP /v1/pieces endpoint.
# Usage: AP_PIECES_URL=... [AP_BEARER_TOKEN=...] ./bin/refresh-pieces-catalog.sh

set -euo pipefail

: "${AP_PIECES_URL:?AP_PIECES_URL must be set}"

REFS_DIR="skills/activepieces/references"
OUTPUT="$REFS_DIR/pieces-catalog.md"
TMP="$(mktemp)"
DETAIL_NAMES_TMP="$(mktemp)"
trap 'rm -f "$TMP" "$DETAIL_NAMES_TMP"' EXIT

AUTH_HEADER=()
if [[ -n "${AP_BEARER_TOKEN:-}" ]]; then
  AUTH_HEADER=(-H "Authorization: Bearer ${AP_BEARER_TOKEN}")
fi

curl -fsSL ${AUTH_HEADER[@]+"${AUTH_HEADER[@]}"} "$AP_PIECES_URL" > "$TMP"

PIECES_COUNT="$(jq 'length' "$TMP")"

# Detail files are piece-<bare-name>.md, where bare-name is the AP piece name minus
# "@activepieces/"; collect their basenames.
find "$REFS_DIR" -maxdepth 1 -name 'piece-*.md' \
  -exec basename {} .md \; | sort > "$DETAIL_NAMES_TMP"
DETAIL_COUNT="$(wc -l < "$DETAIL_NAMES_TMP" | tr -d ' ')"

# Warn about detail files that reference pieces not in the current catalog.
# Each detail-file basename should match a piece name minus the "@activepieces/" prefix.
CATALOG_BARE_NAMES="$(jq -r '.[].name' "$TMP" | sed 's|^@activepieces/||' | sort -u)"
ORPHANED="$(comm -23 "$DETAIL_NAMES_TMP" <(printf "%s\n" "$CATALOG_BARE_NAMES") || true)"
if [[ -n "$ORPHANED" ]]; then
  echo "WARNING: detail files for pieces not present in the catalog:" >&2
  printf "  %s.md\n" $ORPHANED >&2
  echo "  (Rename to match the current piece name or delete if upstream-removed.)" >&2
fi

{
  cat <<EOF
# AP pieces catalog

Source: <$AP_PIECES_URL>
Pieces: $PIECES_COUNT (plus 2 Hegl-internal pieces; see bottom of table)
Detail files: $DETAIL_COUNT (see \`piece-<name>.md\` files in this directory for trigger/action/prop reference per piece)

The \`detail\` column marks pieces with a per-piece file at \`piece-<piece-name>.md\` in this
directory — read it before scaffolding a step using that piece. Pieces without a detail file
haven't been deeply documented yet; check the piece source at \`./activepieces/packages/pieces/\`
(clone setup: \`SKILL.md\` → "Debugging with the AP source") and write a new detail file if the
build paid the cost, following the shape of an existing \`piece-*.md\`.

## Contents

- The catalog — alphabetical table of all AP pieces with name, version, action/trigger counts, and detail-file links.

## The catalog

The bulk of the file is one big alphabetical table — grep for the piece name. Columns:

- \`name\` — the NPM-style piece identifier (use this in flow JSON's \`pieceName\`)
- \`displayName\` — the human label AP shows in its UI
- \`version\` — current semver on Hegl (use this in \`pieceVersion\`; ranges/\`latest\` are rejected)
- \`actions\` — number of actions the piece exposes
- \`triggers\` — number of triggers the piece exposes
- \`detail\` — link to the per-piece \`piece-<name>.md\` if one exists in \`references/\`

| name | displayName | version | actions | triggers | detail |
| --- | --- | --- | --- | --- | --- |
EOF
  jq -r --rawfile detail_names "$DETAIL_NAMES_TMP" '
    ($detail_names | split("\n") | map(select(length > 0))) as $details |
    .[] |
    . as $piece |
    ($piece.name | sub("^@activepieces/"; "")) as $bare |
    ($details | index($bare)) as $has_detail |
    "| \($piece.name) | \($piece.displayName) | \($piece.version) | \($piece.actions | length) | \($piece.triggers | length) | \(if $has_detail then "[\($bare)](\($bare).md)" else "" end) |"
  ' "$TMP" | sort

  # These rows aren't served by the AP /pieces endpoint (baked into Hegl's AP image).
  cat <<'PLATFORM_ROW'
| @marcus-ai/piece-marcus | Marcus | (built-in) | — | — | Pre-installed in Hegl's AP image; never install via `install_activepieces_piece`. Connection auto-provisioned per agent at creation time — never `request_connection` for it. See the `activepieces` skill's "The Hegl pieces" section for the full action list. |
| @hegl-ai/piece-template | Template | (built-in) | 1 | 0 | Pre-installed in Hegl's AP image; never install via `install_activepieces_piece`. No connection. Renders Liquid templates with format escaping — see the `rendering-templates` skill. |
PLATFORM_ROW
} > "$OUTPUT"

echo "Wrote $PIECES_COUNT pieces to $OUTPUT ($DETAIL_COUNT with detail files)" >&2
