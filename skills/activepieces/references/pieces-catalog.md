# AP pieces catalog

Source: <https://cloud.activepieces.com/api/v1/pieces>
Pieces: 766 (plus 2 Hegl-internal pieces; see bottom of table)
Detail files: 4 (see `piece-<name>.md` files in this directory for trigger/action/prop reference per piece)

The `detail` column marks pieces with a per-piece file at `piece-<piece-name>.md` in this
directory — read it before scaffolding a step using that piece. Pieces without a detail file
haven't been deeply documented yet; check the piece source at `./activepieces/packages/pieces/`
(clone setup: `SKILL.md` → "Debugging with the AP source") and write a new detail file if the
build paid the cost, following the shape of an existing `piece-*.md`.

## Contents

- The catalog — alphabetical table of all AP pieces with name, version, action/trigger counts, and detail-file links.

## The catalog

The bulk of the file is one big alphabetical table — grep for the piece name. Columns:

- `name` — the NPM-style piece identifier (use this in flow JSON's `pieceName`)
- `displayName` — the human label AP shows in its UI
- `version` — current semver on Hegl (use this in `pieceVersion`; ranges/`latest` are rejected)
- `actions` — number of actions the piece exposes
- `triggers` — number of triggers the piece exposes
- `detail` — link to the per-piece `piece-<name>.md` if one exists in `references/`

| name | displayName | version | actions | triggers | detail |
| --- | --- | --- | --- | --- | --- |
| @activepieces/cashfree-payments | Cashfree Payments | 0.0.1 | 9 | 0 |  |
| @activepieces/piece-0codekit | 0CodeKit | 0.1.1 | 75 | 0 |  |
| @activepieces/piece-activecampaign | ActiveCampaign | 0.1.9 | 7 | 9 |  |
| @activepieces/piece-activepieces | Activepieces Platform | 0.5.2 | 4 | 0 |  |
| @activepieces/piece-actualbudget | Actual Budget | 0.1.9 | 5 | 0 |  |
| @activepieces/piece-acuity-scheduling | Acuity Scheduling | 0.2.1 | 8 | 2 |  |
| @activepieces/piece-acumbamail | Acumbamail | 0.2.7 | 7 | 0 |  |
| @activepieces/piece-add-event | AddEvent | 0.1.1 | 9 | 2 |  |
| @activepieces/piece-afforai | Afforai | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-agentx | AgentX | 0.1.7 | 5 | 2 |  |
| @activepieces/piece-ai | AI | 0.11.0 | 6 | 0 |  |
| @activepieces/piece-aianswer | AI Answer | 0.2.1 | 6 | 0 |  |
| @activepieces/piece-aidbase | Aidbase | 0.2.1 | 7 | 8 |  |
| @activepieces/piece-aiprise | AiPrise | 0.2.1 | 17 | 0 |  |
| @activepieces/piece-air-ops | AirOps | 0.2.1 | 4 | 0 |  |
| @activepieces/piece-aircall | Aircall | 0.2.1 | 8 | 5 |  |
| @activepieces/piece-airparser | Airparser | 0.1.7 | 2 | 1 |  |
| @activepieces/piece-airtable | Airtable | 0.9.2 | 15 | 2 |  |
| @activepieces/piece-airtop | Airtop | 0.2.1 | 12 | 0 |  |
| @activepieces/piece-alai | Alai | 0.2.0 | 6 | 0 |  |
| @activepieces/piece-algolia | Algolia | 0.1.1 | 4 | 0 |  |
| @activepieces/piece-alt-text-ai | AltText.ai | 0.2.1 | 2 | 0 |  |
| @activepieces/piece-alttextify | AltTextify | 0.2.1 | 2 | 0 |  |
| @activepieces/piece-amazon-bedrock | AWS Bedrock | 0.4.1 | 5 | 0 |  |
| @activepieces/piece-amazon-s3 | Amazon S3 | 0.8.0 | 8 | 1 |  |
| @activepieces/piece-amazon-secrets-manager | AWS Secrets Manager | 0.2.1 | 6 | 0 |  |
| @activepieces/piece-amazon-ses | Amazon SES | 0.1.7 | 7 | 0 |  |
| @activepieces/piece-amazon-sns | Amazon SNS | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-amazon-sqs | Amazon SQS | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-amazon-textract | AWS Textract | 0.3.7 | 5 | 0 |  |
| @activepieces/piece-aminos | Aminos | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-ampeco | AMPECO | 0.3.1 | 377 | 1 |  |
| @activepieces/piece-anyhook-graphql | AnyHook GraphQL | 0.1.7 | 0 | 1 |  |
| @activepieces/piece-anyhook-websocket | AnyHook Websocket | 0.1.7 | 0 | 1 |  |
| @activepieces/piece-apify | Apify | 0.3.1 | 6 | 2 |  |
| @activepieces/piece-apitable | AITable | 0.4.2 | 4 | 1 |  |
| @activepieces/piece-apitemplate-io | APITemplate.io | 0.3.1 | 8 | 0 |  |
| @activepieces/piece-apollo | Apollo | 0.2.1 | 7 | 0 |  |
| @activepieces/piece-appfollow | AppFollow | 0.2.1 | 3 | 2 |  |
| @activepieces/piece-approval | Approval (Legacy) | 0.1.28 | 2 | 0 |  |
| @activepieces/piece-asana | Asana | 0.7.1 | 2 | 0 |  |
| @activepieces/piece-ashby | Ashby | 0.2.1 | 1 | 0 |  |
| @activepieces/piece-ask-handle | AskHandle | 0.1.8 | 4 | 3 |  |
| @activepieces/piece-asknews | AskNews | 0.1.0 | 8 | 1 |  |
| @activepieces/piece-assembled | Assembled | 0.1.9 | 6 | 3 |  |
| @activepieces/piece-assemblyai | AssemblyAI | 1.1.10 | 14 | 0 |  |
| @activepieces/piece-attio | Attio | 0.3.1 | 15 | 5 |  |
| @activepieces/piece-autocalls | Autocalls | 0.1.7 | 5 | 3 |  |
| @activepieces/piece-avian | Avian | 0.0.7 | 1 | 0 |  |
| @activepieces/piece-avoma | Avoma | 0.1.7 | 3 | 4 |  |
| @activepieces/piece-azure-ad | Azure Active Directory | 0.3.1 | 17 | 3 |  |
| @activepieces/piece-azure-blob-storage | Azure Blob Storage | 0.1.10 | 9 | 0 |  |
| @activepieces/piece-azure-communication-services | Azure Communication Services | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-azure-devops | Azure DevOps | 0.1.1 | 6 | 2 |  |
| @activepieces/piece-azure-openai | Azure OpenAI | 0.2.1 | 2 | 0 |  |
| @activepieces/piece-backblaze | Backblaze | 0.1.7 | 2 | 1 |  |
| @activepieces/piece-bamboohr | BambooHR | 0.3.1 | 1 | 1 |  |
| @activepieces/piece-bannerbear | Bannerbear | 0.5.1 | 2 | 0 |  |
| @activepieces/piece-barcode-lookup | Barcode Lookup | 0.0.9 | 1 | 0 |  |
| @activepieces/piece-baremetrics | Baremetrics | 0.0.9 | 4 | 0 |  |
| @activepieces/piece-base44 | Base44 | 0.1.8 | 3 | 1 |  |
| @activepieces/piece-baserow | Baserow | 0.11.2 | 14 | 7 |  |
| @activepieces/piece-beamer | Beamer | 0.2.1 | 5 | 1 |  |
| @activepieces/piece-beebole | Beebole | 0.2.1 | 8 | 0 |  |
| @activepieces/piece-beehiiv | Beehiiv | 0.4.1 | 8 | 4 |  |
| @activepieces/piece-bettermode | Bettermode | 0.2.1 | 5 | 0 |  |
| @activepieces/piece-bexio | Bexio | 0.2.1 | 24 | 7 |  |
| @activepieces/piece-bigcommerce | BigCommerce | 0.2.1 | 16 | 11 |  |
| @activepieces/piece-bigin-by-zoho | Bigin by Zoho CRM | 0.1.7 | 16 | 9 |  |
| @activepieces/piece-bika | Bika.ai | 0.3.0 | 7 | 0 |  |
| @activepieces/piece-billplz | Billplz | 0.0.9 | 2 | 1 |  |
| @activepieces/piece-binance | Binance | 0.5.1 | 10 | 0 |  |
| @activepieces/piece-bitly | Bitly | 0.2.0 | 6 | 1 |  |
| @activepieces/piece-blackbaud | Blackbaud | 0.3.0 | 5 | 0 |  |
| @activepieces/piece-bland-ai | Bland AI | 0.2.1 | 4 | 0 |  |
| @activepieces/piece-blockscout | Blockscout | 0.1.7 | 34 | 0 |  |
| @activepieces/piece-bloomerang | Bloomerang | 0.1.1 | 5 | 0 |  |
| @activepieces/piece-bluesky | Bluesky | 0.2.0 | 34 | 6 |  |
| @activepieces/piece-bocha-search | Bocha | 0.1.1 | 2 | 0 |  |
| @activepieces/piece-bokio | Bokio | 0.1.0 | 11 | 0 |  |
| @activepieces/piece-bolna | Bolna AI | 0.2.0 | 2 | 1 |  |
| @activepieces/piece-bonjoro | Bonjoro | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-bookedin | Bookedin | 0.2.0 | 7 | 0 |  |
| @activepieces/piece-box | Box | 0.2.1 | 1 | 3 |  |
| @activepieces/piece-brave-search | Brave Search | 0.1.0 | 2 | 0 |  |
| @activepieces/piece-brilliant-directories | Brilliant Directories | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-browse-ai | Browse AI | 0.2.0 | 4 | 2 |  |
| @activepieces/piece-browserless | Browserless | 0.2.0 | 16 | 0 |  |
| @activepieces/piece-bubble | Bubble | 0.1.8 | 5 | 0 |  |
| @activepieces/piece-buffer | Buffer | 0.1.1 | 3 | 3 |  |
| @activepieces/piece-bumpups | Bumpups | 0.2.0 | 7 | 0 |  |
| @activepieces/piece-bursty-ai | BurstyAI | 0.1.8 | 1 | 0 |  |
| @activepieces/piece-buttondown | Buttondown | 0.0.7 | 4 | 3 |  |
| @activepieces/piece-cal-com | Cal.com | 0.5.0 | 1 | 3 |  |
| @activepieces/piece-calendly | Calendly | 0.6.0 | 6 | 2 |  |
| @activepieces/piece-camb-ai | Camb.AI | 0.2.0 | 5 | 0 |  |
| @activepieces/piece-campaign-monitor | Campaign Monitor | 0.1.8 | 4 | 3 |  |
| @activepieces/piece-canny | Canny | 0.2.1 | 5 | 4 |  |
| @activepieces/piece-canva | Canva | 0.1.1 | 10 | 0 |  |
| @activepieces/piece-capsule-crm | Capsule CRM | 0.1.7 | 10 | 4 |  |
| @activepieces/piece-captain-data | Captain-data | 0.2.0 | 3 | 0 |  |
| @activepieces/piece-carbone | Carbone | 0.1.1 | 8 | 0 |  |
| @activepieces/piece-cartloom | Cartloom | 0.2.0 | 8 | 0 |  |
| @activepieces/piece-cashfree-payments | Cashfree Payments | 0.1.8 | 9 | 0 |  |
| @activepieces/piece-certopus | Certopus | 0.3.0 | 2 | 0 |  |
| @activepieces/piece-chain-aware | ChainAware.AI | 0.1.0 | 6 | 0 |  |
| @activepieces/piece-chainalysis-api | Chainalysis Screening API | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-chaindesk | Chaindesk | 0.2.0 | 4 | 0 |  |
| @activepieces/piece-chargebee | Chargebee | 0.1.1 | 5 | 8 |  |
| @activepieces/piece-chargekeep | ChargeKeep | 0.3.7 | 6 | 3 |  |
| @activepieces/piece-chartly | Chartly | 0.0.9 | 2 | 0 |  |
| @activepieces/piece-chat-aid | Chat Aid | 0.2.0 | 4 | 0 |  |
| @activepieces/piece-chat-data | Chat Data | 0.1.8 | 6 | 0 |  |
| @activepieces/piece-chatbase | Chatbase | 0.2.0 | 5 | 0 |  |
| @activepieces/piece-chatfly | Chatfly | 0.1.8 | 1 | 0 |  |
| @activepieces/piece-chatling | Chatling | 0.2.0 | 3 | 2 |  |
| @activepieces/piece-chatnode | ChatNode | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-chatsistant | Chatsistant | 0.2.0 | 2 | 1 |  |
| @activepieces/piece-chatwoot | Chatwoot | 0.1.1 | 2 | 1 |  |
| @activepieces/piece-checkout | Checkout.com | 0.1.7 | 7 | 2 |  |
| @activepieces/piece-chess-com | Chess.com | 0.0.7 | 3 | 0 |  |
| @activepieces/piece-circle | Circle | 0.2.0 | 7 | 2 |  |
| @activepieces/piece-clarifai | Clarifai | 0.4.1 | 10 | 0 |  |
| @activepieces/piece-claude | Anthropic Claude | 0.7.2 | 3 | 0 |  |
| @activepieces/piece-clay | Clay | 0.2.1 | 4 | 1 |  |
| @activepieces/piece-clearout | Clearout | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-clearoutphone | ClearoutPhone | 0.1.8 | 3 | 0 |  |
| @activepieces/piece-clicdata | Clicdata | 0.0.10 | 2 | 0 |  |
| @activepieces/piece-clickfunnels | ClickFunnels | 0.2.0 | 7 | 8 |  |
| @activepieces/piece-clicksend | ClickSend SMS | 0.2.0 | 10 | 1 |  |
| @activepieces/piece-clickup | ClickUp | 0.9.1 | 31 | 30 |  |
| @activepieces/piece-clockify | Clockify | 0.2.1 | 8 | 3 |  |
| @activepieces/piece-clockodo | Clockodo | 0.2.8 | 33 | 2 |  |
| @activepieces/piece-close | Close | 0.2.1 | 6 | 3 |  |
| @activepieces/piece-cloudconvert | CloudConvert | 0.2.0 | 7 | 3 |  |
| @activepieces/piece-cloudinary | Cloudinary | 0.2.0 | 6 | 2 |  |
| @activepieces/piece-cloutly | Cloutly | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-coda | Coda | 0.3.0 | 35 | 1 |  |
| @activepieces/piece-cody | Cody | 0.3.1 | 7 | 0 |  |
| @activepieces/piece-cognito-forms | Cognito Forms | 0.2.2 | 5 | 2 |  |
| @activepieces/piece-cohere | Cohere | 0.1.2 | 2 | 0 |  |
| @activepieces/piece-cometapi | CometAPI | 0.2.1 | 2 | 0 |  |
| @activepieces/piece-comfyicu | Comfy.ICU | 0.1.6 | 4 | 3 |  |
| @activepieces/piece-confluence | Confluence | 0.3.2 | 21 | 5 |  |
| @activepieces/piece-connections | Connections | 0.5.10 | 1 | 0 |  |
| @activepieces/piece-connectuc | ConnectUC | 0.0.12 | 6 | 8 |  |
| @activepieces/piece-constant-contact | Constant Contact | 0.3.1 | 2 | 0 |  |
| @activepieces/piece-contentful | Contentful | 0.2.1 | 4 | 0 |  |
| @activepieces/piece-contextual-ai | Contextual AI | 0.1.8 | 7 | 1 |  |
| @activepieces/piece-contiguity | Contiguity | 0.3.1 | 3 | 0 |  |
| @activepieces/piece-convertapi | ConvertAPI | 0.0.2 | 4 | 0 |  |
| @activepieces/piece-convertkit | ConvertKit | 0.4.1 | 36 | 12 |  |
| @activepieces/piece-copper | Copper | 0.2.0 | 20 | 11 |  |
| @activepieces/piece-copy-ai | Copy.ai | 0.1.6 | 3 | 1 |  |
| @activepieces/piece-coralogix | Coralogix | 0.2.2 | 10 | 2 |  |
| @activepieces/piece-couchbase | Couchbase | 0.1.7 | 5 | 0 |  |
| @activepieces/piece-coupa | Coupa | 0.1.1 | 13 | 1 |  |
| @activepieces/piece-crisp | Crisp | 0.2.1 | 7 | 2 |  |
| @activepieces/piece-crypto | Crypto | 0.0.29 | 7 | 0 |  |
| @activepieces/piece-cryptolens | Cryptolens | 0.2.0 | 5 | 1 |  |
| @activepieces/piece-csv | CSV | 0.5.0 | 12 | 0 |  |
| @activepieces/piece-cursor | Cursor | 0.1.7 | 4 | 5 |  |
| @activepieces/piece-customer-io | customer.io | 0.5.1 | 3 | 1 |  |
| @activepieces/piece-customgpt | CustomGPT | 0.1.7 | 8 | 1 |  |
| @activepieces/piece-cyberark | CyberArk | 0.1.8 | 17 | 0 |  |
| @activepieces/piece-dappier | Dappier | 0.1.7 | 4 | 0 |  |
| @activepieces/piece-dashworks | Dashworks | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-data-mapper | Data Mapper | 0.3.21 | 1 | 0 |  |
| @activepieces/piece-data-summarizer | Data Summarizer | 0.0.16 | 4 | 0 |  |
| @activepieces/piece-datadog | Datadog | 0.2.2 | 3 | 0 |  |
| @activepieces/piece-dataforb2b | DataForB2B | 0.1.1 | 7 | 0 |  |
| @activepieces/piece-datafuel | DataFuel | 0.2.0 | 4 | 0 |  |
| @activepieces/piece-date-helper | Date Helper | 0.1.36 | 9 | 0 |  |
| @activepieces/piece-datocms | Dato CMS | 0.2.0 | 1 | 0 |  |
| @activepieces/piece-deepgram | Deepgram | 0.2.0 | 5 | 0 |  |
| @activepieces/piece-deepl | DeepL | 0.2.2 | 2 | 0 |  |
| @activepieces/piece-deepseek | DeepSeek | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-deftform | Deftform | 0.1.1 | 8 | 1 |  |
| @activepieces/piece-delay | Delay | 0.3.35 | 2 | 0 |  |
| @activepieces/piece-denser-ai | Denser.ai | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-descript | Descript | 0.1.1 | 7 | 1 |  |
| @activepieces/piece-detecting-ai | DETECTING-AI.COM | 0.1.0 | 4 | 0 |  |
| @activepieces/piece-devin | Devin AI | 0.1.6 | 3 | 0 |  |
| @activepieces/piece-digital-ocean | DigitalOcean | 0.1.1 | 11 | 0 |  |
| @activepieces/piece-digital-pilot | DigitalPilot | 0.1.7 | 2 | 2 |  |
| @activepieces/piece-dimo | DIMO | 0.3.7 | 38 | 9 |  |
| @activepieces/piece-discord | Discord | 0.7.2 | 16 | 2 |  |
| @activepieces/piece-discourse | Discourse | 0.2.1 | 6 | 0 |  |
| @activepieces/piece-dittofeed | Dittofeed | 0.1.6 | 3 | 0 |  |
| @activepieces/piece-docsbot | DocsBot | 0.2.1 | 6 | 0 |  |
| @activepieces/piece-doctly | Doctly AI | 0.2.1 | 2 | 0 |  |
| @activepieces/piece-documentpro | DocumentPro | 0.2.1 | 3 | 1 |  |
| @activepieces/piece-documerge | DocuMerge | 0.1.8 | 5 | 2 |  |
| @activepieces/piece-docusign | Docusign | 0.3.3 | 8 | 11 |  |
| @activepieces/piece-drip | Drip | 0.6.0 | 33 | 10 |  |
| @activepieces/piece-dropbox | Dropbox | 0.9.2 | 14 | 1 |  |
| @activepieces/piece-drupal | Drupal | 1.1.11 | 6 | 3 |  |
| @activepieces/piece-dub | Dub | 0.1.1 | 6 | 2 |  |
| @activepieces/piece-duckdb | DuckDB | 0.0.9 | 1 | 0 |  |
| @activepieces/piece-dumpling-ai | Dumpling AI | 0.2.1 | 7 | 0 |  |
| @activepieces/piece-dust | Dust | 0.3.0 | 7 | 0 |  |
| @activepieces/piece-easy-peasy-ai | Easy-Peasy.AI | 0.2.0 | 4 | 0 |  |
| @activepieces/piece-echowin | Echowin | 0.1.7 | 3 | 1 |  |
| @activepieces/piece-eden-ai | Eden AI | 0.2.5 | 13 | 0 |  |
| @activepieces/piece-editionguard | EditionGuard | 0.2.1 | 2 | 0 |  |
| @activepieces/piece-elastic-email | Elastic Email | 0.3.1 | 11 | 0 |  |
| @activepieces/piece-elevenlabs | ElevenLabs | 0.4.0 | 2 | 0 |  |
| @activepieces/piece-emailit | Emailit | 0.1.2 | 2 | 0 |  |
| @activepieces/piece-emailoctopus | EmailOctopus | 0.2.1 | 8 | 5 |  |
| @activepieces/piece-enrichlayer | Enrich Layer | 0.1.1 | 26 | 0 |  |
| @activepieces/piece-esignatures | eSignatures | 0.2.1 | 2 | 0 |  |
| @activepieces/piece-eth-name-service | Ethereum Name Service (ENS) | 0.1.6 | 1 | 0 |  |
| @activepieces/piece-everhour | Everhour | 0.2.1 | 4 | 0 |  |
| @activepieces/piece-exa | Exa | 0.3.1 | 9 | 1 |  |
| @activepieces/piece-extracta-ai | Extracta.ai | 0.1.6 | 3 | 2 |  |
| @activepieces/piece-facebook-leads | Facebook Leads | 0.4.0 | 1 | 1 |  |
| @activepieces/piece-facebook-pages | Facebook Pages | 0.4.1 | 3 | 0 |  |
| @activepieces/piece-famulor | Famulor AI - Voice Agent | 0.2.5 | 25 | 4 |  |
| @activepieces/piece-fathom | Fathom | 0.3.0 | 11 | 1 |  |
| @activepieces/piece-fathom-analytics | Fathom Analytics | 0.1.1 | 6 | 0 |  |
| @activepieces/piece-feathery | Feathery | 0.1.7 | 5 | 3 |  |
| @activepieces/piece-feedhive | FeedHive | 0.1.1 | 8 | 2 |  |
| @activepieces/piece-fellow | Fellow.ai | 0.2.1 | 2 | 1 |  |
| @activepieces/piece-figma | Figma | 0.6.3 | 4 | 1 |  |
| @activepieces/piece-file-helper | Files Helper | 0.2.0 | 7 | 0 |  |
| @activepieces/piece-filetopdf | FileToPDF | 0.0.8 | 4 | 0 |  |
| @activepieces/piece-fillout-forms | Fillout Forms | 0.2.0 | 4 | 1 |  |
| @activepieces/piece-fireberry | Fireberry | 0.1.7 | 4 | 1 |  |
| @activepieces/piece-firecrawl | Firecrawl | 0.5.0 | 6 | 0 |  |
| @activepieces/piece-fireflies-ai | Fireflies.ai | 0.1.7 | 5 | 1 |  |
| @activepieces/piece-flipando | Flipando AI | 0.1.0 | 5 | 0 |  |
| @activepieces/piece-fliqr-ai | Fliqr AI | 0.2.1 | 3 | 0 |  |
| @activepieces/piece-floqer | Floqer | 0.1.1 | 4 | 0 |  |
| @activepieces/piece-flow-helper | Flow Helper | 0.1.8 | 3 | 0 |  |
| @activepieces/piece-flow-parser | FlowParser | 0.1.7 | 1 | 2 |  |
| @activepieces/piece-flowise | Flowise | 0.2.1 | 2 | 0 |  |
| @activepieces/piece-flowlu | Flowlu | 0.2.1 | 24 | 4 |  |
| @activepieces/piece-folk | Folk | 0.1.8 | 8 | 8 |  |
| @activepieces/piece-foreplay-co | Foreplay | 0.1.9 | 5 | 3 |  |
| @activepieces/piece-formbricks | Formbricks | 0.3.2 | 1 | 3 |  |
| @activepieces/piece-formio | Form.io | 0.1.2 | 8 | 2 |  |
| @activepieces/piece-formitable | Formitable | 0.0.8 | 0 | 16 |  |
| @activepieces/piece-forms | Human Input | 0.5.0 | 1 | 2 |  |
| @activepieces/piece-formsite | Formsite | 0.1.8 | 0 | 1 |  |
| @activepieces/piece-formspark | Formspark | 0.1.6 | 0 | 1 |  |
| @activepieces/piece-formstack | Formstack | 0.2.0 | 5 | 2 |  |
| @activepieces/piece-fountain | Fountain | 0.1.7 | 10 | 4 |  |
| @activepieces/piece-fragment | Fragment | 0.1.7 | 6 | 2 |  |
| @activepieces/piece-frame | Frame | 0.2.1 | 1 | 3 |  |
| @activepieces/piece-free-agent | FreeAgent | 0.1.8 | 2 | 4 |  |
| @activepieces/piece-freshdesk | Freshdesk | 0.3.1 | 6 | 0 |  |
| @activepieces/piece-freshsales | Freshsales | 0.5.2 | 2 | 0 |  |
| @activepieces/piece-freshservice | Freshservice | 0.2.2 | 12 | 8 |  |
| @activepieces/piece-frill | Frill | 0.1.1 | 9 | 2 |  |
| @activepieces/piece-front | Front | 0.2.2 | 21 | 5 |  |
| @activepieces/piece-gameball | Gameball | 0.1.6 | 1 | 0 |  |
| @activepieces/piece-gamma | Gamma | 0.1.9 | 2 | 0 |  |
| @activepieces/piece-gcloud-pubsub | GCloud Pub/Sub | 0.1.8 | 1 | 1 |  |
| @activepieces/piece-gender-api | Gender API | 0.1.1 | 4 | 0 |  |
| @activepieces/piece-generatebanners | GenerateBanners | 0.4.7 | 1 | 0 |  |
| @activepieces/piece-getresponse | GetResponse | 0.1.1 | 6 | 0 |  |
| @activepieces/piece-ghostcms | GhostCMS | 0.3.1 | 6 | 6 |  |
| @activepieces/piece-giftbit | Giftbit | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-gistly | Gistly | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-gitea | Gitea | 0.1.1 | 4 | 4 |  |
| @activepieces/piece-github | GitHub | 0.9.3 | 19 | 14 |  |
| @activepieces/piece-gitlab | GitLab | 0.2.1 | 2 | 1 |  |
| @activepieces/piece-gladia | Gladia | 0.2.0 | 3 | 0 |  |
| @activepieces/piece-glide | Glide | 0.1.1 | 6 | 0 |  |
| @activepieces/piece-gmail | Gmail | 0.17.4 | 11 | 4 |  |
| @activepieces/piece-goodmem | GoodMem | 0.0.7 | 5 | 0 |  |
| @activepieces/piece-google-bigquery | Google BigQuery | 0.1.1 | 10 | 4 |  |
| @activepieces/piece-google-calendar | Google Calendar | 0.12.2 | 9 | 7 |  |
| @activepieces/piece-google-cloud-storage | Google Cloud Storage | 0.1.8 | 12 | 2 |  |
| @activepieces/piece-google-contacts | Google Contacts | 0.5.3 | 4 | 1 |  |
| @activepieces/piece-google-docs | Google Docs | 0.5.3 | 6 | 1 |  |
| @activepieces/piece-google-drive | Google Drive | 0.11.2 | 17 | 3 |  |
| @activepieces/piece-google-forms | Google Forms | 0.7.1 | 1 | 1 |  |
| @activepieces/piece-google-gemini | Google Gemini | 0.4.2 | 11 | 0 |  |
| @activepieces/piece-google-my-business | Google My Business | 0.5.2 | 7 | 1 |  |
| @activepieces/piece-google-search | Google Search | 0.0.9 | 1 | 0 |  |
| @activepieces/piece-google-search-console | Google Search Console | 0.3.1 | 8 | 0 |  |
| @activepieces/piece-google-sheets | Google Sheets | 0.17.1 | 27 | 4 |  |
| @activepieces/piece-google-slides | Google Slides | 0.4.1 | 19 | 0 |  |
| @activepieces/piece-google-tasks | Google Tasks | 0.6.1 | 2 | 1 |  |
| @activepieces/piece-google-vertexai | Google Vertex AI | 0.1.7 | 3 | 0 |  |
| @activepieces/piece-googlechat | Google Chat | 0.1.8 | 6 | 2 |  |
| @activepieces/piece-gorgias | Gorgias | 0.1.0 | 7 | 0 |  |
| @activepieces/piece-gotify | Gotify | 0.4.7 | 1 | 0 |  |
| @activepieces/piece-gptzero-detect-ai | GPTZero | 0.1.7 | 2 | 0 |  |
| @activepieces/piece-granola | Granola | 0.1.1 | 3 | 2 |  |
| @activepieces/piece-graphql | GraphQL | 0.0.20 | 1 | 0 |  |
| @activepieces/piece-gravityforms | Gravity Forms | 0.1.7 | 0 | 1 |  |
| @activepieces/piece-greenhouse | Greenhouse | 0.1.0 | 8 | 6 |  |
| @activepieces/piece-greenpt | GreenPT | 0.2.1 | 4 | 0 |  |
| @activepieces/piece-greip | Greip | 0.1.8 | 6 | 5 |  |
| @activepieces/piece-griptape | Griptape Cloud | 0.2.0 | 5 | 4 |  |
| @activepieces/piece-grist | Grist | 0.3.0 | 5 | 2 |  |
| @activepieces/piece-grok-xai | Grok by xAI | 0.2.1 | 5 | 0 |  |
| @activepieces/piece-groq | Groq | 0.4.1 | 4 | 0 |  |
| @activepieces/piece-guidelite | GuideLite | 0.2.0 | 2 | 1 |  |
| @activepieces/piece-hackernews | Hacker News | 0.5.0 | 2 | 0 |  |
| @activepieces/piece-harvest | Harvest | 0.2.0 | 11 | 0 |  |
| @activepieces/piece-hashi-corp-vault | HashiCorp Vault | 0.1.0 | 5 | 0 |  |
| @activepieces/piece-hastewire | Hastewire | 0.1.7 | 2 | 0 |  |
| @activepieces/piece-heartbeat | Heartbeat | 0.3.0 | 45 | 5 |  |
| @activepieces/piece-hedy | Hedy | 0.2.5 | 19 | 5 |  |
| @activepieces/piece-help-scout | Help Scout | 0.2.1 | 9 | 4 |  |
| @activepieces/piece-heygen | HeyGen | 0.2.0 | 10 | 2 |  |
| @activepieces/piece-heymarket-sms | Heymarket SMS | 0.1.0 | 5 | 2 |  |
| @activepieces/piece-hootsuite | Hootsuite | 0.1.0 | 4 | 2 |  |
| @activepieces/piece-housecall-pro | Housecall Pro | 0.2.0 | 46 | 0 |  |
| @activepieces/piece-http | HTTP | 0.12.2 | 2 | 0 |  |
| @activepieces/piece-http-oauth2 | HTTP (OAuth2) | 0.3.1 | 1 | 0 |  |
| @activepieces/piece-hubspot | HubSpot | 0.12.1 | 45 | 24 |  |
| @activepieces/piece-hugging-face | Hugging Face | 0.3.1 | 8 | 0 |  |
| @activepieces/piece-hume-ai | Hume AI | 0.1.8 | 6 | 1 |  |
| @activepieces/piece-hunter | Hunter | 0.1.7 | 9 | 1 |  |
| @activepieces/piece-hystruct | Hystruct | 0.1.7 | 1 | 1 |  |
| @activepieces/piece-ibm-cognose | IBM Cognos Analytics | 0.2.0 | 9 | 0 |  |
| @activepieces/piece-iloveapi | iLoveAPI | 0.0.6 | 22 | 11 |  |
| @activepieces/piece-image-helper | Image Helper | 0.1.22 | 7 | 0 |  |
| @activepieces/piece-image-router | ImageRouter | 0.1.8 | 2 | 0 |  |
| @activepieces/piece-imap | IMAP | 0.6.2 | 4 | 1 |  |
| @activepieces/piece-imeetify | iMeetify | 0.0.5 | 0 | 1 |  |
| @activepieces/piece-influencers-club | Influencers.club | 0.1.0 | 4 | 0 |  |
| @activepieces/piece-insightly | Insightly | 0.1.7 | 5 | 3 |  |
| @activepieces/piece-insighto-ai | Insighto.ai | 0.1.7 | 4 | 3 |  |
| @activepieces/piece-insta-charts | InstaCharts | 0.0.8 | 1 | 0 |  |
| @activepieces/piece-instabase | Instabase | 0.2.0 | 3 | 1 |  |
| @activepieces/piece-instagram-business | Instagram for Business | 1.0.2 | 27 | 0 |  |
| @activepieces/piece-instantly-ai | Instantly.ai | 0.2.1 | 6 | 2 |  |
| @activepieces/piece-instasent | Instasent | 0.1.7 | 3 | 0 |  |
| @activepieces/piece-intercom | Intercom | 0.8.3 | 26 | 22 |  |
| @activepieces/piece-intruder | Intruder | 0.1.0 | 6 | 0 |  |
| @activepieces/piece-invoiceninja | Invoice Ninja | 0.4.1 | 10 | 0 |  |
| @activepieces/piece-jina-ai | Jina AI | 0.2.0 | 6 | 0 |  |
| @activepieces/piece-jira-cloud | Jira Cloud | 0.5.2 | 17 | 9 |  |
| @activepieces/piece-jira-data-center | Jira Data Center | 0.1.1 | 15 | 3 |  |
| @activepieces/piece-jogg-ai | JoggAI | 0.1.7 | 8 | 2 |  |
| @activepieces/piece-jotform | Jotform | 0.5.2 | 1 | 1 |  |
| @activepieces/piece-jsm-operations | Jira Service Management Operations | 0.0.1 | 16 | 1 |  |
| @activepieces/piece-json | JSON | 0.1.13 | 4 | 0 |  |
| @activepieces/piece-jungle-grid | Jungle Grid | 0.2.1 | 10 | 0 |  |
| @activepieces/piece-just-invoice | JustInvoice | 0.0.8 | 6 | 0 |  |
| @activepieces/piece-kallabot-ai | Kallabot | 0.4.7 | 8 | 1 |  |
| @activepieces/piece-kapso | Kapso | 0.2.0 | 15 | 2 |  |
| @activepieces/piece-katana | Katana | 0.2.0 | 4 | 0 |  |
| @activepieces/piece-kimai | Kimai | 0.3.1 | 2 | 0 |  |
| @activepieces/piece-kissflow | Kissflow | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-kizeo-forms | Kizeo Forms | 0.5.1 | 11 | 6 |  |
| @activepieces/piece-klaviyo | Klaviyo | 0.2.1 | 11 | 2 |  |
| @activepieces/piece-klenty | Klenty | 0.1.0 | 5 | 0 |  |
| @activepieces/piece-klipy | Klipy | 0.1.0 | 4 | 0 |  |
| @activepieces/piece-knack | Knack | 0.2.1 | 5 | 0 |  |
| @activepieces/piece-knock | Knock | 0.2.0 | 7 | 0 |  |
| @activepieces/piece-ko-fi | Ko-fi | 0.0.5 | 0 | 4 |  |
| @activepieces/piece-kommo | Kommo | 0.2.1 | 8 | 4 |  |
| @activepieces/piece-krisp-call | KrispCall | 0.1.7 | 4 | 5 |  |
| @activepieces/piece-kudosity | Kudosity | 0.2.0 | 7 | 3 |  |
| @activepieces/piece-kustomer | Kustomer | 0.1.0 | 6 | 0 |  |
| @activepieces/piece-lead-connector | LeadConnector | 0.4.1 | 11 | 4 |  |
| @activepieces/piece-leap-ai | Leap AI | 0.0.8 | 2 | 0 |  |
| @activepieces/piece-leexi | Leexi | 0.2.1 | 2 | 1 |  |
| @activepieces/piece-lemlist | Lemlist | 0.1.11 | 13 | 2 |  |
| @activepieces/piece-lemon-squeezy | Lemon Squeezy | 0.2.0 | 7 | 16 |  |
| @activepieces/piece-letmepost | Letmepost | 0.1.1 | 5 | 2 |  |
| @activepieces/piece-lets-calendar | Let's Calendar | 0.1.0 | 2 | 1 |  |
| @activepieces/piece-letta | Letta | 0.1.8 | 4 | 2 |  |
| @activepieces/piece-lever | Lever | 0.2.0 | 6 | 0 |  |
| @activepieces/piece-lightfunnels | Lightfunnels | 0.1.7 | 10 | 2 |  |
| @activepieces/piece-line | Line Bot | 0.2.1 | 2 | 1 |  |
| @activepieces/piece-linear | Linear | 0.9.1 | 13 | 8 |  |
| @activepieces/piece-linka | Linka | 0.1.6 | 6 | 3 |  |
| @activepieces/piece-linkedin | LinkedIn | 0.5.1 | 3 | 0 |  |
| @activepieces/piece-linkup | Linkup | 0.1.7 | 2 | 0 |  |
| @activepieces/piece-linkupapi | LinkupAPI | 0.1.0 | 12 | 2 |  |
| @activepieces/piece-livesession | LiveSession | 0.1.0 | 1 | 1 |  |
| @activepieces/piece-llmrails | LLMRails | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-lobstermail | LobsterMail | 0.2.1 | 10 | 5 |  |
| @activepieces/piece-localai | LocalAI | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-lofty | Lofty | 0.2.1 | 5 | 0 |  |
| @activepieces/piece-logrocket | LogRocket | 0.1.7 | 2 | 1 |  |
| @activepieces/piece-logsnag | LogSnag | 0.1.1 | 2 | 1 |  |
| @activepieces/piece-lokalise | Lokalise | 0.1.0 | 12 | 3 |  |
| @activepieces/piece-loops | Loops | 0.1.1 | 6 | 0 |  |
| @activepieces/piece-lucidya | Lucidya | 0.0.8 | 0 | 1 |  |
| @activepieces/piece-lusha | Lusha | 0.2.0 | 3 | 0 |  |
| @activepieces/piece-luxury-presence | Luxury Presence | 0.1.7 | 0 | 1 |  |
| @activepieces/piece-magical-api | Magical API | 0.2.1 | 6 | 0 |  |
| @activepieces/piece-magicslides | MagicSlides | 0.1.7 | 3 | 0 |  |
| @activepieces/piece-mailchain | Mailchain | 0.1.6 | 2 | 0 |  |
| @activepieces/piece-mailchimp | Mailchimp | 0.5.10 | 17 | 9 |  |
| @activepieces/piece-mailer-lite | MailerLite | 0.9.1 | 11 | 4 |  |
| @activepieces/piece-mailercheck | Mailercheck | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-maileroo | Maileroo | 0.3.0 | 4 | 0 |  |
| @activepieces/piece-mailgun | Mailgun | 0.1.0 | 9 | 8 |  |
| @activepieces/piece-mailjet | Mailjet | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-manual-trigger | Manual Trigger | 0.0.8 | 0 | 1 |  |
| @activepieces/piece-manus | Manus | 0.2.0 | 5 | 2 |  |
| @activepieces/piece-manychat | Manychat | 0.1.7 | 7 | 0 |  |
| @activepieces/piece-mastodon | Mastodon | 0.8.1 | 14 | 4 |  |
| @activepieces/piece-math-helper | Math Helper | 0.1.0 | 6 | 0 |  |
| @activepieces/piece-matomo | Matomo | 0.2.1 | 2 | 0 |  |
| @activepieces/piece-matrix | Matrix | 0.5.1 | 2 | 0 |  |
| @activepieces/piece-mattermost | Mattermost | 0.5.1 | 2 | 0 |  |
| @activepieces/piece-mautic | Mautic | 0.6.1 | 7 | 4 |  |
| @activepieces/piece-mcp | MCP | 0.0.21 | 1 | 1 |  |
| @activepieces/piece-mcp-client | MCP Client | 0.0.5 | 1 | 0 |  |
| @activepieces/piece-medullar | Medullar | 0.3.7 | 6 | 0 |  |
| @activepieces/piece-meetgeek-ai | Meetgeek | 0.1.7 | 6 | 1 |  |
| @activepieces/piece-meistertask | MeisterTask | 0.2.2 | 13 | 9 |  |
| @activepieces/piece-mem | Mem | 0.2.1 | 4 | 0 |  |
| @activepieces/piece-mempool-space | Mempool | 0.2.0 | 35 | 0 |  |
| @activepieces/piece-messagebird | Bird | 0.3.1 | 3 | 0 |  |
| @activepieces/piece-metabase | Metabase | 0.3.1 | 6 | 0 |  |
| @activepieces/piece-metatext | Metatext | 0.1.7 | 3 | 0 |  |
| @activepieces/piece-microsoft-365-people | Microsoft 365 People | 0.3.1 | 7 | 1 |  |
| @activepieces/piece-microsoft-365-planner | Microsoft 365 Planner | 0.3.2 | 12 | 3 |  |
| @activepieces/piece-microsoft-copilot | Microsoft 365 Copilot | 0.2.2 | 3 | 0 |  |
| @activepieces/piece-microsoft-dynamics-365-business-central | Microsoft Dynamics 365 Business Central | 0.3.0 | 6 | 1 |  |
| @activepieces/piece-microsoft-dynamics-crm | Microsoft Dynamics CRM | 0.4.1 | 5 | 0 |  |
| @activepieces/piece-microsoft-excel-365 | Microsoft Excel 365 | 0.8.2 | 33 | 4 |  |
| @activepieces/piece-microsoft-onedrive | Microsoft OneDrive | 0.6.1 | 6 | 1 |  |
| @activepieces/piece-microsoft-onenote | Microsoft OneNote | 0.4.2 | 7 | 1 |  |
| @activepieces/piece-microsoft-outlook | Microsoft Outlook | 0.7.2 | 12 | 3 |  |
| @activepieces/piece-microsoft-outlook-calendar | Microsoft Outlook Calendar | 0.3.1 | 4 | 0 |  |
| @activepieces/piece-microsoft-power-bi | Microsoft Power BI | 0.4.2 | 9 | 0 |  |
| @activepieces/piece-microsoft-sharepoint | Microsoft SharePoint | 0.4.2 | 16 | 8 |  |
| @activepieces/piece-microsoft-sql-server | Microsoft SQL Server | 0.1.0 | 7 | 1 |  |
| @activepieces/piece-microsoft-teams | Microsoft Teams | 0.7.2 | 16 | 4 |  |
| @activepieces/piece-microsoft-teams-bot | Microsoft Teams Bot | 0.1.0 | 1 | 0 |  |
| @activepieces/piece-microsoft-todo | Microsoft To Do | 0.5.1 | 13 | 4 |  |
| @activepieces/piece-millionverifier | MillionVerifier | 0.1.8 | 1 | 0 |  |
| @activepieces/piece-mind-studio | MindStudio | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-mindee | Mindee | 0.3.1 | 2 | 0 |  |
| @activepieces/piece-missive | Missive | 0.2.0 | 6 | 5 |  |
| @activepieces/piece-mistral-ai | Mistral AI | 0.4.0 | 6 | 0 |  |
| @activepieces/piece-mixmax | Mixmax | 0.1.0 | 6 | 0 |  |
| @activepieces/piece-mixpanel | Mixpanel | 0.2.1 | 2 | 0 |  |
| @activepieces/piece-modelslab | ModelsLab | 0.0.5 | 1 | 0 |  |
| @activepieces/piece-mollie | Mollie | 0.1.6 | 8 | 7 |  |
| @activepieces/piece-monday | monday.com | 0.4.0 | 9 | 2 |  |
| @activepieces/piece-mongodb | MongoDB | 0.1.7 | 7 | 0 |  |
| @activepieces/piece-moonclerk | Moonclerk | 0.1.0 | 2 | 5 |  |
| @activepieces/piece-mooninvoice | Moon Invoice | 0.0.9 | 7 | 0 |  |
| @activepieces/piece-motion | Motion | 0.2.1 | 7 | 1 |  |
| @activepieces/piece-motiontools | MotionTools | 0.1.7 | 2 | 5 |  |
| @activepieces/piece-moveo-ai | Moveo | 0.1.0 | 1 | 2 |  |
| @activepieces/piece-moxie-crm | Moxie | 0.4.0 | 45 | 32 |  |
| @activepieces/piece-muna-ai | Muna | 0.1.0 | 2 | 0 |  |
| @activepieces/piece-murf-api | Murf AI | 0.2.1 | 5 | 0 |  |
| @activepieces/piece-mycase-piece | MyCase | 0.1.7 | 37 | 5 |  |
| @activepieces/piece-mysendingbox | Mysendingbox | 0.1.0 | 1 | 0 |  |
| @activepieces/piece-mysql | MySQL | 0.3.0 | 7 | 0 |  |
| @activepieces/piece-netlify | Netlify | 0.1.7 | 4 | 4 |  |
| @activepieces/piece-netsuite | NetSuite | 0.2.1 | 5 | 0 |  |
| @activepieces/piece-neverbounce | NeverBounce | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-nifty | Nifty | 0.3.0 | 17 | 3 |  |
| @activepieces/piece-ninety | Ninety | 0.1.0 | 14 | 3 |  |
| @activepieces/piece-ninjapipe | NinjaPipe | 0.1.1 | 51 | 8 |  |
| @activepieces/piece-ninox | Ninox | 0.2.0 | 8 | 1 |  |
| @activepieces/piece-nocodb | NocoDB | 0.5.0 | 5 | 0 |  |
| @activepieces/piece-notion | Notion | 0.7.5 | 15 | 4 |  |
| @activepieces/piece-ntfy | ntfy | 0.4.1 | 8 | 1 |  |
| @activepieces/piece-nuelink | Nuelink | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-octopush-sms | Octopush SMS | 0.2.0 | 3 | 0 |  |
| @activepieces/piece-odoo | Odoo | 0.3.1 | 15 | 5 |  |
| @activepieces/piece-okta | Okta | 0.2.0 | 10 | 1 |  |
| @activepieces/piece-omni-co | Omni | 0.2.0 | 9 | 0 |  |
| @activepieces/piece-omnihr | Omni HR | 0.2.1 | 6 | 0 |  |
| @activepieces/piece-omnisend | Omnisend | 0.1.0 | 6 | 0 |  |
| @activepieces/piece-oncehub | Oncehub | 0.2.1 | 3 | 9 |  |
| @activepieces/piece-oneclickimpact | 1ClickImpact | 0.1.0 | 5 | 0 |  |
| @activepieces/piece-onfleet | Onfleet | 0.2.0 | 33 | 18 |  |
| @activepieces/piece-open-phone | OpenPhone | 0.1.7 | 4 | 5 |  |
| @activepieces/piece-open-router | OpenRouter | 0.3.0 | 9 | 0 |  |
| @activepieces/piece-openai | OpenAI | 0.12.2 | 19 | 0 |  |
| @activepieces/piece-openmic-ai | OpenMic AI | 0.2.0 | 6 | 1 |  |
| @activepieces/piece-opnform | Opnform | 0.2.1 | 1 | 1 |  |
| @activepieces/piece-opportify | Opportify | 0.1.7 | 2 | 0 |  |
| @activepieces/piece-oracle-database | Oracle Database | 0.1.15 | 6 | 1 |  |
| @activepieces/piece-oracle-fusion-cloud-erp | Oracle Fusion Cloud ERP | 0.1.1 | 23 | 0 |  |
| @activepieces/piece-orimon | Orimon | 0.2.0 | 2 | 1 |  |
| @activepieces/piece-outseta | Outseta | 0.3.1 | 44 | 6 |  |
| @activepieces/piece-paddle | Paddle | 0.1.0 | 6 | 5 |  |
| @activepieces/piece-pagerduty | PagerDuty | 0.2.0 | 6 | 3 |  |
| @activepieces/piece-pandadoc | PandaDoc | 0.2.1 | 8 | 3 |  |
| @activepieces/piece-paperform | Paperform | 0.2.0 | 14 | 2 |  |
| @activepieces/piece-parallel | Parallel | 0.1.1 | 9 | 0 |  |
| @activepieces/piece-parser-expert | Parser Expert | 0.1.7 | 2 | 0 |  |
| @activepieces/piece-parseur | Parseur | 0.2.1 | 6 | 5 |  |
| @activepieces/piece-pastebin | Pastebin | 0.2.8 | 2 | 0 |  |
| @activepieces/piece-pastefy | Pastefy | 0.3.1 | 9 | 1 |  |
| @activepieces/piece-paywhirl | Paywhirl | 0.1.0 | 6 | 0 |  |
| @activepieces/piece-pdf | PDF | 0.6.0 | 9 | 0 |  |
| @activepieces/piece-pdf-co | PDF.co | 0.2.0 | 34 | 0 |  |
| @activepieces/piece-pdf4me | PDF4me | 0.1.0 | 8 | 0 |  |
| @activepieces/piece-pdfcrowd | Pdfcrowd | 0.2.1 | 3 | 0 |  |
| @activepieces/piece-pdfmonkey | PDFMonkey | 0.2.1 | 4 | 1 |  |
| @activepieces/piece-peekshot | PeekShot | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-pendo | Pendo | 0.2.0 | 5 | 0 |  |
| @activepieces/piece-perplexity-ai | Perplexity AI | 0.4.1 | 1 | 0 |  |
| @activepieces/piece-personal-ai | Personal AI | 0.1.7 | 10 | 0 |  |
| @activepieces/piece-phantombuster | PhantomBuster | 0.2.0 | 2 | 1 |  |
| @activepieces/piece-phone-validator | Phone Validator | 0.0.8 | 1 | 0 |  |
| @activepieces/piece-photoroom | Photoroom | 0.1.8 | 1 | 0 |  |
| @activepieces/piece-pinch-payments | Pinch Payments | 0.0.11 | 8 | 14 |  |
| @activepieces/piece-pinecone | Pinecone | 0.1.7 | 7 | 0 |  |
| @activepieces/piece-pinterest | Pinterest | 0.2.2 | 6 | 3 |  |
| @activepieces/piece-pipedrive | Pipedrive | 0.10.2 | 30 | 14 |  |
| @activepieces/piece-placid | Placid | 0.2.0 | 8 | 0 |  |
| @activepieces/piece-plausible | Plausible Analytics | 0.2.0 | 20 | 1 |  |
| @activepieces/piece-plunk | Plunk | 0.1.0 | 5 | 0 |  |
| @activepieces/piece-pocketbase | Pocketbase | 0.0.6 | 6 | 0 |  |
| @activepieces/piece-podio | Podio | 0.2.2 | 10 | 6 |  |
| @activepieces/piece-pollybot-ai | PollyBot AI | 0.2.0 | 5 | 1 |  |
| @activepieces/piece-polydoc | PolyDoc | 0.1.1 | 4 | 0 |  |
| @activepieces/piece-poper | Poper | 0.2.7 | 0 | 1 |  |
| @activepieces/piece-postgres | Postgres | 0.4.1 | 7 | 1 |  |
| @activepieces/piece-posthog | PostHog | 0.6.1 | 5 | 1 |  |
| @activepieces/piece-postiz | Postiz | 0.1.1 | 9 | 1 |  |
| @activepieces/piece-postmark | Postmark | 0.1.1 | 5 | 0 |  |
| @activepieces/piece-predict-leads | PredictLeads | 0.2.0 | 12 | 0 |  |
| @activepieces/piece-predis-ai | Predis.ai | 0.0.8 | 1 | 1 |  |
| @activepieces/piece-presentation | Presenton | 0.3.0 | 2 | 1 |  |
| @activepieces/piece-productboard | Productboard | 0.1.8 | 4 | 3 |  |
| @activepieces/piece-produktly | Produktly | 0.1.0 | 15 | 4 |  |
| @activepieces/piece-promotekit | PromoteKit | 0.4.0 | 14 | 3 |  |
| @activepieces/piece-prompthub | PromptHub | 0.2.1 | 4 | 0 |  |
| @activepieces/piece-promptmate | PromptMate | 0.2.0 | 9 | 1 |  |
| @activepieces/piece-provenexpert | ProvenExpert | 0.1.0 | 6 | 0 |  |
| @activepieces/piece-proxycurl | Proxycurl | 0.1.4 | 5 | 0 |  |
| @activepieces/piece-pubrio | Pubrio | 0.1.1 | 28 | 1 |  |
| @activepieces/piece-pushbullet | Pushbullet | 0.2.0 | 3 | 0 |  |
| @activepieces/piece-pushover | Pushover | 0.2.10 | 1 | 0 |  |
| @activepieces/piece-pylon | Pylon | 0.2.0 | 1 | 0 |  |
| @activepieces/piece-qawafel | Qawafel | 0.1.0 | 15 | 8 |  |
| @activepieces/piece-qdrant | Qdrant | 0.3.7 | 7 | 0 |  |
| @activepieces/piece-qrcode | QR Code | 0.0.18 | 1 | 0 |  |
| @activepieces/piece-quaderno | Quaderno | 0.1.0 | 5 | 0 |  |
| @activepieces/piece-queue | Queue | 0.2.0 | 5 | 0 |  |
| @activepieces/piece-quickbase | Quickbase | 0.2.0 | 7 | 2 |  |
| @activepieces/piece-quickbooks | Quickbooks Online | 0.3.3 | 13 | 8 |  |
| @activepieces/piece-quickbooks-desktop-conductor | QuickBooks Desktop (via Conductor) | 0.1.1 | 8 | 2 |  |
| @activepieces/piece-quickbooks-sandbox | QuickBooks Online (Sandbox) | 0.2.1 | 13 | 8 |  |
| @activepieces/piece-quickzu | Quickzu | 0.1.7 | 15 | 1 |  |
| @activepieces/piece-quizell | Quizell | 0.1.0 | 8 | 0 |  |
| @activepieces/piece-qwilr | Qwilr | 0.2.0 | 2 | 7 |  |
| @activepieces/piece-rabbitmq | RabbitMQ | 0.1.7 | 2 | 1 |  |
| @activepieces/piece-raia-ai | raia | 0.2.0 | 3 | 0 |  |
| @activepieces/piece-raindrop | Raindrop | 0.1.1 | 6 | 0 |  |
| @activepieces/piece-rapidtext-ai | RapidText AI | 0.1.7 | 2 | 0 |  |
| @activepieces/piece-razorpay | Razorpay | 0.2.1 | 2 | 0 |  |
| @activepieces/piece-reachinbox | Reachinbox | 0.2.1 | 13 | 7 |  |
| @activepieces/piece-readwise | Readwise | 0.2.0 | 3 | 1 |  |
| @activepieces/piece-recall-ai | Recall.ai | 0.2.0 | 4 | 0 |  |
| @activepieces/piece-recurly | Recurly | 0.1.0 | 5 | 0 |  |
| @activepieces/piece-reddit | Reddit | 0.4.0 | 10 | 0 |  |
| @activepieces/piece-rendex | Rendex | 0.1.1 | 2 | 0 |  |
| @activepieces/piece-reoon-verifier | Reoon Email Verifier | 0.2.1 | 3 | 0 |  |
| @activepieces/piece-reply-io | Reply.io | 0.2.0 | 10 | 0 |  |
| @activepieces/piece-resend | Resend | 0.5.2 | 22 | 1 |  |
| @activepieces/piece-respaid | Respaid | 0.1.7 | 4 | 10 |  |
| @activepieces/piece-respond-io | Respond.io | 0.2.0 | 9 | 7 |  |
| @activepieces/piece-retable | Retable | 0.2.0 | 7 | 0 |  |
| @activepieces/piece-retell-ai | Retell AI | 0.2.1 | 7 | 1 |  |
| @activepieces/piece-retune | re:tune | 0.2.1 | 2 | 0 |  |
| @activepieces/piece-returning-ai | Returning AI | 0.2.5 | 3 | 0 |  |
| @activepieces/piece-ringcentral | RingCentral | 0.1.1 | 8 | 3 |  |
| @activepieces/piece-robolly | Robolly | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-roe-ai | Roe AI | 0.1.0 | 3 | 0 |  |
| @activepieces/piece-rounded-studio | Call-rounded | 0.3.0 | 1 | 0 |  |
| @activepieces/piece-rss | RSS Feed | 0.7.0 | 0 | 2 |  |
| @activepieces/piece-runware | Runware | 0.1.7 | 4 | 0 |  |
| @activepieces/piece-runway | Runway | 0.1.7 | 4 | 0 |  |
| @activepieces/piece-saastic | Saastic | 0.2.1 | 3 | 0 |  |
| @activepieces/piece-sage-accounting | Sage Accounting | 0.0.1 | 30 | 8 |  |
| @activepieces/piece-saleor | Saleor | 0.1.6 | 3 | 0 |  |
| @activepieces/piece-salesforce | Salesforce | 0.9.3 | 27 | 9 |  |
| @activepieces/piece-salesloft | Salesloft | 0.1.0 | 8 | 0 |  |
| @activepieces/piece-salsa | Salsa | 0.1.2 | 3 | 0 |  |
| @activepieces/piece-sap-ariba | SAP Ariba | 0.0.8 | 14 | 0 |  |
| @activepieces/piece-sardis | Sardis | 0.2.0 | 6 | 0 |  |
| @activepieces/piece-savvycal | SavvyCal | 0.2.1 | 15 | 3 |  |
| @activepieces/piece-scenario | Scenario | 0.2.0 | 1 | 0 |  |
| @activepieces/piece-schedule | Schedule | 0.1.22 | 0 | 6 | [piece-schedule](piece-schedule.md) |
| @activepieces/piece-scrapegrapghai | ScrapeGraphAI | 0.2.1 | 4 | 0 |  |
| @activepieces/piece-scrapeless | Scrapeless | 0.2.1 | 6 | 0 |  |
| @activepieces/piece-seek-table | SeekTable | 0.0.9 | 2 | 2 |  |
| @activepieces/piece-segment | Segment | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-send-it | SendIt | 0.2.0 | 8 | 3 |  |
| @activepieces/piece-sender | Sender | 0.1.7 | 7 | 7 |  |
| @activepieces/piece-sendfox | SendFox | 0.2.0 | 4 | 0 |  |
| @activepieces/piece-sendgrid | SendGrid | 0.6.3 | 8 | 0 |  |
| @activepieces/piece-sendinblue | Brevo | 0.4.2 | 7 | 8 |  |
| @activepieces/piece-sendpulse | SendPulse | 0.2.1 | 6 | 3 |  |
| @activepieces/piece-sendr | Sendr | 0.1.0 | 19 | 4 |  |
| @activepieces/piece-sendy | Sendy | 0.1.7 | 10 | 0 |  |
| @activepieces/piece-senja | Senja | 0.2.0 | 6 | 1 |  |
| @activepieces/piece-serp-api | SerpApi | 0.1.10 | 4 | 0 |  |
| @activepieces/piece-serpstat | Serpstat | 0.2.0 | 3 | 0 |  |
| @activepieces/piece-service-now | ServiceNow | 0.3.1 | 17 | 3 |  |
| @activepieces/piece-sessions-us | Sessions.us | 0.2.1 | 4 | 13 |  |
| @activepieces/piece-seven | seven | 0.1.8 | 4 | 1 |  |
| @activepieces/piece-sftp | FTP/SFTP | 0.5.10 | 8 | 1 |  |
| @activepieces/piece-shippo | Shippo | 0.1.7 | 3 | 2 |  |
| @activepieces/piece-shopify | Shopify | 0.9.1 | 27 | 6 |  |
| @activepieces/piece-short-io | Short.io | 0.2.0 | 10 | 1 |  |
| @activepieces/piece-sign-now | SignNow | 0.0.7 | 8 | 5 |  |
| @activepieces/piece-signrequest | Signrequest | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-simplepdf | SimplePDF | 1.1.7 | 0 | 1 |  |
| @activepieces/piece-simpliroute | SimpliRoute | 0.2.0 | 35 | 0 |  |
| @activepieces/piece-simplybookme | SimplyBook.me | 0.1.7 | 10 | 6 |  |
| @activepieces/piece-simplyprint | SimplyPrint | 0.6.7 | 63 | 62 |  |
| @activepieces/piece-sitespeakai | SiteSpeakAI | 0.1.6 | 3 | 1 |  |
| @activepieces/piece-skyprep | SkyPrep | 0.0.9 | 3 | 3 |  |
| @activepieces/piece-skyvern | Skyvern | 0.2.1 | 6 | 0 |  |
| @activepieces/piece-slack | Slack | 0.21.1 | 29 | 14 | [piece-slack](piece-slack.md) |
| @activepieces/piece-slashed | SlashedCloud | 0.1.0 | 2 | 0 |  |
| @activepieces/piece-slidespeak | SlideSpeak | 0.2.0 | 5 | 1 |  |
| @activepieces/piece-slite | Slite | 0.1.0 | 9 | 0 |  |
| @activepieces/piece-smaily | Smaily | 0.2.0 | 3 | 0 |  |
| @activepieces/piece-smartlead | SmartLead | 0.1.1 | 5 | 0 |  |
| @activepieces/piece-smartsheet | Smartsheet | 0.1.9 | 6 | 4 |  |
| @activepieces/piece-smartsuite | SmartSuite | 0.2.0 | 7 | 2 |  |
| @activepieces/piece-smoove | Smoove | 0.1.7 | 4 | 4 |  |
| @activepieces/piece-smsmode | smsmode | 0.1.0 | 2 | 0 |  |
| @activepieces/piece-smtp | SMTP | 0.5.0 | 1 | 0 |  |
| @activepieces/piece-snowflake | Snowflake | 0.3.6 | 14 | 5 |  |
| @activepieces/piece-soap | SOAP | 0.1.6 | 1 | 0 |  |
| @activepieces/piece-socialkit | Socialkit | 0.2.0 | 5 | 0 |  |
| @activepieces/piece-softr | Softr | 0.2.1 | 7 | 1 |  |
| @activepieces/piece-sofya | Sofya | 0.1.0 | 5 | 0 |  |
| @activepieces/piece-sperse | Sperse | 0.1.7 | 6 | 3 |  |
| @activepieces/piece-splitwise | Splitwise | 0.1.7 | 1 | 1 |  |
| @activepieces/piece-spotify | Spotify | 0.6.1 | 15 | 1 |  |
| @activepieces/piece-square | Square | 0.4.7 | 0 | 7 |  |
| @activepieces/piece-stability-ai | Stability AI | 0.3.1 | 2 | 0 |  |
| @activepieces/piece-stable-diffusion-webui | Stable Dffusion web UI | 0.1.6 | 1 | 0 |  |
| @activepieces/piece-store | Storage | 0.6.20 | 6 | 0 | [piece-store](piece-store.md) |
| @activepieces/piece-strale | Strale | 0.2.0 | 5 | 0 |  |
| @activepieces/piece-streak | Streak | 0.1.1 | 11 | 11 |  |
| @activepieces/piece-stripe | Stripe | 0.8.1 | 19 | 13 |  |
| @activepieces/piece-subflows | Sub Flows | 0.7.0 | 3 | 1 |  |
| @activepieces/piece-supabase | Supabase | 0.4.1 | 22 | 1 |  |
| @activepieces/piece-supadata | Supadata | 0.2.0 | 2 | 0 |  |
| @activepieces/piece-surrealdb | SurrealDB | 0.1.7 | 1 | 1 |  |
| @activepieces/piece-surveymonkey | SurveyMonkey | 0.2.0 | 1 | 1 |  |
| @activepieces/piece-surveytale | SurveyTale | 0.1.0 | 1 | 3 |  |
| @activepieces/piece-swarmnode | SwarmNode | 0.2.0 | 3 | 0 |  |
| @activepieces/piece-synthesia | Synthesia | 0.1.7 | 2 | 1 |  |
| @activepieces/piece-systeme-io | Systeme.io | 0.2.1 | 15 | 6 |  |
| @activepieces/piece-tableau | Tableau | 0.1.6 | 5 | 9 |  |
| @activepieces/piece-tables | Tables | 0.5.2 | 9 | 3 |  |
| @activepieces/piece-tags | Tags | 0.0.23 | 1 | 0 |  |
| @activepieces/piece-talkable | Talkable | 0.3.1 | 14 | 0 |  |
| @activepieces/piece-tally | Tally | 0.6.2 | 1 | 1 |  |
| @activepieces/piece-tapfiliate | Tapfiliate | 0.2.0 | 5 | 0 |  |
| @activepieces/piece-tarvent | Tarvent | 0.1.8 | 18 | 17 |  |
| @activepieces/piece-taskade | Taskade | 0.2.2 | 4 | 0 |  |
| @activepieces/piece-tavily | Tavily | 0.3.1 | 3 | 0 |  |
| @activepieces/piece-teable | Teable | 0.2.0 | 7 | 0 |  |
| @activepieces/piece-teamhood | Teamhood | 0.1.0 | 8 | 3 |  |
| @activepieces/piece-teamleader | Teamleader | 0.2.0 | 13 | 5 |  |
| @activepieces/piece-teamwork | Teamwork | 0.1.7 | 18 | 7 |  |
| @activepieces/piece-telegram-bot | Telegram Bot | 0.8.1 | 20 | 1 |  |
| @activepieces/piece-telnyx | Telnyx | 0.1.0 | 3 | 1 |  |
| @activepieces/piece-tenzo | Tenzo | 0.0.8 | 0 | 3 |  |
| @activepieces/piece-text-helper | Text Helper | 0.6.6 | 12 | 0 |  |
| @activepieces/piece-textcortex-ai | TextCortex AI | 0.2.1 | 9 | 0 |  |
| @activepieces/piece-thankster | Thankster | 0.1.8 | 1 | 0 |  |
| @activepieces/piece-ticktick | TickTick | 0.3.0 | 8 | 1 |  |
| @activepieces/piece-tidely | Tidely | 0.1.0 | 3 | 0 |  |
| @activepieces/piece-tidycal | TidyCal | 0.2.0 | 1 | 3 |  |
| @activepieces/piece-time-ops | TimeOps | 0.1.0 | 6 | 4 |  |
| @activepieces/piece-timelines-ai | TimelinesAI | 0.2.1 | 11 | 7 |  |
| @activepieces/piece-tiny-talk-ai | Tiny Talk AI | 0.1.8 | 1 | 0 |  |
| @activepieces/piece-tl-dv | tl;dv | 0.1.7 | 5 | 2 |  |
| @activepieces/piece-todoist | Todoist | 0.5.2 | 5 | 1 |  |
| @activepieces/piece-todos | Todos | 0.0.17 | 3 | 0 |  |
| @activepieces/piece-toggl-track | Toggl Track | 0.1.9 | 13 | 7 |  |
| @activepieces/piece-totalcms | Total CMS | 0.2.0 | 14 | 1 |  |
| @activepieces/piece-trello | Trello | 0.7.1 | 9 | 3 |  |
| @activepieces/piece-truelayer | TrueLayer | 0.2.1 | 39 | 0 |  |
| @activepieces/piece-trust | Trust | 0.1.0 | 12 | 1 |  |
| @activepieces/piece-twenty | Twenty | 0.1.1 | 8 | 2 |  |
| @activepieces/piece-twilio | Twilio | 0.6.1 | 6 | 5 |  |
| @activepieces/piece-twin-labs | Twin Web Agent | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-twitch | Twitch | 0.1.0 | 1 | 1 |  |
| @activepieces/piece-twitter | Twitter | 0.5.1 | 2 | 0 |  |
| @activepieces/piece-typeform | Typeform | 0.6.1 | 5 | 1 |  |
| @activepieces/piece-typefully | Typefully | 0.3.1 | 9 | 1 |  |
| @activepieces/piece-umami | Umami | 0.3.0 | 7 | 2 |  |
| @activepieces/piece-upgradechat | Upgrade.chat | 0.1.6 | 6 | 3 |  |
| @activepieces/piece-uptimerobot | UptimeRobot | 0.0.5 | 5 | 0 |  |
| @activepieces/piece-uscreen | Uscreen | 0.2.0 | 3 | 5 |  |
| @activepieces/piece-useinbox | Inbox | 0.1.0 | 7 | 6 |  |
| @activepieces/piece-uxsniff | UXsniff | 0.1.0 | 1 | 2 |  |
| @activepieces/piece-vadoo-ai | Vadoo AI | 0.1.7 | 4 | 0 |  |
| @activepieces/piece-validatedmails | ValidatedMails | 0.1.1 | 2 | 0 |  |
| @activepieces/piece-valyu | Valyu | 0.1.0 | 7 | 0 |  |
| @activepieces/piece-vapi | Vapi | 0.1.0 | 4 | 0 |  |
| @activepieces/piece-vbout | VBOUT | 0.1.7 | 10 | 0 |  |
| @activepieces/piece-vercel | Vercel | 0.1.1 | 6 | 0 |  |
| @activepieces/piece-vero | Vero | 0.1.7 | 7 | 11 |  |
| @activepieces/piece-video-ai | Video AI | 0.1.0 | 1 | 0 |  |
| @activepieces/piece-videoask | VideoAsk | 0.2.0 | 6 | 4 |  |
| @activepieces/piece-vidlab7 | VidLab7 | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-vidnoz | Vidnoz | 0.0.8 | 2 | 1 |  |
| @activepieces/piece-village | Village | 0.4.5 | 40 | 0 |  |
| @activepieces/piece-vimeo | Vimeo | 0.2.1 | 5 | 4 |  |
| @activepieces/piece-visible | Visible | 0.0.9 | 4 | 0 |  |
| @activepieces/piece-vlm-run | VLM Run | 0.2.0 | 6 | 0 |  |
| @activepieces/piece-voipstudio | VoIPstudio | 0.2.0 | 6 | 7 |  |
| @activepieces/piece-vouchery-io | Vouchery | 0.1.0 | 4 | 0 |  |
| @activepieces/piece-vtex | VTEX | 0.3.0 | 17 | 0 |  |
| @activepieces/piece-vtiger | Vtiger | 1.4.1 | 8 | 1 |  |
| @activepieces/piece-wafeq | Wafeq | 0.1.0 | 15 | 4 |  |
| @activepieces/piece-waitwhile | WaitWhile | 0.1.0 | 5 | 2 |  |
| @activepieces/piece-wayfront | Wayfront | 0.0.5 | 11 | 0 |  |
| @activepieces/piece-wealthbox | Wealthbox | 0.1.6 | 11 | 4 |  |
| @activepieces/piece-webex | Cisco Webex Meetings | 0.1.1 | 6 | 2 |  |
| @activepieces/piece-webflow | Webflow | 0.3.0 | 13 | 1 |  |
| @activepieces/piece-webhook | Webhook | 0.1.42 | 2 | 1 | [piece-webhook](piece-webhook.md) |
| @activepieces/piece-webling | Webling | 0.1.6 | 1 | 2 |  |
| @activepieces/piece-webscraping-ai | WebScraping AI | 0.1.7 | 5 | 0 |  |
| @activepieces/piece-wedof | Wedof | 1.4.7 | 45 | 28 |  |
| @activepieces/piece-week-done | Weekdone | 0.1.0 | 14 | 0 |  |
| @activepieces/piece-weekdone | Weekdone | 0.1.0 | 5 | 2 |  |
| @activepieces/piece-what-converts | WhatConverts | 0.1.7 | 4 | 2 |  |
| @activepieces/piece-whatsable | Whatsable | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-whatsapp | WhatsApp Business | 1.0.1 | 22 | 4 |  |
| @activepieces/piece-whatsscale | WhatsScale | 1.1.0 | 41 | 5 |  |
| @activepieces/piece-wistia | Wistia | 0.1.0 | 8 | 2 |  |
| @activepieces/piece-wonderchat | Wonderchat | 0.1.7 | 4 | 1 |  |
| @activepieces/piece-woocommerce | WooCommerce | 0.4.1 | 16 | 12 |  |
| @activepieces/piece-woodpecker | Woodpecker | 0.1.0 | 6 | 20 |  |
| @activepieces/piece-wootric | Wootric | 0.1.6 | 1 | 0 |  |
| @activepieces/piece-wordpress | WordPress | 0.7.1 | 5 | 1 |  |
| @activepieces/piece-workable | Workable | 0.2.1 | 7 | 1 |  |
| @activepieces/piece-workday | Workday | 0.1.1 | 25 | 14 |  |
| @activepieces/piece-wrike | Wrike | 0.2.0 | 9 | 3 |  |
| @activepieces/piece-writesonic-bulk | Writesonic | 0.2.0 | 11 | 0 |  |
| @activepieces/piece-wufoo | Wufoo | 0.2.0 | 5 | 2 |  |
| @activepieces/piece-xero | Xero | 0.8.1 | 48 | 13 |  |
| @activepieces/piece-xml | XML | 0.2.1 | 3 | 0 |  |
| @activepieces/piece-xquik | Xquik | 0.1.1 | 7 | 0 |  |
| @activepieces/piece-youcanbookme | YouCanBookMe | 0.2.0 | 3 | 1 |  |
| @activepieces/piece-youform | Youform | 0.1.8 | 0 | 1 |  |
| @activepieces/piece-youtrack | YouTrack | 0.2.1 | 19 | 2 |  |
| @activepieces/piece-youtube | YouTube | 0.8.1 | 9 | 1 |  |
| @activepieces/piece-zendesk | Zendesk | 0.5.1 | 18 | 10 |  |
| @activepieces/piece-zendesk-sell | Zendesk-sell | 0.2.1 | 12 | 8 |  |
| @activepieces/piece-zeplin | Zeplin | 0.1.0 | 6 | 2 |  |
| @activepieces/piece-zerobounce | ZeroBounce | 0.1.7 | 1 | 0 |  |
| @activepieces/piece-zoho-bookings | Zoho Bookings | 0.1.7 | 5 | 0 |  |
| @activepieces/piece-zoho-books | Zoho Books | 0.2.0 | 1 | 0 |  |
| @activepieces/piece-zoho-campaigns | Zoho Campaigns | 0.2.2 | 11 | 3 |  |
| @activepieces/piece-zoho-crm | Zoho CRM | 0.4.1 | 11 | 3 |  |
| @activepieces/piece-zoho-desk | Zoho Desk | 0.2.2 | 4 | 0 |  |
| @activepieces/piece-zoho-invoice | Zoho Invoice | 0.2.2 | 1 | 1 |  |
| @activepieces/piece-zoho-mail | Zoho Mail | 0.2.2 | 8 | 1 |  |
| @activepieces/piece-zoo | Zoo | 0.1.7 | 81 | 0 |  |
| @activepieces/piece-zoom | Zoom | 0.9.1 | 10 | 0 |  |
| @activepieces/piece-zuora | Zuora | 0.1.6 | 4 | 0 |  |
| @marcus-ai/piece-marcus | Marcus | (built-in) | — | — | Pre-installed in Hegl's AP image; never install via `install_activepieces_piece`. Connection auto-provisioned per agent at creation time — never `request_connection` for it. See the `activepieces` skill's "The Hegl pieces" section for the full action list. |
| @hegl-ai/piece-template | Template | (built-in) | 1 | 0 | Pre-installed in Hegl's AP image; never install via `install_activepieces_piece`. No connection. Renders Liquid templates with format escaping — see the `rendering-templates` skill. |
