# First build checklist

Go through it before finishing the first version. The how is in `building-the-automation` and `implementing-decision-boxes`.

1. **Ground truth.** Find what the customer's process already records about whether the job was done right (a later record state, their own finished output, their calculator). Add no step whose only purpose is collecting labels. An existing automation is a baseline, not the truth.
2. **Review while untrusted.** Until the output is trusted, it passes a person before it affects anything real (`await_user_input`). Agree who answers and where. The answers are eval rows.
3. **Baseline.** Measure how fast and how well the job is done today.
4. **Records against the description.** Read real records beside the written description of the job. Where they differ, ask.
5. **Rules.** Each rule the user states goes into `requirements` and gets a test in the same turn. A rule with no exceptions is code, not prompt.
6. **Never score on what you tuned on.** Too few examples: use an oracle or write new cases, and say so.
7. **What the score does not cover.** List it (field mappings, writes, the schedule, failure branches) and test each directly.
8. **Invariants.** The checks every correct output passes, one function shared by the harness and the flow.
9. **Model steps.** Frontier model first, then a cheaper tier. Record cost and latency; repeat runs when the score varies.
10. **No typed-in ids.** No id, host, address or allow-list typed into a step: config (`request_config`), the trigger payload or `get_agent`.
11. **One real run.** Through the real trigger to the last external write, on a record agreed with the user, read back afterwards. Test output reaches no real person. Force each failure branch once.
12. **Code steps are files.** Keep each CODE step as a file with `node` tests; build the flow JSON from the files.
13. **Feedback collection.** It cannot fail a run and it ignores the agent's own writes.
14. **Documents.** Rewrite `requirements` and `flow_description` to match the candidate, then read them back against the flow (`get_agent`, `get_activepieces_flow`).
15. **Finish last.** Say what is unproven. After publishing, read the first production run.

Removing the review is the user's decision, made on the measured share of outputs that passed unchanged. It is its own version.
