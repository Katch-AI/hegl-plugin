# Email

Every agent gets an inbox at creation (`ibx-<random>@<domain>`). Do not use the Gmail or IMAP pieces for the agent's own email; the Hegl inbox gives you threading, reply handling, and observability for free.

## What happens by itself

- **With the inbound-email trigger flow** (below), every email to an inbox starts a run of the published flow: new conversations and replies to emails the agent sent alike. A reply carries `in_reply_to`; branch on it. Hegl does not classify replies for you: when a reply judges the agent's work, `record_feedback` from the flow (`feedback.md`).
- **Without it**, a reply to an email the agent sent is matched by `In-Reply-To` and classified by Hegl: replies that judge the agent's work become `Feedback` rows (`HIGH | MEDIUM | LOW`), others are flagged for human review (requires `flowRunId` on the send). A new email is flagged for review.

## Receiving as a trigger

`create_trigger_flow(name: "Email", trigger_key: "inbound_email")`. Hegl provisions the flow body; do not fill it. List its id in `set_supported_triggers`. The candidate's `trigger.body.inputs` is:

```json
{ "received_email_id": "rcv-…", "inbox": { "id": "ibx-…", "name": "…", "address": "…" }, "from": "…", "to": ["…"], "cc": ["…"],
  "subject": "…", "text_body": "…", "html_body": "…", "received_at": "2026-…",
  "attachments": [{ "id": "att-…", "filename": "…", "content_type": "…", "byte_size": 123, "download_url": "https://…" }],
  "dropped_attachments": [{ "filename": "…", "detected_content_type": "…" }], "in_reply_to": null }
```

For a reply to an email the agent sent, `in_reply_to` is:

```json
{ "sent_email_id": "snt-…", "flow_run_id": "fr-…",
  "flow_run": { "status": "finished", "tagline": "…", "metadata": { "…": "…" }, "trigger_name": "inbound_email", "trigger_inputs": { "…": "…" } },
  "thread": [{ "direction": "received", "id": "rcv-…", "from": "…", "to": ["…"], "subject": "…", "text_body": "…", "at": "2026-…" },
             { "direction": "sent", "id": "snt-…", "flow_run_id": "fr-…", "from": "…", "to": ["…"], "subject": "…", "text_body": "…", "at": "2026-…" }] }
```

`thread` is the conversation before this email, oldest first; the reply itself is the top-level payload. `flow_run` is the run that sent the parent email: `metadata` is what its `finish_flow_run` stored (keep the state a follow-up needs there) and `trigger_inputs` what started it, minus its own `in_reply_to`. Answer in the same thread with `inReplyToReceivedEmailId` set to this trigger's `received_email_id`.

`download_url` needs no token and expires 1 hour after the run is triggered; download it in the first steps with a non-default `User-Agent` (Cloudflare rejects Python's). `dropped_attachments` were refused for a disallowed type.

Route on `inbox.address` if several inboxes feed one flow. Anyone who has the address can start a run (it is the From of every email the agent sends), so check `from` against the allowed senders before any side effect and finish quietly for everyone else.

## Sending

The Hegl piece's `send_email` action. Props: `to` (list), `subject`, `textBody`, `htmlBody`, `flowRunId: "{{ step_start.output.flowRunId }}"` (always), `inReplyToReceivedEmailId: "{{ trigger.output.body.inputs.received_email_id }}"` (when replying to the trigger email; then omit `to`), optional `fromInboxId`, `replyToAddress`, `cc`, `bcc`, `attachments` (`[{file, filename, contentType}]`), `headers`. `file` is a URL or `data:<mime>;base64,…`; bare base64 is dropped. Always set `filename` on a data URL, or the recipient gets `unknown.<ext>`.

Decide the recipient explicitly: reply to the sender, a fixed list, a decision box's output field, or a field looked up from a record. Never assume "the customer". Compose `htmlBody` with the `composing-email-html` skill and always send `textBody` too.

## Inboxes

`create_agent_inbox(agent_id, name, display_name?)` returns the inbox with its `address`. Surface the address to the user so they can set up forwarding. `update_agent_inbox(agent_inbox_id, name?, display_name?)`, `discard_agent_inbox(agent_inbox_id)` (not the default one). One inbox covers most agents; add more only when different sources need routing or different identities.

Reads on `findAgent(id:)` through `graphql`: `defaultInbox`, `agentInboxes`, `receivedEmails(first:)` (`status`: pending, classifying, classified, failed, needs_review), `sentEmails(first:)` (`status`: pending, dispatched, failed).
