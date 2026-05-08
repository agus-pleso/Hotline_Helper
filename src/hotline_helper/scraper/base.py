"""Base classes for per-country scrapers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date

import httpx
from selectolax.parser import HTMLParser

from hotline_helper.models import Hotline

DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
DEFAULT_HEADERS = {
    # Identify ourselves so site operators can contact us if there's an issue.
    "User-Agent": (
        "HotlineHelperBot/0.1 (+https://github.com/agus-pleso/Hotline_Helper) "
        "monthly crisis-hotline data refresh"
    ),
    "Accept-Language": "en;q=0.9",
}


@dataclass
class ScrapeResult:
    """What a scraper returns for one country."""

    iso_code: str
    hotlines: list[Hotline]
    sources: list[str] = field(default_factory=list)
    notes: str | None = None
    scraped_on: date = field(default_factory=date.today)


class Scraper(ABC):
    """One Scraper per country (or per source within a country).

    Subclasses set `iso_code` and implement `scrape(client)`. The runner
    is responsible for instantiating the HTTP client and applying retries.
    """

    iso_code: str = ""
    sources: list[str] = []

    def __init__(self, client: httpx.Client | None = None):
        self._client = client

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=DEFAULT_TIMEOUT,
                headers=DEFAULT_HEADERS,
                follow_redirects=True,
            )
        return self._client

    def fetch(self, url: str) -> str:
        """Fetch text content with our shared client. Raises on non-2xx."""
        resp = self.client.get(url)
        resp.raise_for_status()
        return resp.text

    def parse(self, html: str) -> HTMLParser:
        return HTMLParser(html)

    @abstractmethod
    def scrape(self) -> ScrapeResult:
        """Return the canonical list of hotlines for this country.

        Implementations should not mutate disk or YAML — just return the
        in-memory `ScrapeResult`. The runner handles diffing and writing.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{type(self).__name__} iso={self.iso_code}>"
