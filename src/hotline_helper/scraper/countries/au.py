"""Australia — healthdirect.gov.au mental health helpline list."""

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


class AUScraper(Scraper):
    """Sources: healthdirect.gov.au (Australian Government) mental-health helplines page."""

    iso_code = "AU"
    sources = [
        "https://www.healthdirect.gov.au/mental-health-helplines",
    ]

    EXPECTED_TOKENS = ["13 11 14", "Lifeline", "Beyond Blue"]

    def scrape(self) -> ScrapeResult:
        html = self.fetch(self.sources[0])
        for token in self.EXPECTED_TOKENS:
            if token not in html:
                raise RuntimeError(
                    f"AU fact-check failed: expected token '{token}' not on healthdirect page."
                )

        today = date.today()
        gov_source = Source(
            name="healthdirect Australia (Australian Government Department of Health)",
            url="https://www.healthdirect.gov.au/mental-health-helplines",  # type: ignore[arg-type]
            type=SourceType.GOVERNMENT,
            last_verified=today,
        )

        hotlines = [
            Hotline(
                id="au-lifeline",
                name="Lifeline Australia",
                categories=[Category.SUICIDE, Category.CRISIS, Category.MENTAL_HEALTH],
                contacts=Contacts(
                    phone="13 11 14",
                    sms="0477 13 11 14",
                    chat_url="https://www.lifeline.org.au/crisis-chat/",  # type: ignore[arg-type]
                    website="https://www.lifeline.org.au",  # type: ignore[arg-type]
                ),
                languages=["en"],
                hours=Hours(type=HoursType.TWENTY_FOUR_SEVEN),
                cost=Cost.FREE,
                operator=OperatorType.NGO_GOVERNMENT_FUNDED,
                operator_name="Lifeline Australia (gov-funded NGO listed by healthdirect)",
                source=gov_source,
            ),
            Hotline(
                id="au-beyond-blue",
                name="Beyond Blue",
                categories=[Category.MENTAL_HEALTH, Category.CRISIS],
                contacts=Contacts(
                    phone="1300 22 4636",
                    chat_url="https://www.beyondblue.org.au/get-support/talk-to-a-counsellor/chat",  # type: ignore[arg-type]
                    website="https://www.beyondblue.org.au",  # type: ignore[arg-type]
                ),
                languages=["en"],
                hours=Hours(type=HoursType.TWENTY_FOUR_SEVEN),
                cost=Cost.FREE,
                operator=OperatorType.NGO_GOVERNMENT_FUNDED,
                operator_name="Beyond Blue (gov-funded NGO listed by healthdirect)",
                source=gov_source,
            ),
            Hotline(
                id="au-13yarn",
                name="13YARN",
                categories=[Category.SUICIDE, Category.CRISIS, Category.MENTAL_HEALTH],
                contacts=Contacts(
                    phone="13 92 76",
                    website="https://www.13yarn.org.au",  # type: ignore[arg-type]
                ),
                languages=["en"],
                hours=Hours(type=HoursType.TWENTY_FOUR_SEVEN),
                cost=Cost.FREE,
                target_population="Aboriginal and Torres Strait Islander peoples",
                operator=OperatorType.NGO_GOVERNMENT_FUNDED,
                operator_name="13YARN (Lifeline + Gayaa Dhuwi, gov-funded)",
                source=gov_source,
            ),
            Hotline(
                id="au-kids-helpline",
                name="Kids Helpline",
                categories=[Category.YOUTH, Category.CRISIS, Category.MENTAL_HEALTH],
                contacts=Contacts(
                    phone="1800 55 1800",
                    chat_url="https://kidshelpline.com.au/get-help/webchat-counselling",  # type: ignore[arg-type]
                    website="https://kidshelpline.com.au",  # type: ignore[arg-type]
                ),
                languages=["en"],
                hours=Hours(type=HoursType.TWENTY_FOUR_SEVEN),
                cost=Cost.FREE,
                target_population="children and young people aged 5–25",
                operator=OperatorType.NGO_GOVERNMENT_FUNDED,
                operator_name="Kids Helpline (yourtown, gov-funded)",
                source=gov_source,
            ),
        ]
        return ScrapeResult(
            iso_code=self.iso_code,
            hotlines=hotlines,
            sources=self.sources,
            scraped_on=today,
        )
