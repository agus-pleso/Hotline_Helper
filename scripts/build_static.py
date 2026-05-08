"""Build the static JSON tree that gets deployed to GitHub Pages.

Layout produced (under `dist/`):

    index.html              ← landing page (Pages root)
    api/v1/health.json
    api/v1/index.json
    api/v1/countries.json
    api/v1/countries/{ISO}.json
    api/v1/categories.json
    api/v1/categories/{category}.json
    api/v1/openapi.json

The whole `dist/` tree is what the GitHub Pages workflow uploads. URL shape:
`https://user.github.io/Hotline_Helper/api/v1/countries/US.json`.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from hotline_helper import __version__
from hotline_helper.api import app
from hotline_helper.loader import load_all
from hotline_helper.models import Category


def _write_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False),
        encoding="utf-8",
    )


def build(out_root: Path) -> None:
    """Generate the full static site under `out_root`.

    `out_root` is the Pages artifact root (e.g. `dist/`). The landing
    `index.html` goes at `out_root`, JSON tree at `out_root/api/v1/`.
    """
    base = out_root / "api" / "v1"
    base.mkdir(parents=True, exist_ok=True)

    countries = load_all()

    _write_json(base / "health.json", {"status": "ok", "version": __version__})

    countries_summary = [
        {
            "iso_code": iso,
            "name": cf.country.name,
            "region": cf.country.region,
            "hotline_count": len(cf.hotlines),
            "verification_status": cf.metadata.verification_status,
            "last_updated": cf.metadata.last_updated.isoformat(),
        }
        for iso, cf in sorted(countries.items())
    ]
    _write_json(
        base / "countries.json",
        {"count": len(countries_summary), "countries": countries_summary},
    )

    countries_dir = base / "countries"
    for iso, cf in countries.items():
        _write_json(countries_dir / f"{iso}.json", cf.model_dump(mode="json"))

    by_cat: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for iso, cf in countries.items():
        for h in cf.hotlines:
            for c in h.categories:
                code = c if isinstance(c, str) else c.value
                by_cat[code][iso].append(h.model_dump(mode="json"))

    cat_summary = []
    cat_dir = base / "categories"
    for cat in Category:
        results = by_cat.get(cat.value, {})
        total = sum(len(hs) for hs in results.values())
        cat_summary.append({"code": cat.value, "hotline_count": total})
        _write_json(
            cat_dir / f"{cat.value}.json",
            {
                "category": cat.value,
                "country_count": len(results),
                "results": dict(results),
            },
        )
    _write_json(base / "categories.json", {"categories": cat_summary})

    _write_json(
        base / "index.json",
        {
            "version": __version__,
            "countries": {iso: cf.model_dump(mode="json") for iso, cf in countries.items()},
        },
    )

    _write_json(base / "openapi.json", app.openapi())

    _write_landing(out_root, countries_summary)


def _write_landing(out_root: Path, countries_summary: list[dict]) -> None:
    """A minimal HTML landing page so the Pages root isn't a 404."""
    rows = "\n".join(
        f'      <tr><td><code>{c["iso_code"]}</code></td>'
        f'<td>{c["name"]}</td>'
        f'<td>{c["hotline_count"]}</td>'
        f'<td>{c["verification_status"]}</td></tr>'
        for c in countries_summary
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Hotline Helper API</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body {{ font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; max-width: 880px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
  h1 {{ margin-bottom: 0.25rem; }}
  code {{ background: #f3f3f3; padding: 1px 5px; border-radius: 3px; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
  th, td {{ text-align: left; padding: 6px 10px; border-bottom: 1px solid #eee; }}
  th {{ background: #fafafa; }}
  .warn {{ background: #fff8d4; border-left: 4px solid #c9a800; padding: 0.75rem 1rem; margin: 1rem 0; }}
</style>
</head>
<body>
  <h1>Hotline Helper</h1>
  <p>Free, open, government-sourced crisis hotline data for every country in the world.</p>

  <div class="warn">
    <strong>Disclaimer.</strong> Best-effort dataset, not a substitute for verified emergency services.
    See <a href="https://github.com/agus-pleso/Hotline_Helper/blob/main/DISCLAIMER.md">DISCLAIMER.md</a> before integrating.
  </div>

  <h2>Endpoints</h2>
  <ul>
    <li><a href="v1/countries.json"><code>/v1/countries.json</code></a> — country index</li>
    <li><code>/v1/countries/{{ISO}}.json</code> — one country (e.g. <a href="v1/countries/US.json">US</a>, <a href="v1/countries/AU.json">AU</a>, <a href="v1/countries/FR.json">FR</a>)</li>
    <li><a href="v1/categories.json"><code>/v1/categories.json</code></a> — category index</li>
    <li><code>/v1/categories/{{category}}.json</code> — one category (e.g. <a href="v1/categories/suicide.json">suicide</a>)</li>
    <li><a href="v1/index.json"><code>/v1/index.json</code></a> — full dataset (one big JSON)</li>
    <li><a href="v1/openapi.json"><code>/v1/openapi.json</code></a> — OpenAPI spec</li>
  </ul>

  <h2>Coverage ({len(countries_summary)} countries)</h2>
  <table>
    <thead><tr><th>ISO</th><th>Country</th><th>Hotlines</th><th>Status</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table>

  <p style="margin-top:2rem;color:#777">
    Source code &amp; contributing: <a href="https://github.com/agus-pleso/Hotline_Helper">github.com/agus-pleso/Hotline_Helper</a>.
    Data is CC0; code is MIT.
  </p>
</body>
</html>
"""
    (out_root / "index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", "-o", default="dist", type=Path)
    args = parser.parse_args()
    build(args.output)
    print(f"Built static site -> {args.output}")
