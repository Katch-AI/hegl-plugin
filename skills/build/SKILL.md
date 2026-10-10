---
name: build
description: Use when the user runs `/hegl:build` or asks to start or continue building an agent.
---

# Build

Pick the agent (`hegl` → "Picking the agent"). No agent yet, or the user wants a new one: `create_agent`.

Read `get_agent`, plus the agent's `improvementRuns` through `graphql`, to see how far the build got:

| State | Continue with |
| --- | --- |
| No requirements document | `building-the-automation`, from learning the job |
| Requirements, no flow | `building-the-automation`, from the first step not done yet |
| A flow, no improvement run | Smoke-test it, then `implementing-decision-boxes` |
| An open improvement run | `implementing-decision-boxes`, on that run. Never start a second |
| A run `AWAITING_REVIEW` | The user's move: open the run's page for them |
| A published flow (`publishedFlow`) | Nothing left to build. Offer `feedback` or `fix-errors` |

Say in one line where you are picking up, then go on. Go by what Hegl shows, not by what the user remembers.
