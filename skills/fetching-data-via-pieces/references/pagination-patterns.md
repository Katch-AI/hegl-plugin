# Pagination patterns — piece-by-piece reference

## Contents

- [Salesforce — `@activepieces/piece-salesforce`](#salesforce--activepiecespiece-salesforce) — `run_query` with SOQL LIMIT/OFFSET; keyset workaround for tables >2 000 rows.
- [Airtable — `@activepieces/piece-airtable`](#airtable--activepiecespiece-airtable) — single-page `airtable_find_record`; multi-page uses the piece's `custom_api_call` with the `offset` token per call.
- [HubSpot — `@activepieces/piece-hubspot`](#hubspot--activepiecespiece-hubspot) — piece action returns one page only; multi-page uses the piece's `custom_api_call` against CRM Search with the `after` cursor per call.
- [Notion — `@activepieces/piece-notion`](#notion--activepiecespiece-notion) — `notion-find-database-item` paginates internally; use date/ID range filters for large tables.
- [Postgres — `@activepieces/piece-postgres`](#postgres--activepiecespiece-postgres) — `run-query` with parameterized LIMIT/OFFSET and an agent-controlled loop.
- [Google Sheets — `@activepieces/piece-google-sheets`](#google-sheets--activepiecespiece-google-sheets) — `find_rows` with `startingRow`/`numberOfRows` props for explicit row windows.

Each section gives the recommended action, the pagination mechanism the agent controls via `props`, and a loop to follow. In the loops, `sample(props)` is one pass of the SKILL.md loop (`UPDATE_ACTION` the `inv_<uuid>` step's `input` to `props`, `sample_activepieces_step`, poll `get_activepieces_flow_run`, return `steps.inv_<uuid>.output`).

Versions are from the AP checkout at the time of writing. Flag any mismatch with `# verify at install time`.

---

## Salesforce — `@activepieces/piece-salesforce`

Recommended action: `run_query` (action name `run_query`; display name "Run Query (Advanced)").

Prop shape: `{"query": "<full SOQL string>"}`. The agent writes the entire SOQL, including `LIMIT` and `OFFSET`. Pick a page size that keeps each response under `AP_MAX_FILE_SIZE_MB` (default 25 MB); `LIMIT 1000` works for typical Opportunity rows.

```python
# piece @activepieces/piece-salesforce 0.7.3 (verify at install time), action run_query, connection "Prod Salesforce"
offset = 0
while True:
    page = sample({
        "query": f"SELECT Id, StageName, Amount FROM Opportunity LIMIT 1000 OFFSET {offset}"
    })
    records = page.get("records", [])
    if not records:
        break
    yield from records
    offset += 1000
```

**Caveat:** SOQL `OFFSET` is capped at 2 000 by Salesforce. For tables larger than 2 000 rows, use a `WHERE CreatedDate >= {last_id}` keyset approach or the Bulk API instead.

---

## Airtable — `@activepieces/piece-airtable`

Recommended action: `airtable_find_record` (finds records matching a field/value filter). The piece has no general list-all action — use `find-record` with an empty or broad `searchValue` to retrieve a first page, then walk pages via the Airtable `offset` token.

**Important:** The Airtable AP action does not expose an `offset` prop. The action fetches one page internally. To paginate, sample the piece's `custom_api_call` action against `GET /{baseId}/{tableId}` (it reuses the connection's auth), or ask the user whether a full-table export is really needed.

If the table is small enough to fit in one response, use `airtable_find_record` with a catch-all filter. For larger tables, sample `custom_api_call` once per page, passing the `offset` token returned in each response as the next call's `offset` query parameter; stop when a response has no `offset`.

```python
# Single-page fetch via the piece — works for tables < AP_MAX_FILE_SIZE_MB.
# For multi-page needs, sample custom_api_call once per page with the offset token.
# piece @activepieces/piece-airtable 0.6.7 (verify at install time), action airtable_find_record, connection "Prod Airtable"
page = sample({
    "base": "<base-id>",          # Airtable base ID (starts with "app")
    "tableId": "<table-id>",       # Table ID (starts with "tbl")
    "searchField": "Name",         # Any indexed field
    "searchValue": "",             # Empty matches all rows up to page limit
})
records = page  # list of AirtableRecord dicts
```

---

## HubSpot — `@activepieces/piece-hubspot`

Recommended action: `find-contact`, `find-deal`, `find-company`, etc. Each uses `doSearch` internally and returns up to `MAX_SEARCH_PAGE_SIZE` (100) results per call. The `after` cursor appears in the *response* (`paging.next.after`), not as an input prop.

To walk all pages, call the action once per page and pass the cursor from the previous response back via the `after` field in props — but **the current AP action does not expose `after` as a prop**. Multi-page collection samples the piece's `custom_api_call` action once per page (`POST /crm/v3/objects/{objectType}/search` with `{"after": "<cursor>", "limit": 100}`), passing the previous response's `paging.next.after` as `after`.

```python
# Multi-page HubSpot contacts — the piece's custom_api_call action reuses the
# connection's auth against HubSpot CRM Search; sample it once per page.
#
# If you only need one page (≤ 100 records), use the find-contact action:
# piece @activepieces/piece-hubspot 0.8.4 (verify at install time), action find-contact, connection "Prod HubSpot"
page1 = sample({
    "firstSearchPropertyName": "email",
    "firstSearchPropertyValue": "@example.com",
})
contacts = page1.get("results", [])
# For full pagination, sample custom_api_call against the HubSpot CRM Search API
# and pass paging.next.after through successive calls.
```

---

## Notion — `@activepieces/piece-notion`

Recommended action: `notion-find-database-item`. The action queries a database with filters and returns all matching rows in one shot — it paginates internally against the Notion API. No `start_cursor` prop exists.

For a full-table dump, call with an empty filter object. For tables that exceed `AP_MAX_FILE_SIZE_MB`, use a filter that partitions rows by a date or ID range.

```python
# piece @activepieces/piece-notion 0.6.1 (verify at install time), action notion-find-database-item, connection "Prod Notion"
# Empty filterDatabaseFields returns all rows (no filter applied).
result = sample({
    "database_id": "<notion-database-id>",
    "filterDatabaseFields": {},
})
records = result.get("results", [])
```

**Size guard:** If the database is large, filter by `created_time` or a status field to fetch a date-bounded slice at a time.

---

## Postgres — `@activepieces/piece-postgres`

Recommended action: `run-query`. The agent writes the full SQL, including `LIMIT` and `OFFSET`. Use parameterized queries to prevent SQL injection — pass dynamic values in `args` and reference them as `$1`, `$2`, etc.

```python
# piece @activepieces/piece-postgres 0.2.3 (verify at install time), action run-query, connection "Prod Postgres"
offset = 0
page_size = 1000
while True:
    rows = sample({
        "query": "SELECT id, label, created_at FROM tickets ORDER BY id LIMIT $1 OFFSET $2",
        "args": [page_size, offset],
    })
    if not rows:
        break
    yield from rows
    offset += page_size
```

Prop names confirmed from source: `query` (required), `args` (optional array), `query_timeout` (optional ms, default 30 000).

---

## Google Sheets — `@activepieces/piece-google-sheets`

Recommended action: `find_rows`. Props `startingRow` and `numberOfRows` let the agent slice the sheet in explicit row windows. Leave `searchValue` empty to return all rows in the window.

For small sheets (fits one response), `get-many-rows` fetches the whole sheet at once with no pagination needed.

```python
# piece @activepieces/piece-google-sheets 0.14.6 (verify at install time), action find_rows, connection "Prod Google Sheets"
start = 2          # row 1 is the header
page_size = 500
while True:
    rows = sample({
        "spreadsheetId": "<spreadsheet-id>",
        "sheetId": "<sheet-id>",         # numeric sheet ID, not the tab name
        "startingRow": start,
        "numberOfRows": page_size,
        "searchValue": "",               # empty = return all rows in window
        "headerRow": 1,
        "useHeaderNames": True,
    })
    if not rows:
        break
    yield from rows
    start += page_size
```

Prop names confirmed from source: `spreadsheetId`, `sheetId`, `startingRow`, `numberOfRows`, `searchValue`, `headerRow`, `useHeaderNames`.
