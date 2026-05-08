# Hotline Helper

> Free, open, government-sourced crisis & suicide-prevention hotline data for every country in the world — available as a static JSON API and a self-hostable service.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Data License: CC0](https://img.shields.io/badge/Data%20License-CC0-blue.svg)](DATA_LICENSE)
[![Monthly scrape](https://img.shields.io/badge/data%20refresh-monthly-green.svg)](.github/workflows/scrape.yml)

Hotline Helper makes it easy for healthcare companies, telehealth platforms, and other applications to **show users the right crisis resources for their country**, without each company having to maintain their own list.

The dataset is:

- **Government-sourced.** Every entry cites a government health authority (or government-published list) as its source of truth. NGO/charity hotlines are included only when listed by an authoritative government source.
- **Refreshed monthly.** A scheduled scraper opens a pull request with diffs every month, so the data stays current without manual upkeep.
- **Human-reviewed.** No data lands in `main` without a maintainer reviewing the diff. The scraper proposes; humans dispose.
- **Free.** Hosted on GitHub Pages (free), refreshed by GitHub Actions (free for public repos). No paid services, no API keys, no rate limits.

> [!IMPORTANT]
> **Read the [DISCLAIMER](DISCLAIMER.md) before integrating this data.** Crisis hotline information changes; numbers can be retired or rerouted; this dataset is best-effort and is not a substitute for live verification by a qualified clinician or organization. Do not rely on it as the sole pathway for someone in active crisis.

---

## Quick start

### Use the public API (no setup)

The dataset is published as static JSON to GitHub Pages on every merge to `main`:

```
https://<agus-pleso>.github.io/Hotline_Helper/api/v1/countries/US.json
https://<agus-pleso>.github.io/Hotline_Helper/api/v1/countries.json
https://<agus-pleso>.github.io/Hotline_Helper/api/v1/categories/suicide.json
https://<agus-pleso>.github.io/Hotline_Helper/api/v1/index.json
https://<agus-pleso>.github.io/Hotline_Helper/api/v1/openapi.json
```

Fetch from your app:

```js
const res = await fetch(
  "https://<agus-pleso>.github.io/Hotline_Helper/api/v1/countries/US.json"
);
const { hotlines } = await res.json();
```

### Self-host the API

For SLA-backed deployments, run the FastAPI service yourself.

```bash
git clone https://github.com/<agus-pleso>/Hotline_Helper.git
cd Hotline_Helper
pip install -e .
hotline-helper serve            # → http://localhost:8000/docs
```

Or with Docker:

```bash
docker build -t hotline-helper .
docker run -p 8000:8000 hotline-helper
```

### Use the raw YAML

Each country is one file under [`data/countries/`](data/countries/). YAML is the source of truth; JSON is generated. If you don't want a network dependency, vendor the YAML or JSON directly.

---

## Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET`  | `/v1/countries` | List all countries with metadata |
| `GET`  | `/v1/countries/{iso}` | All hotlines for one country (ISO 3166-1 alpha-2) |
| `GET`  | `/v1/categories` | List all categories |
| `GET`  | `/v1/categories/{category}` | All hotlines for a category, grouped by country |
| `GET`  | `/v1/search?q=&country=&category=` | Search/filter hotlines |
| `GET`  | `/v1/index` | Full dataset (one big JSON) |
| `GET`  | `/v1/openapi.json` | OpenAPI 3.1 spec |
| `GET`  | `/v1/health` | Service heartbeat |

See [`docs/SCHEMA.md`](docs/SCHEMA.md) for the response shape.

---

## How the data stays fresh

```
                    ┌──────────────────────────────────┐
  GitHub Actions ─▶ │ scraper.runner: per-country jobs │
   (monthly cron)   └──────────────────────────────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │  data/countries/*  │ ← diff'd against current YAML
                         └────────────────────┘
                                   │
                                   ▼
                       ┌──────────────────────────┐
                       │  Pull request with diff  │ ← maintainer reviews
                       └──────────────────────────┘
                                   │ merge
                                   ▼
                       ┌──────────────────────────┐
                       │  Build static JSON +     │
                       │  deploy to GitHub Pages  │
                       └──────────────────────────┘
```

Each country's gov source URLs live alongside its scraper at [`src/hotline_helper/scraper/countries/{iso_lower}.py`](src/hotline_helper/scraper/countries/) — see [`us.py`](src/hotline_helper/scraper/countries/us.py) for the template. Adding a new country means:

1. Drop a module at `src/hotline_helper/scraper/countries/xx.py` declaring `iso_code`, `sources`, and a `scrape()` that returns a curated `ScrapeResult` with a fact-check assertion.
2. Run `hotline-helper scrape --country XX` locally to preview the diff.
3. Open a PR.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full flow.

---

## Coverage

All 249 ISO 3166-1 alpha-2 codes have a YAML file. Each file is in one of three states:

| Status | Meaning |
| ------ | ------- |
| `verified` | Hotline data sourced from a government authority and confirmed by a maintainer in the last review cycle. |
| `unverified` | Data exists but has not been confirmed by a maintainer (e.g., still pending review after a scrape). |
| `no_government_source` | No government-published crisis hotline list could be identified for this country. The file lists international fallbacks (IASP, Befrienders Worldwide) only if a government source endorses them. |

You can filter by `verification_status` in any API response.

---

## Categories

| Code | Description |
| ---- | ----------- |
| `suicide` | Suicide prevention / ideation |
| `mental_health` | General mental health crisis |
| `crisis` | General crisis (catch-all) |
| `domestic_violence` | Domestic / intimate partner violence |
| `sexual_assault` | Sexual assault / rape crisis |
| `child_abuse` | Child abuse, neglect, missing children |
| `youth` | Youth-specific crisis lines |
| `lgbtq` | LGBTQ+ crisis & hate-crime support |
| `substance_abuse` | Drug & alcohol crisis support |
| `elder_abuse` | Abuse and crisis support for older adults |
| `veterans` | Military veterans |
| `general_emergency` | Police / fire / medical (e.g. 911, 112) |
| `discrimination` | Hate crime / discrimination reporting |

---

## License

- **Code:** [MIT](LICENSE)
- **Data:** [CC0 1.0 Universal](DATA_LICENSE) — public domain dedication. Use it however you want, with no attribution required (though we appreciate it).

---

## Contributing

Corrections, new sources, and new country scrapers are very welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md). If you spot incorrect or out-of-date data, please [open a data correction issue](.github/ISSUE_TEMPLATE/data_correction.yml) — even without a PR, that flag is useful.

---

## Disclaimer (short)

This dataset is best-effort, community-maintained, and **does not replace** authoritative emergency-services routing. Always verify a number is current before depending on it for someone in crisis. See [DISCLAIMER.md](DISCLAIMER.md).
