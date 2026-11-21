# Smart Search Tool

> **Development status:** This project is under active development. Features and provider availability may change. Review the provider limitations below before configuring a live search.

Smart Search Tool is an interactive command-line application for building structured web-search queries, validating and previewing them, running them through configured search APIs, and displaying normalized results.

## Features

- Guided search and direct expert-query modes
- Query Builder for keywords, domain, file type, title, URL, text, range, and excluded terms
- JSON-based operator catalog with support-status metadata
- Query validation and an explicit preview before a search is sent
- Provider abstraction and configuration status
- Brave Search API integration
- Google Custom Search JSON API integration for eligible existing customers
- Combined results across configured providers, with URL deduplication
- Local search history, saved queries, presets, and settings
- Automated tests

## Provider availability

| Provider | State in this application | Important notes |
| --- | --- | --- |
| Brave Search | Available when configured | Requires a Brave Search API subscription and API key. |
| Google Custom Search JSON API | Legacy integration | Google says the API is unavailable to new customers and will be discontinued on January 1, 2027. Existing eligible customers can use it until then, subject to Google's terms and quotas. |
| Bing Search API | Disabled | Microsoft retired the Bing Search APIs on August 11, 2025. The old endpoint in this project is not used. |
| DuckDuckGo | Not implemented | No provider is exposed as working until a supported API integration is available. |

**Recommended provider for a new setup: Brave Search API.** This tool does not scrape search-engine HTML pages. Provider requests require network access and may incur charges or usage limits.

## Requirements

- Python 3.11 or newer
- pip
- Internet access for live searches
- API credentials for at least one active provider

## Installation

Open PowerShell or Command Prompt in the project directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

For Command Prompt, activate with:

```bat
.venv\Scripts\activate.bat
```

## Configure an API key

1. Create a local `.env` file from the example:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Obtain a key from the provider:

   - **Brave:** create an account and API subscription at [Brave Search API](https://brave.com/search/api/), then copy the API key from the Brave developer dashboard.
   - **Google (existing customers only):** Google requires a Google Cloud API key and Programmable Search Engine ID (`cx`). Follow the [Custom Search JSON API overview](https://developers.google.com/custom-search/v1/overview) and [Programmable Search Engine setup guide](https://programmablesearchengine.google.com/controlpanel/all). Google currently states that this API is unavailable to new customers and is scheduled to discontinue on January 1, 2027.

3. Edit `.env` and set the key(s). Do not include quote marks unless they are part of a value:

   ```env
   BRAVE_API_KEY=paste_your_key_here
   DEFAULT_PROVIDER=brave
   RESULTS_PER_PAGE=10

   # Only for eligible existing Google Custom Search API customers:
   GOOGLE_API_KEY=
   GOOGLE_CX_ID=
   ```

4. Save `.env`. The application loads it on startup. API keys are never needed in Python source files.

The `.gitignore` excludes `.env`. **Never commit or share your API keys.** If a key is accidentally published, revoke it in the provider dashboard and generate a replacement.

### Getting credentials

- [Brave Search API](https://brave.com/search/api/)
- [Google Custom Search JSON API overview and requirements](https://developers.google.com/custom-search/v1/overview)
- [Google Programmable Search Engine control panel](https://programmablesearchengine.google.com/controlpanel/all)

There is no functioning Bing Search API integration because the product was retired. Do not add a `BING_API_KEY` expecting the old endpoint to work.

## Run the application

From the project directory:

```powershell
python -m smart_search
```

Choose **Guided Search** or **Query Builder**, fill in any fields you need, review the generated query, choose **Search**, then select a configured provider. Empty optional fields are allowed. You can also use **Expert Query** to enter a search string directly.

Example query:

```text
site:example.com filetype:pdf "annual financial report" intitle:2025 -draft
```

The **All Search Engines** selection runs only the providers implemented and configured in this application. A provider that is missing credentials is reported as unavailable; it is not treated as a successful search.

## Main menu

- **Guided Search** — choose a target and scopes, enter criteria, review the generated query, then search.
- **Expert Query** — enter the query string directly and choose a provider.
- **Query Builder** — enter structured fields; blank optional values are skipped.
- **Search Operators** — inspect the operator catalog and each operator's declared status.
- **Search Engines** — inspect availability, set the default provider, and initiate a test search.
- **Search History** — inspect previous searches and optionally run one again.
- **Presets** — load a bundled preset or a saved query into the builder.
- **Settings** — set the default provider and result count.

Search Engine Manager's **Test Connection** sends a real query (`test`) and may count against provider quotas or billing.

## Operators

Operator definitions are stored in [`smart_search/data/operators.json`](smart_search/data/operators.json), separately from query-generation logic. Current examples include:

- `site:domain`
- `filetype:pdf`
- `intitle:words`
- `inurl:words`
- `intext:words`
- `"exact phrase"`
- `(term1 OR term2)`
- `-excluded-term`
- range notation such as `2023..2025`

Operator behavior can vary by provider. Catalog status labels are descriptive metadata, not a guarantee that every engine interprets an operator identically.

## Local data and configuration

Search history, saved queries, and user settings are stored outside the source tree in the current user's application-data directory:

Bundled presets, operator definitions, and default settings remain in the project. This separation keeps personal search history and settings out of version control.

## Run tests

```powershell
python -m pytest -q
```

Provider tests use mocked HTTP responses, so the unit test suite does not require API keys or make live network requests.

## Current limitations

- The project is still under development; the terminal interface and some workflows may change.
- Only Brave and eligible Google Custom Search API accounts are exposed as active providers.
- Google Custom Search JSON API is unavailable to new customers and is scheduled to end on January 1, 2027.
- Bing Search API support is disabled because Microsoft retired the service.
- DuckDuckGo integration is not implemented.
- Result counts are limited to 10 per provider request; pagination is not yet implemented.
- Provider-specific operator compatibility warnings and a full interactive settings editor are not yet complete.
- API quotas, pricing, service availability, and terms are controlled by each provider.
# Smart-Search-Tool
