# Contributing to Hotline Helper

Thanks for helping make crisis hotline data more accessible. This project is volunteer-maintained, and your contribution — even a small data correction — could help someone in a vulnerable moment.

## Ground rules

1. **Government sources only.** Every entry must cite a government health authority (or a government-published list, like an NHS-signposted charity). NGO websites alone are not sufficient.
2. **Don't fabricate.** If a country's gov source doesn't list a hotline, the right answer is `verification_status: no_government_source` — not a guess.
3. **No live crisis advice in PRs.** If you encounter someone in crisis while researching, contact local emergency services. Don't escalate via this repo.
4. **Numbers are case-sensitive.** Phone numbers should be displayed as the source displays them (with spaces, hyphens, or parens preserved if that's how the gov page formats them).

## Local setup

Requires Python 3.10+.

```bash
git clone https://github.com/<agus-pleso>/Hotline_Helper.git
cd Hotline_Helper
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

hotline-helper validate           # validates every country YAML
hotline-helper list               # prints coverage table
hotline-helper serve              # starts the API at localhost:8000
pytest                            # runs the test suite
```

## Common tasks

### Correct or add a hotline for an existing country

1. Open `data/countries/{ISO}.yml`.
2. Edit. Set `last_verified: <today>` on each entry you touched.
3. Run `hotline-helper validate`.
4. Open a PR linking the gov source URL you used.

### Add a country that's currently `no_government_source`

1. Find a government health-authority page that lists crisis hotlines (.gov, .gob, ministry of health, NHS-equivalent).
2. Update `data/countries/{ISO}.yml` with the data and set `verification_status: verified`.
3. Add the source URLs to `metadata.data_sources`.
4. **Highly encouraged but optional:** add a scraper at `src/hotline_helper/scraper/countries/{iso_lower}.py` so future refreshes are automatic. See [adding a scraper](#adding-a-scraper) below.
5. Open a PR.

### Adding a scraper

Use `src/hotline_helper/scraper/countries/fr.py` as a template. The pattern:

```python
class XXScraper(Scraper):
    iso_code = "XX"
    sources = ["https://gov.example/crisis-hotlines"]
    EXPECTED_TOKENS = ["123-456-7890"]   # numbers/names that MUST still appear

    def scrape(self) -> ScrapeResult:
        html = self.fetch(self.sources[0])
        for token in self.EXPECTED_TOKENS:
            if token not in html:
                raise RuntimeError(f"XX fact-check failed: {token!r} missing")

        # Curated entries — DO NOT extract via fragile CSS selectors.
        return ScrapeResult(iso_code=self.iso_code, hotlines=[...], sources=self.sources)
```

### The "fact-check" pattern

Crisis data being subtly wrong is more dangerous than data being missing. Our scrapers do **not** extract entries with brittle DOM selectors. Instead, each scraper:

1. Hardcodes a curated list of entries reviewed by a maintainer.
2. Asserts the gov source page still mentions key tokens (numbers, names) before returning the curated list.
3. Raises if any expected token is missing — this surfaces the change for human review instead of silently overwriting good data with garbage.

If a number genuinely changed on the gov page, the maintainer updates both the curated list AND the `EXPECTED_TOKENS`.

## Verification status

| Status | When to use |
| ------ | ----------- |
| `verified` | A maintainer confirmed every entry against the cited source within the last review cycle. |
| `unverified` | The data is plausible but a maintainer hasn't re-confirmed since the most recent change (e.g. the auto-scraper proposed an update). |
| `no_government_source` | No gov page lists crisis hotlines for this country, or none has been identified. |

The monthly auto-scraper always sets touched countries to `unverified` until a maintainer reviews and re-flips them to `verified` in a follow-up PR.

## Style

- Run `ruff check src tests scripts` (or `ruff format` to auto-fix).
- Type hints on all new public functions.
- Tests for any new scraper logic; data changes don't need new tests but should pass existing validation.
- Commit messages: `data: ...`, `scraper: ...`, `api: ...`, `docs: ...`. Imperative mood.

## When in doubt

Open a draft PR and tag a maintainer. Better to ask than to guess.
