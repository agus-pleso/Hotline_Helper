"""FastAPI application — the self-hostable runtime API.

The same data is also exported as static JSON to GitHub Pages by
`scripts/build_static.py`. Both surfaces share the schema in `models.py`.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from hotline_helper import __version__
from hotline_helper.loader import load_all
from hotline_helper.models import Category, CountryFile, Hotline, VerificationStatus

app = FastAPI(
    title="Hotline Helper",
    version=__version__,
    description=(
        "Free, open, government-sourced crisis hotline data for every country. "
        "See https://github.com/agus-pleso/Hotline_Helper for the source dataset and disclaimer."
    ),
    contact={"url": "https://github.com/agus-pleso/Hotline_Helper"},
    license_info={"name": "MIT (code) / CC0 (data)"},
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Public read-only data — open CORS is intentional.
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/v1/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/v1/countries", tags=["countries"])
def list_countries(
    verification_status: Annotated[
        VerificationStatus | None,
        Query(description="Filter to only countries with this verification status."),
    ] = None,
) -> dict:
    """Lightweight list — country metadata only, no hotlines.

    Use `/v1/countries/{iso}` for full data on one country, or `/v1/index` for everything.
    """
    data = load_all()
    items = []
    for iso, cf in data.items():
        if verification_status and cf.metadata.verification_status != verification_status.value:
            continue
        items.append(
            {
                "iso_code": iso,
                "name": cf.country.name,
                "region": cf.country.region,
                "hotline_count": len(cf.hotlines),
                "verification_status": cf.metadata.verification_status,
                "last_updated": cf.metadata.last_updated.isoformat(),
            }
        )
    return {"count": len(items), "countries": items}


@app.get("/v1/countries/{iso_code}", tags=["countries"], response_model=CountryFile)
def get_country(iso_code: str) -> CountryFile:
    cf = load_all().get(iso_code.upper())
    if cf is None:
        raise HTTPException(status_code=404, detail=f"Country '{iso_code}' not found.")
    return cf


@app.get("/v1/categories", tags=["categories"])
def list_categories() -> dict:
    counts: dict[str, int] = defaultdict(int)
    for cf in load_all().values():
        for h in cf.hotlines:
            for c in h.categories:
                counts[c if isinstance(c, str) else c.value] += 1
    return {
        "categories": [
            {"code": cat.value, "hotline_count": counts.get(cat.value, 0)} for cat in Category
        ]
    }


@app.get("/v1/categories/{category}", tags=["categories"])
def get_category(category: Category) -> dict:
    target = category.value
    by_country: dict[str, list[Hotline]] = defaultdict(list)
    for iso, cf in load_all().items():
        for h in cf.hotlines:
            cats = [c if isinstance(c, str) else c.value for c in h.categories]
            if target in cats:
                by_country[iso].append(h)
    return {
        "category": target,
        "country_count": len(by_country),
        "results": {iso: [h.model_dump(mode="json") for h in hs] for iso, hs in by_country.items()},
    }


@app.get("/v1/search", tags=["search"])
def search(
    q: Annotated[
        str | None, Query(description="Free-text match against name/aliases/notes.")
    ] = None,
    country: Annotated[str | None, Query(description="ISO 3166-1 alpha-2.")] = None,
    category: Category | None = None,
    language: Annotated[str | None, Query(description="ISO 639-1 (e.g. 'en').")] = None,
) -> dict:
    needle = q.lower().strip() if q else None
    target_cat = category.value if category else None
    target_lang = language.lower().strip() if language else None
    target_country = country.upper().strip() if country else None

    results: list[dict] = []
    for iso, cf in load_all().items():
        if target_country and iso != target_country:
            continue
        for h in cf.hotlines:
            cats = [c if isinstance(c, str) else c.value for c in h.categories]
            if target_cat and target_cat not in cats:
                continue
            if target_lang and target_lang not in h.languages:
                continue
            if needle:
                haystack = " ".join(
                    [h.name, *h.aliases, h.notes or "", h.target_population or ""]
                ).lower()
                if needle not in haystack:
                    continue
            entry = h.model_dump(mode="json")
            entry["country"] = iso
            results.append(entry)
    return {"count": len(results), "results": results}


@app.get("/v1/index", tags=["bulk"])
def full_index() -> JSONResponse:
    """Entire dataset in one response. Cache aggressively — this can be large."""
    payload = {
        "version": __version__,
        "countries": {
            iso: cf.model_dump(mode="json") for iso, cf in load_all().items()
        },
    }
    return JSONResponse(payload, headers={"Cache-Control": "public, max-age=3600"})
