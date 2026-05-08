"""Scraper framework tests — no live HTTP."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest

from hotline_helper.models import (
    Category,
    Contacts,
    Hotline,
    Source,
    SourceType,
)
from hotline_helper.scraper.base import Scraper, ScrapeResult
from hotline_helper.scraper.registry import discover


class FakeScraper(Scraper):
    iso_code = "ZZ"
    sources = ["https://example.gov/test"]

    def scrape(self) -> ScrapeResult:
        return ScrapeResult(
            iso_code=self.iso_code,
            hotlines=[
                Hotline(
                    id="zz-test",
                    name="Test",
                    categories=[Category.SUICIDE],
                    contacts=Contacts(phone="123"),
                    source=Source(
                        name="Test",
                        url="https://example.gov/test",
                        type=SourceType.GOVERNMENT,
                    ),
                )
            ],
            sources=self.sources,
        )


def test_scrape_result_shape():
    result = FakeScraper(client=MagicMock()).scrape()
    assert result.iso_code == "ZZ"
    assert len(result.hotlines) == 1
    assert result.scraped_on == date.today()


def test_registry_finds_shipped_scrapers():
    scrapers = discover()
    # We ship US, AU, FR by default — fail loudly if any disappear.
    for iso in ("US", "AU", "FR"):
        assert iso in scrapers, f"{iso} scraper missing from registry"


def test_us_scraper_factcheck_blocks_on_missing_token(monkeypatch):
    """If the SAMHSA page no longer mentions '988', the US scraper must raise."""
    from hotline_helper.scraper.countries.us import USAScraper

    scraper = USAScraper(client=MagicMock())
    monkeypatch.setattr(scraper, "fetch", lambda url: "<html>nothing relevant</html>")
    with pytest.raises(RuntimeError, match="fact-check failed"):
        scraper.scrape()


def test_us_scraper_passes_factcheck(monkeypatch):
    from hotline_helper.scraper.countries.us import USAScraper

    scraper = USAScraper(client=MagicMock())
    monkeypatch.setattr(
        scraper, "fetch", lambda url: "<html>Call 988 for the Suicide and Crisis Lifeline</html>"
    )
    result = scraper.scrape()
    assert any(h.id == "us-988" for h in result.hotlines)
