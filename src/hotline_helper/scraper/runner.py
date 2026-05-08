"""Run scrapers, diff against current YAML, optionally write."""

from __future__ import annotations

import difflib
from datetime import date

import httpx
import yaml
from rich.console import Console

from hotline_helper.loader import country_files_dir, load_country_file
from hotline_helper.models import CountryFile, Metadata, VerificationStatus
from hotline_helper.scraper.base import DEFAULT_HEADERS, DEFAULT_TIMEOUT, Scraper
from hotline_helper.scraper.registry import discover

console = Console()


def _yaml_dump(obj: dict) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=100,
    )


def _serialize(cf: CountryFile) -> str:
    """Stable, diff-friendly YAML representation of a CountryFile."""
    return _yaml_dump(cf.model_dump(mode="json", exclude_none=True))


def _merge(existing: CountryFile | None, scraper: Scraper) -> CountryFile:
    """Merge a fresh scrape into an existing CountryFile.

    The scrape only owns hotline content + last_scraped — it does NOT change
    the country block, emergency_services, or human-set verification status.
    """
    result = scraper.scrape()
    if existing is None:
        # Brand-new file: bare-minimum scaffolding. Maintainer will flesh out
        # the country metadata in the same PR.
        from hotline_helper.models import Country

        country = Country(iso_code=scraper.iso_code, name=scraper.iso_code)
        return CountryFile(
            country=country,
            hotlines=result.hotlines,
            metadata=Metadata(
                last_updated=date.today(),
                last_scraped=result.scraped_on,
                verification_status=VerificationStatus.UNVERIFIED,
                data_sources=result.sources,  # type: ignore[arg-type]
            ),
        )
    return existing.model_copy(
        update={
            "hotlines": result.hotlines,
            "metadata": existing.metadata.model_copy(
                update={
                    "last_updated": date.today(),
                    "last_scraped": result.scraped_on,
                    # Force a re-review on any change. Maintainer flips back to verified.
                    "verification_status": VerificationStatus.UNVERIFIED,
                    "data_sources": result.sources or list(existing.metadata.data_sources),
                }
            ),
        }
    )


def run(country: str | None = None, write: bool = False) -> list[str]:
    """Run all (or one) scrapers. Return list of ISO codes whose YAML changed."""
    scrapers = discover()
    if country:
        iso = country.upper()
        if iso not in scrapers:
            console.print(f"[red]No scraper registered for {iso}.[/red]")
            return []
        targets = {iso: scrapers[iso]}
    else:
        targets = scrapers

    if not targets:
        console.print("[yellow]No scrapers found.[/yellow]")
        return []

    changed: list[str] = []
    with httpx.Client(timeout=DEFAULT_TIMEOUT, headers=DEFAULT_HEADERS, follow_redirects=True) as client:
        for iso, scraper_cls in sorted(targets.items()):
            scraper = scraper_cls(client=client)
            console.print(f"[cyan]→ scraping {iso}[/cyan]")
            try:
                path = country_files_dir() / f"{iso}.yml"
                existing = load_country_file(path) if path.exists() else None
                merged = _merge(existing, scraper)
            except Exception as e:  # noqa: BLE001 — scraper failures shouldn't kill the whole run
                console.print(f"[red]✗ {iso}: {e}[/red]")
                continue

            new_text = _serialize(merged)
            old_text = _serialize(existing) if existing else ""

            if new_text == old_text:
                continue

            changed.append(iso)
            if write:
                path.write_text(new_text, encoding="utf-8")
                console.print(f"  [green]wrote {path.name}[/green]")
            else:
                _print_diff(iso, old_text, new_text)

    return changed


def _print_diff(iso: str, old: str, new: str) -> None:
    diff = difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=f"a/{iso}.yml",
        tofile=f"b/{iso}.yml",
        n=3,
    )
    text = "".join(diff)
    if text:
        console.print(text)
