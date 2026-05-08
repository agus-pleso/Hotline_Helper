"""Scraper framework — pulls hotline data from authoritative government pages.

The scraper is intentionally split per country. Each country module:

  1. Declares the gov URLs it sources from.
  2. Implements `scrape() -> list[Hotline]` that returns canonical entries.

The runner (see `scraper.runner`) collects results, diffs against the current
YAML files, and either prints the diff or writes the YAML in place. In CI,
the diff is committed onto a branch and surfaced as a pull request for human
review — the scraper proposes, maintainers dispose.
"""

from hotline_helper.scraper.base import Scraper, ScrapeResult

__all__ = ["Scraper", "ScrapeResult"]
