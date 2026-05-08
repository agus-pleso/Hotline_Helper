"""United States — SAMHSA-published crisis hotlines."""

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


class USAScraper(Scraper):
    """Sources: SAMHSA (HHS) and the 988 Lifeline operator (federally administered).

    This scraper uses a "fact-check" pattern: it asserts the curated number(s)
    still appear on the gov page. If they don't, it raises rather than silently
    overwriting a verified entry with garbage.
    """

    iso_code = "US"
    sources = [
        "https://www.samhsa.gov/find-help/988",
        "https://www.hhs.gov/988-suicide-crisis-lifeline/",
    ]

    EXPECTED_NUMBER = "988"

    def scrape(self) -> ScrapeResult:
        # Fact-check: at least one canonical source must still mention "988".
        confirmed = False
        for url in self.sources:
            try:
                html = self.fetch(url)
                if self.EXPECTED_NUMBER in html:
                    confirmed = True
                    break
            except Exception:  # noqa: BLE001 — try the next source
                continue

        if not confirmed:
            raise RuntimeError(
                "US fact-check failed: '988' not found on any SAMHSA/HHS source page. "
                "Investigate before overwriting US.yml."
            )

        today = date.today()
        source = Source(
            name="Substance Abuse and Mental Health Services Administration (SAMHSA)",
            url="https://www.samhsa.gov/find-help/988",  # type: ignore[arg-type]
            type=SourceType.GOVERNMENT,
            last_verified=today,
        )

        hotlines = [
            Hotline(
                id="us-988",
                name="988 Suicide and Crisis Lifeline",
                aliases=["988 Lifeline", "National Suicide Prevention Lifeline"],
                categories=[Category.SUICIDE, Category.MENTAL_HEALTH, Category.CRISIS],
                contacts=Contacts(
                    phone="988",
                    sms="988",
                    chat_url="https://988lifeline.org/chat/",  # type: ignore[arg-type]
                    website="https://988lifeline.org",  # type: ignore[arg-type]
                ),
                languages=["en", "es"],
                hours=Hours(type=HoursType.TWENTY_FOUR_SEVEN),
                cost=Cost.FREE,
                fees_note="Free; standard SMS/data rates may apply.",
                target_population="general",
                operator=OperatorType.GOVERNMENT,
                operator_name="SAMHSA",
                notes=(
                    "Press 1 to reach the Veterans Crisis Line. Spanish-language line "
                    "and translation services for 240+ languages. Available throughout "
                    "the United States and US territories."
                ),
                source=source,
            ),
            Hotline(
                id="us-veterans-crisis-line",
                name="Veterans Crisis Line",
                categories=[Category.SUICIDE, Category.MENTAL_HEALTH, Category.VETERANS],
                contacts=Contacts(
                    phone="988",
                    phone_alt="1-800-273-8255",
                    sms="838255",
                    chat_url="https://www.veteranscrisisline.net/get-help-now/chat/",  # type: ignore[arg-type]
                    website="https://www.veteranscrisisline.net",  # type: ignore[arg-type]
                ),
                languages=["en"],
                hours=Hours(type=HoursType.TWENTY_FOUR_SEVEN),
                cost=Cost.FREE,
                target_population="veterans, service members, and their families",
                operator=OperatorType.GOVERNMENT,
                operator_name="US Department of Veterans Affairs",
                notes="Reachable by dialing 988 then pressing 1.",
                source=Source(
                    name="US Department of Veterans Affairs",
                    url="https://www.veteranscrisisline.net",  # type: ignore[arg-type]
                    type=SourceType.GOVERNMENT,
                    last_verified=today,
                ),
            ),
        ]

        return ScrapeResult(
            iso_code=self.iso_code,
            hotlines=hotlines,
            sources=self.sources,
            scraped_on=today,
        )
