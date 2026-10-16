---
name: fix-errors
description: Use when the user runs `/hegl:fix-errors` or asks why an agent's runs are failing, or about an incident.
---

# Fix errors

Pick the agent (`hegl` → "Picking the agent").

1. `search_error_incidents(agent_id, query: "")`: Hegl groups production failures by cause into incidents, unresolved first, often with a diagnosis (`get_error_incident`). Leave a `FIXING` one alone; Autopilot is on it.
2. `search_flow_runs(agent_id, query: "", status: FAILED)`. It covers the last 7 days; widen `since` if the user means older runs. No incident and no failed run: say so and stop.
3. For each distinct failure, read the run (`get_flow_run`), then the failing step and its error on the Activepieces run (`get_activepieces_flow_run`).
4. Tell the user, in plain words, what is breaking, how often and why.
5. Sort by cause:
   - **Only the user can fix it** (an expired connection, a missing setting): open the page for them (`linking-to-the-dashboard`), wait until it is fixed, then `retry_activepieces_flow_run` each failed run with `FROM_FAILED_STEP`.
   - **A defect in the flow**: never edit the published flow. Fix a candidate copy in an `IMPROVEMENT` run (`implementing-decision-boxes`), smoke-test it with an input that failed, and finish the run for the user to publish. A retry runs the old flow, so once they publish, send the failed inputs again with `trigger_flow`. That starts from step one and repeats every earlier write: say which, and ask first.
6. Once the fix is live in production, `mark_incident_fixed(id, note)` each `OPEN` or `NEEDS_HUMAN` incident it fixes. Hegl watches it: resolved after a day without the error, reopened if it returns. Publishing ends every watch, so mark after the publish. The note (cause, fix, where it lives) is shown to the user.

The agent already has an open improvement run for this failure? Continue that one.
