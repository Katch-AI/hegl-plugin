# `@activepieces/piece-slack`

Snapshot: piece-slack v0.17.9. Verify the version in `pieces-catalog.md`; props via `get_activepieces_piece(piece_name: "@activepieces/piece-slack", action: "<action name>")`.

## `send_channel_message` / `send_direct_message`

`text` is rendered as a section block **above** `blocks`, despite the prop description calling it a notification fallback. For a Block Kit card pass `blocks` only; one of the two is required.
