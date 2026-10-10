---
name: feedback
description: Use when the user runs `/hegl:feedback` or asks to act on the feedback an agent has received.
---

# Feedback

Pick the agent (`hegl` → "Picking the agent").

1. `search_feedbacks(agent_id, query: "", sentiment: DOWN)`. It covers the last 30 days; widen `since` if that is thin. None: say so and stop.
2. Group the items by decision box. An item with no box still counts: read its run when it has one (`get_flow_run`) and work out which judgment call it is about.
3. Tell the user, in plain words, what people complain about and how often, worst first.
4. Take the box with the most complaints, or the one the user picks, and improve it in an `IMPROVEMENT` run per `implementing-decision-boxes`. Those feedback items go into the eval set.

The agent already has an open improvement run? Continue that one.
