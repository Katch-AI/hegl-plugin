---
name: fix-errors
description: Use when the user runs `/hegl:fix-errors` or asks why an agent's runs are failing.
---

# Fix errors

Pick the agent (`hegl` → "Picking the agent").

1. `search_flow_runs(agent_id, query: "", status: FAILED)`. It covers the last 7 days; widen `since` if the user means older runs. None: say so and stop.
2. For each distinct failure, read the run (`get_flow_run`), then the failing step and its error on the Activepieces run (`get_activepieces_flow_run`).
3. Tell the user, in plain words, what is breaking, how often and why.
4. Sort by cause:
   - **Only the user can fix it** (an expired connection, a missing setting): open the page for them (`linking-to-the-dashboard`), wait until it is fixed, then `retry_activepieces_flow_run` each failed run with `FROM_FAILED_STEP`.
   - **A defect in the flow**: never edit the published flow. Fix a candidate copy in an `IMPROVEMENT` run (`implementing-decision-boxes`), smoke-test it with an input that failed, and finish the run for the user to publish. A retry runs the old flow, so once they publish, send the failed inputs again with `trigger_flow`. That starts from step one and repeats every earlier write: say which, and ask first.

The agent already has an open improvement run for this failure? Continue that one.
