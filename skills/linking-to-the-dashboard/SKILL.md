---
name: linking-to-the-dashboard
description: Use when you mention anything the user can look at in the Hegl dashboard (an agent, a run, a version, a decision box, an experiment, a form, a connection, usage, billing) or hand them a step only they can take. Covers where each link comes from, when to open it, and request links that expire.
---

# Linking to the dashboard

Whenever you name something the user can look at, link it. Take the link from a tool result; never build a dashboard URL yourself.

## Where links come from

| For | Read |
| --- | --- |
| A record | Its `dashboardUrl`: agent, flow run, decision box, flow (the version's report), experiment (its box's backlog), trigger flow (the triggers page), improvement run (the versions page), human review, connection requirement, config requirement |
| An agent's pages | `get_agent` → `dashboardLinks`: `spec`, `connections`, `config`, `triggers`, `versions`, `decisionBoxes`, `runs`, `forms`, `feedback` |
| An organization's pages | `list_organizations` → `dashboardLinks`: `agents`, `connections`, `members`, `usage`, `billing` |

A tool result without the field? Select `dashboardUrl` through `graphql`.

## Link or open

Something to look at: a Markdown link in your reply, named for what it shows ("the run", "version 4's report"), never a bare URL.

Something only the user can do (make a connection, fill a config form, review and publish a version, answer a human review): open the page. In Claude Code the plugin opens it for you and says so; otherwise open it in the user's browser (`open` on macOS, `xdg-open` on Linux, `start ""` on Windows). Either way, say in one line what to do there, then poll for the outcome. No local shell or browser (a hosted sandbox)? Give the link instead.

## Request links expire

A connection or config requirement's `dashboardUrl` is the user's personal link to that one request. It works without signing in and lasts an hour. Do not keep one: every read (`get_agent`, `get_config_requirement`) returns a fresh link. If the user says the link expired, read the requirement again and open the new one.
