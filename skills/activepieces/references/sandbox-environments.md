# Sandbox environments

A container you set up with shell commands (root; the base image has Python 3.11 and Node 20, install anything else), snapshot, and run from the flow with the Hegl piece's `execute_snapshot_command` action. Not only for decision boxes.

| Thing | Id | What it is |
|---|---|---|
| Build sandbox | `sbx-…` | a long-lived container you install into and test in; stops after 30 idle minutes, wakes on the next call |
| Snapshot | `sbs-…` | an immutable image published from a build sandbox; what the flow runs |
| Execution sandbox | none | a throwaway container spawned per snapshot run (the flow step or the `execute_snapshot_command` tool) |

## Workflow

1. `create_sandbox(agent_id, name, description)`.
2. `run_sandbox_command(sandbox_id, command, cwd?, timeout_seconds?)` to install dependencies. Each call is recorded in the sandbox's history (`get_sandbox`), the environment's build log.
3. `write_sandbox_files(sandbox_id, files: [{path, content}])`, paths relative to the home directory. Keep the source of truth in your workspace.
4. `execute_sandbox_command(sandbox_id, command, inputs, timeout_seconds?)`: a dry run of the exact production protocol. Pass the bare command, no redirects.
5. `snapshot_sandbox(sandbox_id, name, description)` once the winner is ready, not per iteration; snapshots are immutable.
6. Wire the Hegl piece's `execute_snapshot_command` action with `snapshotId: "sbs-…"` (never the `sbx-…` id), the same bare command, and `inputs`. Leave the timeout prop unset for the default. JSON: `flow-json-shape.md`.
7. `delete_sandbox(id)` after publishing to stop billing; the snapshot outlives it (`get_sandbox_snapshot`, or `findAgent(id:) { sandboxSnapshots { nodes { id name status } } }` through `graphql`).

## Credentials in a sandbox step

`inputs` is resolved like any other prop, so a connection field reaches the
command on stdin. The connection does not have to belong to the Hegl piece —
AP looks connections up by externalId alone:

```json
"inputs": { "password": "{{connections['<externalId>'].password}}" }
```

Never echo a credential: `output` is combined stdout+stderr and travels into the
AP flow-run log on every run.

## The command contract

Production runs `cd ~ && ( <command> ) < /tmp/run/input.json > /tmp/run/output.json`. The command reads JSON on stdin, writes JSON to stdout, exits non-zero on failure. On exit 0 the output must parse or the step fails. Adding your own `<`/`>` redirects hijacks the real input and output and surfaces as a misleading JSON-parse error.

The result is `{exitCode, output, outputJson, durationMs}`: `output` is combined stdout+stderr truncated at 10KiB (diagnostics only), `outputJson` is never truncated and is `null` on non-zero exit. The piece action drops `durationMs`, so leave that prop unset on the box's record step.

Timeouts default to 60s and cap at 300s. The `execute_snapshot_command(snapshot_id, command, inputs, timeout_seconds?)` tool runs a snapshot the same way, so smoke-test it before wiring.
