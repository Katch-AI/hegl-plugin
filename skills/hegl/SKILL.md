---
name: hegl
description: Use when starting any work on a Hegl agent (building an automation, improving a decision box, inspecting runs or feedback) and whenever unsure which Hegl skill or tool applies. Orientation and the rules every other Hegl skill assumes.
---

# Hegl

Hegl turns a job someone does by hand into an automation that runs on its own. Two halves: the dashboard, where the user reads what you built and publishes it, and an Activepieces flow that does the work. You learn the job, build the flow, measure how well it does the job, and improve it until it is good enough to publish.

## Tools

The `hegl` MCP server acts as the signed-in user across their organizations. Start with `list_organizations` for organization and agent ids. Tools that create, search or run in an agent's context take `agent_id`; tools that act on an existing record take that record's id (`id`, `flow_id`, `decision_box_id`, …). `get_agent` returns an agent's name, description, documents, flows, trigger flows and connection requirements; poll it for provisioning and connection status. Anything without a tool goes through `graphql` (introspection works, errors carry "Did you mean"). `platform-api` maps what to call when.

## How the work goes

1. Learn the job. Write it down.
2. Build the flow with placeholder decisions and check it runs end to end.
3. Build a test set from real past examples, check the labels, set a target score.
4. Keep a backlog of ideas, run experiments, iterate until the target is met.
5. Finish the version for review. The user publishes it from the dashboard.

`building-the-automation` covers 1 and 2, `implementing-decision-boxes` 3 to 5. `platform-api` and `activepieces` hold the details. Read the skill before acting.

## Documents

Keep two documents current with `update_agent_documents` whenever they change: `requirements` (what the job is and what the agent will do) and `flow_description` (how the flow works, step by step, with a Mermaid diagram; see `mermaid`). They are the user's window into your work. Do not wait for sign-off on them. Send the whole document each time.

## Writing for the dashboard

Everything that lands on Hegl is read by people who are not developers: requirements, flow description, flow and version descriptions, experiment titles and results, publish notes, artifacts. Short sentences, plain words, the systems they know ("Slack", "Salesforce"), never the machinery ("piece", "flow JSON", "webhook", "CODE step"). Technical detail goes under an "Implementation detail" heading.

## Working practice

- Record state on Hegl as you go: start the improvement run, write the backlog, define metrics and record iterations the moment each exists. Anything held back is invisible to the user until then.
- Before saying something is done, read it back (`get_agent`, `get_flow_run`, `get_activepieces_flow`) and go by what you saw, not by a mutation's return.
- Big lookups (sampled records, piece metadata, long documents) belong in a subagent that returns a short answer, if your harness has one.
- Something missing or broken (a piece, a tool, a skill)? `report_platform_issue`, then tell the user plainly what you cannot do. Do not fake around it.
- Hegl's hosted coding agent may have worked on the same agent. `list_workspace_files` and `read_workspace_file` reach its files; `write_workspace_file` hands files back.
