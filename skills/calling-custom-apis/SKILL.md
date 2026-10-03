---
name: calling-custom-apis
description: Use when the customer's agent must call an HTTP API that has no dedicated Activepieces piece — internal services, undocumented vendor APIs, anything reachable over plain HTTP(S) with API-key, basic, OAuth2, or JWT-from-shared-secret auth. NOT for APIs that have a real piece (search the pieces catalog first) and NOT for non-HTTP protocols (those are still missing-piece territory).
---

# Calling Custom APIs

## Overview

The `@marcus-ai/piece-marcus-custom-api` piece calls any HTTP API with credentials
stored as a normal AP connection. One action — `custom_api_request` — applies
the connection's auth automatically: API key header, basic auth, OAuth2
bearer token, or a fresh short-lived JWT signed from a shared secret on every
request. You never hand-build auth headers or signing code.

**Order of preference:** a dedicated piece (check `activepieces` skill's
pieces-catalog) → this piece → `missing-pieces/<name>.md` (non-HTTP or
piece-worthy integrations).

## What to find out

1. **Base URL** — e.g. `https://api.acme.internal`.
2. **Auth shape** — which the API accepts:
   - API key/token in a header → `SECRET_TEXT`
   - username + password → `BASIC_AUTH`
   - OAuth2 authorization-code (customer has client id/secret + endpoint URLs) → `OAUTH2`
   - JWT minted from a shared secret (HS256/384/512) → `CUSTOM_AUTH`
3. **An example request** (curl or docs) if one exists; it pins the header
   name (`Authorization: Bearer` vs `X-Api-Key`) and paths.

## Declaring the connection and base URL

The connection carries auth only — the base URL is **config**, declared
separately via `request_config` and linked to the connection requirement.
`request_connection` has no `base_url` argument.

```
request_connection(
  agent_id: "a-…"
  piece_name: "@marcus-ai/piece-marcus-custom-api"
  purpose: "Read inventory levels from the Acme warehouse API"
  requested_display_name: "Acme warehouse API"
  allowed_auth_types: ["SECRET_TEXT"]          # only what the API accepts
)
```

`allowed_auth_types` filters the methods the customer sees; pass exactly what
the API accepts. One requirement per distinct API, even if two share an auth
style.

Once you have the connection requirement's id, declare the base URL as a
`URL`-typed config field linked to it via `connection_requirement_id`:

```
request_config(
  agent_id: "a-…"
  connection_requirement_id: "cr-abc123"
  title: "Acme warehouse API base URL"
  description: "Base URL of the customer's Acme warehouse API instance."
  fields: [
    { key: "base_url", label: "Base URL", purpose: "Root URL every request is made against.", type: "URL", value: "https://api.acme.example" }
  ]
)
```

Any other tenant config the custom API needs (e.g. a tenant/account id, a
default query param) can be declared the same way — either more fields on
the same `request_config` call, or a separate standalone `request_config` call
(no `connection_requirement_id`) for config that isn't tied to this connection.
See the `request_config` tool (see `platform-api`) for the full
argument/field reference and the standalone-vs-linked distinction. For a
**non-secret** field you can derive from the API's public docs — the base
URL, a header name, a fixed default — set its `value` in the `request_config`
call; it is pre-filled in the dashboard for the customer to review or
override. Credentials belong in the connection, never in a config `SECRET` field:
config values ride verbatim in every run's trigger payload, so a token there
shows in run history.

## Wiring the flow step

Reference the connection by its **externalId** (read it back via
`get_agent` (its `connectionRequirements`: `status`, `connection.externalId`)
once the requirement is `satisfied`), never by display name.

The base URL is read at dispatch time off the trigger payload's injected
config, keyed by the connection requirement's id —
`{{trigger.output.body.config.connection_requirements['<cr_id>'].base_url}}` — not baked
into the step as a literal:

```json
{
  "name": "step_fetch_inventory",
  "type": "PIECE",
  "settings": {
    "pieceName": "@marcus-ai/piece-marcus-custom-api",
    "pieceVersion": "~0.1.0",
    "actionName": "custom_api_request",
    "input": {
      "auth": "{{connections['<externalId>']}}",
      "base_url": "{{trigger.output.body.config.connection_requirements['cr-abc123'].base_url}}",
      "path": "/v1/inventory",
      "method": "GET",
      "query": { "warehouse": "eu-1" }
    },
    "propertySettings": {
      "auth": { "type": "MANUAL" },
      "base_url": { "type": "MANUAL" },
      "path": { "type": "MANUAL" },
      "method": { "type": "MANUAL" },
      "query": { "type": "MANUAL" }
    }
  }
}
```

- `base_url` in the step MUST reference the config requirement's `cr_id` exactly as declared via `request_config`'s `connection_requirement_id` — confirm `status: SATISFIED` via `get_config_requirement` before wiring the reference, since an unsatisfied requirement resolves to nothing at dispatch time.
- Output is `{status, headers, body}`; `body` is the parsed JSON.
- Non-2xx fails the step (good — fail loudly). Set `"fail_on_error": false`
  only when the flow genuinely branches on error responses.
- API-key APIs with a custom header: set `"auth_header_name": "X-Api-Key"`,
  `"auth_header_prefix": ""`.
- JWT connections need nothing extra in the step — signing config (secret,
  algorithm, claims, ttl, header) lives on the connection the customer fills
  in.

## Credentials the API wants in the body

SOAP `login()` and the OAuth2 password grant put credentials in the body, not a
header. AP resolves connection fields into **any** prop, so reference them there
and turn the auth header off:

```json
"input": {
  "auth": "{{connections['<externalId>']}}",
  "base_url": "{{trigger.output.body.config.connection_requirements['cr-abc123'].base_url}}",
  "method": "POST",
  "send_auth_header": false,
  "content_type": "text/xml",
  "body_raw": "<soapenv:Envelope …><n1:username>{{connections['<externalId>'].username}}</n1:username><n1:password>{{connections['<externalId>'].password}}</n1:password>…</soapenv:Envelope>",
  "response_format": "xml"
}
```

- `{{auth.username}}` does **not** work. AP evaluates unknown template paths and
  yields an empty string, so the request silently goes out with no credential.
  Only `{{connections[…]}}` resolves.
- `body_raw` and `body` are mutually exclusive; setting both fails the step.
- `response_format: "xml"` parses the reply — namespace prefixes stripped,
  attributes under `@_`, values left as strings. Read it as
  `{{step_login.output.body.Envelope.Body.loginResponse.result.sessionId}}`.
- For a form grant use `"content_type": "application/x-www-form-urlencoded"` and
  a `body_raw` of `grant_type=password&username=…&password=…`.

Credentials the piece cannot reach at all — an SDK handshake, a non-HTTP
protocol — belong in a sandbox step instead (`activepieces` →
`references/sandbox-environments.md`).

## Per-auth-shape notes

| Shape | allowed_auth_types | Customer enters | Step extras |
|---|---|---|---|
| API key | `["SECRET_TEXT"]` | the key | `auth_header_name`/`_prefix` if not `Authorization: Bearer` |
| Basic | `["BASIC_AUTH"]` | username + password | none |
| OAuth2 | `["OAUTH2"]` | endpoint URLs at connect; admin configures client id/secret | none — flag to the user that an OAuth app must be configured first |
| JWT from secret | `["CUSTOM_AUTH"]` | secret, algorithm, iss/aud/sub, ttl, header | none |
