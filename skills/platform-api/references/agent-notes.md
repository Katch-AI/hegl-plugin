# Agent Notes

Agent notes are open-ended ideas, feature requests, or requirement changes about an agent (e.g. "user wants to also handle Spanish-language inputs", "add a Slack DM trigger in v2") that a later improvement run picks up and either applies or dismisses. They are **distinct from feedback**: feedback (the `record_feedback` piece action) is a right/wrong signal on a specific run/execution; agent notes are the change-request channel for the agent's general operation, with their own lifecycle (`NEW → APPLIED | DISMISSED`).

Requests that come up while learning the job belong in the requirements document (`update_agent_documents`), not in notes.

## create_agent_note(agent_id, text, submission_context?)

`submission_context` says who or what submitted it. Returns the note (`id`, `text`, `status`, `submissionContext`, `createdAt`); status starts at `NEW`.

**Agent notes are NOT a queue for reviewing feedback.**

## update_agent_note_status(agent_note_id, status)

`status`: `NEW | APPLIED | DISMISSED`. Allowed transitions: NEW → APPLIED, NEW → DISMISSED, APPLIED → NEW, DISMISSED → NEW (reopen). Other transitions fail validation.

## Reading notes

Through `graphql`:

```graphql
query AgentNotes($agentId: AgentId!, $status: AgentNoteStatusEnum) {
  findAgent(id: $agentId) {
    notes(status: $status) { id status text submissionContext createdAt updatedAt }
  }
}
```

- `status` is optional (`NEW`, `APPLIED`, `DISMISSED`); omit for all.
- Most recent first.
