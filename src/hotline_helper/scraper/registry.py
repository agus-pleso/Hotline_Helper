"""Discover scrapers by ISO code.

Scrapers live in `hotline_helper.scraper.countries.<iso_lower>` and export
a `Scraper` subclass. Adding a new country = drop a module in that package.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hotline_helper.scraper.base import Scraper


def discover() -> dict[str, type[Scraper]]:
    """Walk `scraper.countries` and collect all `Scraper` subclasses, keyed by ISO."""
    from hotline_helper.scraper import countries
    from hotline_helper.scraper.base import Scraper

    out: dict[str, type[Scraper]] = {}
    for mod_info in pkgutil.iter_modules(countries.__path__):
        module = importlib.import_module(f"hotline_helper.scraper.countries.{mod_info.name}")
        for attr in vars(module).values():
            if (
                isinstance(attr, type)
                and issubclass(attr, Scraper)
                and attr is not Scraper
                and attr.iso_code
            ):
                out[attr.iso_code.upper()] = attr
    return out
