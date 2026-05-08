"""France — Ministère du Travail, de la Santé et des Solidarités: 3114."""

from __future__ import annotations

from datetime import date

from hotline_helper.models import (
    Category,
    Contacts,
    Cost,
    Hotline,
    Hours,
    HoursType,
    OperatorType,
    Source,
    SourceType,
)
from hotline_helper.scraper.base import Scraper, ScrapeResult


class FRScraper(Scraper):
    """Sources: 3114.fr (official site) and sante.gouv.fr."""

    iso_code = "FR"
    sources = [
        "https://3114.fr",
        "https://sante.gouv.fr/prevention-en-sante/sante-mentale/article/3114-numero-national-de-prevention-du-suicide",
    ]

    EXPECTED_NUMBER = "3114"

    def scrape(self) -> ScrapeResult:
        confirmed = False
        for url in self.sources:
            try:
                if self.EXPECTED_NUMBER in self.fetch(url):
                    confirmed = True
                    break
            except Exception:  # noqa: BLE001
                continue
        if not confirmed:
            raise RuntimeError("FR fact-check failed: '3114' not found on official sources.")

        today = date.today()
        gov_source = Source(
            name="Ministère du Travail, de la Santé et des Solidarités",
            url="https://3114.fr",  # type: ignore[arg-type]
            type=SourceType.GOVERNMENT,
            last_verified=today,
        )
        hotlines = [
            Hotline(
                id="fr-3114",
                name="3114 — Numéro national de prévention du suicide",
                categories=[Category.SUICIDE, Category.MENTAL_HEALTH, Category.CRISIS],
                contacts=Contacts(
                    phone="3114",
                    website="https://3114.fr",  # type: ignore[arg-type]
                ),
                languages=["fr"],
                hours=Hours(type=HoursType.TWENTY_FOUR_SEVEN),
                cost=Cost.FREE,
                target_population="general",
                operator=OperatorType.GOVERNMENT,
                operator_name="Ministère de la Santé",
                notes="Free, confidential, 24/7. Staffed by trained mental-health professionals.",
                source=gov_source,
            ),
        ]
        return ScrapeResult(
            iso_code=self.iso_code,
            hotlines=hotlines,
            sources=self.sources,
            scraped_on=today,
        )
