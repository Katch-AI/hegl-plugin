# Example ingestions

Three worked examples, each self-contained. Copy, adapt the connection name and field list, run.

**Prerequisite:** `sample(props)` below is one pass of the SKILL.md loop (`UPDATE_ACTION` the `inv_<uuid>` step's `input` to `props`, `sample_activepieces_step`, poll `get_activepieces_flow_run`, return `steps.inv_<uuid>.output`); write each output to a file and run the rest of the script over the files.

## Contents

- [Pulling labeled rows from Salesforce](#pulling-labeled-rows-from-salesforce) — SOQL `run_query` loop with 80/20 train/val split written to JSONL.
- [Joining Gmail threads to JIRA tickets](#joining-gmail-threads-to-jira-tickets) — multi-piece join using thread IDs as the correlation key.
- [Sanity-checking a connection before committing to a dataset shape](#sanity-checking-a-connection-before-committing-to-a-dataset-shape) — lightweight single-record fetch to confirm field presence before full ingestion.

---

## Pulling labeled rows from Salesforce

Opportunities where `StageName` carries the outcome — "Closed Won" or "Closed Lost" — are already labeled. No join, no inference needed.

The script pages through up to 2 000 rows (the Salesforce SOQL `OFFSET` ceiling; see `pagination-patterns.md` for the keyset workaround when the table is larger), then splits 80 / 20 into train and validation sets and writes `train.jsonl` and `val.jsonl` to the current directory.

```python
import json
import random

PIECE = "@activepieces/piece-salesforce"
PIECE_VERSION = "0.7.3"  # verify at install time
CONNECTION = "Prod Salesforce"
PAGE_SIZE = 1000
MAX_OFFSET = 2000  # Salesforce SOQL OFFSET ceiling

records = []

# step: PIECE / PIECE_VERSION, action run_query, connection CONNECTION
offset = 0
while offset < MAX_OFFSET:
    page = sample({
        "query": (
            "SELECT Id, Name, Amount, StageName, CloseDate "
            "FROM Opportunity "
            "WHERE StageName IN ('Closed Won', 'Closed Lost') "
            f"LIMIT {PAGE_SIZE} OFFSET {offset}"
        )
    })
    batch = page.get("records", [])
    if not batch:
        break
    records.extend(batch)
    offset += PAGE_SIZE

# Build (input, label) pairs.
examples = [
    {
        "input": {
            "name": r["Name"],
            "amount": r["Amount"],
            "close_date": r["CloseDate"],
        },
        "label": "won" if r["StageName"] == "Closed Won" else "lost",
    }
    for r in records
]

random.shuffle(examples)
split = int(len(examples) * 0.8)
train, val = examples[:split], examples[split:]

with open("train.jsonl", "w") as f:
    for ex in train:
        f.write(json.dumps(ex) + "\n")

with open("val.jsonl", "w") as f:
    for ex in val:
        f.write(json.dumps(ex) + "\n")

print(f"Wrote {len(train)} train, {len(val)} val examples.")
```

---

## Joining Gmail threads to JIRA tickets

The flow under construction triages inbound emails into JIRA tickets with a priority label. Eval data needs `(email_body, priority)` pairs. The label lives in JIRA; the text lives in Gmail. Pull both, then correlate.

**Prerequisite check:** both a Gmail piece action that lists messages and a JIRA piece action that queries issues must exist in the catalog. If either is missing, declare that to the user and stop — this skill only works with pieces that expose a data-retrieval action. Do not attempt to build the join using a piece that has no list or query action.

Correlation strategy: look for a JIRA ticket key (pattern `[A-Z]+-\d+`) in the email subject or body via regex. If that match fails, fall back to matching on `In-Reply-To` if the ticket was created by email. See `pagination-patterns.md` for the per-piece pagination details used in the loops below.

```python
import json
import re

GMAIL_PIECE = "@activepieces/piece-gmail"
GMAIL_VERSION = "0.6.4"  # verify at install time
JIRA_PIECE = "@activepieces/piece-jira-cloud"
JIRA_VERSION = "0.9.1"   # verify at install time
CONNECTION_GMAIL = "Prod Gmail"
CONNECTION_JIRA = "Prod JIRA"

TICKET_RE = re.compile(r"\b([A-Z]+-\d+)\b")

# --- Step 1: Pull inbound emails ---
emails = []
# step: GMAIL_PIECE / GMAIL_VERSION, action gmail_search_mail, connection CONNECTION_GMAIL
page_token = None
while True:
    props = {"query": "in:inbox", "maxResults": 100}
    if page_token:
        props["pageToken"] = page_token
    page = sample(props)
    messages = page.get("messages", [])
    if not messages:
        break
    emails.extend(messages)
    page_token = page.get("nextPageToken")
    if not page_token:
        break

# --- Step 2: Pull JIRA issues ---
jira_by_key = {}
# step: JIRA_PIECE / JIRA_VERSION, action search_issues, connection CONNECTION_JIRA
start_at = 0
page_size = 50
while True:
    page = sample({
        "jql": "project = SUPPORT ORDER BY created DESC",
        "startAt": start_at,
        "maxResults": page_size,
        "fields": "summary,priority,customfield_10001",  # customfield_10001 = inboundEmail on many instances
    })
    issues = page.get("issues", [])
    if not issues:
        break
    for issue in issues:
        jira_by_key[issue["key"]] = issue
    start_at += page_size
    if start_at >= page.get("total", 0):
        break

# --- Step 3: Join ---
examples = []
for email in emails:
    subject = email.get("subject", "")
    body = email.get("body", "") or email.get("snippet", "")
    text = f"{subject}\n{body}"

    match = TICKET_RE.search(text)
    if not match:
        continue  # no ticket reference found in this email

    key = match.group(1)
    if key not in jira_by_key:
        continue  # ticket not in our pull

    issue = jira_by_key[key]
    priority = issue["fields"]["priority"]["name"]
    examples.append({
        "input": {"subject": subject, "body": body},
        "label": priority,
    })

print(f"Joined {len(examples)} email-ticket pairs.")
with open("email_priority_eval.jsonl", "w") as f:
    for ex in examples:
        f.write(json.dumps(ex) + "\n")
```

---

## Sanity-checking a connection before committing to a dataset shape

The user has just connected Salesforce. Before scaffolding the full ingestion, pull five rows to confirm the connection is live and show the user what the data looks like. This takes ten seconds and catches bad credentials, wrong org, or missing field permissions early.

```python
import json

# step: @activepieces/piece-salesforce 0.7.2, action run_query, connection "Prod Salesforce"
rows = sample({"query": "SELECT Id, Name, StageName FROM Opportunity LIMIT 5"})
print(json.dumps(rows, indent=2))
```

After printing, ask the user: "Does this look right? Any fields missing?" Wait for confirmation before committing to the full eval dataset shape. If the connection fails — the connection is missing from `list_activepieces_connections`, the run ends `FAILED`, or a 4xx from AP — surface the error message verbatim and halt.
