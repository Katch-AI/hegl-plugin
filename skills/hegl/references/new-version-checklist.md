# New version checklist

For any change to a published agent, whatever started it (feedback, an error, a request, a new model).

1. **Open the run first** (`start_improvement_run`, `IMPROVEMENT`). Never edit the published flow. One session per run.
2. **Read what is live**, not your notes: the published flow, `requirements`, open change requests (`platform-api/references/agent-notes.md`), the last version's justification.
3. **Read production since the last version** (`search_flow_runs`, `search_feedbacks`, `search_error_incidents`). Where it disagrees with the last score, fix the measurement first.
4. **The measure follows the feedback source.** A kind of difference counts against the agent only if the source reacts to it when it sees it; what it sees and leaves alone is not scored. Check the scorer on past outputs: the ones that passed untouched score clean, the corrected ones do not.
5. **Re-check the last version's claims**: each fix it said it made, and its "not proven" list.
6. **Sort by cause.** A skipped item and the agent's own writes are not feedback. A cause seen before is not downgraded again.
7. **Trace each miss to the step that lost it**: not in any input, lost reading the input, lost in a later step, or only arranged or worded differently. Count them. A step that loses most of them is replaced, not patched.
8. **Work done by hand.** Whatever the user fixed or did by hand since the last version is a requirement.
9. **Tune on some of the new evidence, score on the rest.** Each item you address gets a line in `requirements` and a permanent test.
10. **Contradictory feedback**: ask once, showing both forms and how often each occurs.
11. **Changes outside a box** (a mapping, a route, a write) are tested directly; no box score sees them.
12. **Re-measure, never re-quote.** Score the base version and the candidate the same day on the same rows. A new scorer or dataset is a new metric name.
13. **The copy.** Replace every old id, wire the boxes, declare the triggers. Test last, through the real trigger to the last external write, on a record agreed with the user.
14. **Code steps are files** with `node` tests; build the flow JSON from the files, never by hand-editing the last version's tree.
15. **Documents.** Rewrite `requirements` and `flow_description` to match the candidate, then read them back against the flow (`get_agent`, `get_activepieces_flow`). Every version, not only when asked.
16. **Finish when nothing is left to try.** Name what is unaddressed and unproven. Every remaining miss is put down to a measured limit (missing input, the source contradicting itself, run-to-run variation), and every idea was tried or ruled out on numbers. A list of things you could try next is not a finish. An unattended run never writes to the customer's systems.

Removing a review step is the user's decision, made on the measured share of outputs that passed unchanged. It is its own version.
