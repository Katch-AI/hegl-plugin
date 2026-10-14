# Feedback

Feedback is a real-world outcome tied to a run: right or wrong, and ideally which judgment call. It reaches Hegl at runtime through the Hegl piece's `record_feedback` action (`auth: "{{connections['<platform connection external id>']}}"`). The narrower the attachment (`decisionBoxExecutionId` > `flowRunId` > `flowId`), the more useful the row. Read it back with `search_feedbacks`.

## Props

`record_feedback`: `flowId` (required), `positive` (required), `confidence?`, `decisionBoxId?`, `flowRunId?`, `decisionBoxExecutionId?`, `text?`, `payload?`, `submissionContext?`. `confidence` defaults to `DIRECT` (a human said so). Use `HIGH` (≥0.85), `MEDIUM` (0.6–0.85), `LOW` (<0.6) only when a classifier decided polarity or attribution. Always record low-confidence rows too; eval-set builders filter on `confidence`. Put the classifier's score, rationale, and model in `payload`.

## Sources, best first

| Source | How it works | Confidence |
|---|---|---|
| Fields the team already fills in their CRM (`Outcome`, `Quality score`) | A cron trigger flow polls records changed since the last run that carry the run-id marker and a filled field; a CODE step maps field values to `positive`; loop and record. Keep a cursor in `@activepieces/piece-store`. Handles late and edited entries. | `DIRECT` |
| Reply to an email the agent sent through Hegl | With the inbound-email trigger flow the reply starts a run (`email.md`, `in_reply_to`): classify it there (`jev_decision`) and `record_feedback` against the box it judges. Without that trigger flow Hegl classifies it; just pass `flowRunId` to `send_email`. | bucketed |
| Approve/correct pause in the flow | After `await_user_input`, a router on `{{ <pause>.output.button }}`; on the "approve edited" branch record feedback with `payload: {original, corrected, reason}`. Pair with a post-run source for volume. | `DIRECT` |
| CRM status push (a webhook when a stage flips) | Piece trigger on the record; branch on terminal stages only. | `DIRECT` |
| Chat reaction (Slack 👍/👎) | `reaction_added` trigger filtered to an allowlist; ignore the bot's own reactions. | `DIRECT` |
| Reply to email sent from the user's own mailbox | Gmail/Outlook trigger, then the Hegl LLM piece's `jev_decision` (a `noul` for is-feedback, a `choice` for polarity) or `completions`; a CODE step buckets the probability into `confidence`. Only when Hegl email is not an option. | bucketed |
| External webhook or widget | AP `WEBHOOK` trigger; the caller posts `{flow_run_id, positive, text}`. Needs a `feedback_agent`-scoped token, which there is no tool to mint: ask Hegl for one with `report_platform_issue` (category `MISSING_API`) and tell the user this source waits on it. | `DIRECT` |

## Correlation

The signal almost never carries the run id. Pick one, best first:

1. **Hidden marker on the side effect.** Write the `fr-…` id into a custom CRM field, a Slack message footer, or an email header when the candidate flow acts. The feedback flow reads it back.
2. **Natural key lookup.** The signal carries an id the run also touched (opportunity id, ticket number); find the run with `search_flow_runs(agent_id, query)`.
3. **Most recent run within N minutes.** Weakest; only when nothing can carry a marker. Use UTC.

## Flow shape

```
trigger → CODE: extract marker + raw signal → (CODE or LLM: classify) → router: skip if no marker → record_feedback
```

One feedback flow per source; do not merge them. Watch for double counting (a stage flipping back and forth) and for records edited before the marker existed.
