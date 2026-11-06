# Sandbox environments

A container built from your Dockerfile (root; any language), published as an image and run by the Hegl piece's `execute_image_command` action. Not only for decision boxes.

| Thing | Id | What it is |
|---|---|---|
| Build sandbox | `sbx-…` | built from a Dockerfile (default base Python 3.11 + Node 20); stops after 30 idle minutes, wakes on use |
| Image | `sbi-…` | the sandbox's Dockerfile, frozen; what the flow builds and runs |
| Execution sandbox | none | throwaway, built per run; ~3s warm, up to a minute cold |

Flows published before November 2026 run from snapshots (`sbs-…`, `execute_snapshot_command`); leave them alone.

## Workflow

1. `create_sandbox(agent_id, name, description, dockerfile?)`. `FROM` needs a pinned tag/digest (not `latest`/`lts`/`stable`); max 64 KiB. Packages: `RUN pip install x==1.2`. Files: `COPY <<'EOF' /root/x.py … EOF` heredocs; no `COPY`/`ADD` from the build context (URLs, `--from=` fine). `get_sandbox` returns the Dockerfile and images. Change it with `update_sandbox(id, dockerfile)`, which rebuilds the container (history kind `rebuild`).
2. `run_sandbox_command` and `write_sandbox_files` are for exploring: anything not in the Dockerfile is not in the image.
3. `execute_sandbox_command(sandbox_id, command, inputs, timeout_seconds?)` builds fresh from the Dockerfile: exactly what the flow runs. Bare command, no redirects.
4. `publish_sandbox_image(sandbox_id, name, description)` for the winner: instant, unlimited, immutable.
5. Wire the Hegl piece's `execute_image_command` action with `imageId: "sbi-…"` (never the `sbx-…` id), the same command and `inputs`; leave the timeout unset. JSON: `flow-json-shape.md`.
6. `delete_sandbox(id)` after publishing to stop billing; the image outlives it (`get_sandbox_image`, `delete_sandbox_image`).

## Credentials in a sandbox step

`inputs` is resolved like any other prop, so a connection field reaches the
command on stdin. Any connection works; AP looks connections up by externalId alone:

```json
"inputs": { "password": "{{connections.<externalId>.password}}" }
```

Never echo a credential: `output` lands in the AP flow-run log on every run.

## The command contract

Production runs `cd ~ && ( <command> ) < /tmp/run/input.json > /tmp/run/output.json`. The command reads JSON on stdin, writes JSON to stdout, exits non-zero on failure. On exit 0 the output must parse or the step fails. Adding your own `<`/`>` redirects hijacks the real input and output and surfaces as a misleading JSON-parse error.

The result is `{exitCode, output, outputJson, durationMs}`: `output` is combined stdout+stderr truncated at 10KiB (diagnostics only), `outputJson` is never truncated and is `null` on non-zero exit. The piece action drops `durationMs`; leave it unset on the box's record step.

Timeouts default to 60s and cap at 300s. Build plus command share a ~290s ceiling; a slow cold build eats the command's time. Smoke-test with the `execute_image_command(image_id, command, inputs, timeout_seconds?)` tool before wiring.
