"""Pydantic schema for the Hotline Helper dataset.

The schema is intentionally narrow and explicit — every field has a single
well-defined meaning so downstream consumers (healthcare apps, telehealth
platforms) can map it deterministically to their own UI.
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class Category(str, Enum):
    """Crisis category. Used to filter hotlines by topic."""

    SUICIDE = "suicide"
    MENTAL_HEALTH = "mental_health"
    CRISIS = "crisis"
    DOMESTIC_VIOLENCE = "domestic_violence"
    SEXUAL_ASSAULT = "sexual_assault"
    CHILD_ABUSE = "child_abuse"
    YOUTH = "youth"
    LGBTQ = "lgbtq"
    SUBSTANCE_ABUSE = "substance_abuse"
    ELDER_ABUSE = "elder_abuse"
    VETERANS = "veterans"
    GENERAL_EMERGENCY = "general_emergency"
    DISCRIMINATION = "discrimination"


class OperatorType(str, Enum):
    """Who operates the hotline."""

    GOVERNMENT = "government"
    NGO_GOVERNMENT_FUNDED = "ngo_government_funded"
    NGO = "ngo"
    PRIVATE = "private"
    UNKNOWN = "unknown"


class SourceType(str, Enum):
    """Provenance of the data entry."""

    GOVERNMENT = "government"
    INTERGOVERNMENTAL = "intergovernmental"
    ACADEMIC = "academic"
    NGO = "ngo"


class VerificationStatus(str, Enum):
    """Whether a maintainer has confirmed the country's data."""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    NO_GOVERNMENT_SOURCE = "no_government_source"


class Cost(str, Enum):
    FREE = "free"
    PAID = "paid"
    VARIES = "varies"
    UNKNOWN = "unknown"


class HoursType(str, Enum):
    TWENTY_FOUR_SEVEN = "24/7"
    BUSINESS_HOURS = "business_hours"
    EVENING = "evening"
    WEEKENDS_ONLY = "weekends_only"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


class Hours(BaseModel):
    """When the hotline is reachable."""

    type: HoursType = HoursType.UNKNOWN
    details: str | None = Field(
        default=None,
        description="Free-text notes when `type` is `custom`, or extra context (timezone, etc.).",
    )

    model_config = ConfigDict(use_enum_values=True)


class Contacts(BaseModel):
    """Ways to reach the hotline. At least one of phone/sms/chat_url/website is required."""

    phone: str | None = Field(default=None, description="Primary phone number, dialable as-shown.")
    phone_alt: str | None = Field(default=None, description="Secondary number, e.g. mobile/WhatsApp.")
    sms: str | None = Field(default=None, description="SMS shortcode or number.")
    chat_url: HttpUrl | None = None
    email: str | None = None
    website: HttpUrl | None = None

    @field_validator("phone", "phone_alt", "sms")
    @classmethod
    def _strip_whitespace(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v or None


class Source(BaseModel):
    """Where this entry came from. Required — every hotline must cite a source."""

    name: str = Field(description="Human-readable source name, e.g. 'SAMHSA' or 'NHS England'.")
    url: HttpUrl = Field(description="Canonical URL of the source page.")
    type: SourceType = SourceType.GOVERNMENT
    last_verified: date | None = Field(
        default=None,
        description="Last date a maintainer or scraper confirmed the source still listed this hotline.",
    )


class Hotline(BaseModel):
    """A single crisis hotline entry."""

    id: str = Field(
        description="Stable slug identifier, e.g. 'us-988'. Lowercase, hyphenated.",
        pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$",
    )
    name: str
    aliases: list[str] = Field(default_factory=list)
    categories: list[Category] = Field(min_length=1)

    contacts: Contacts
    languages: list[str] = Field(
        default_factory=list,
        description="ISO 639-1 codes (e.g. 'en', 'es'). Lowercase.",
    )
    hours: Hours = Field(default_factory=Hours)
    cost: Cost = Cost.UNKNOWN
    fees_note: str | None = None

    target_population: str | None = Field(
        default=None,
        description="Free-text, e.g. 'youth', 'veterans', 'indigenous', 'general'.",
    )
    operator: OperatorType = OperatorType.UNKNOWN
    operator_name: str | None = None
    notes: str | None = None

    source: Source

    model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

    @field_validator("languages")
    @classmethod
    def _normalize_languages(cls, v: list[str]) -> list[str]:
        return [lang.strip().lower() for lang in v if lang.strip()]

    @field_validator("contacts")
    @classmethod
    def _at_least_one_contact(cls, v: Contacts) -> Contacts:
        if not any([v.phone, v.phone_alt, v.sms, v.chat_url, v.email, v.website]):
            raise ValueError("Hotline must have at least one contact channel.")
        return v


class Country(BaseModel):
    """Country metadata."""

    iso_code: str = Field(min_length=2, max_length=2, description="ISO 3166-1 alpha-2.")
    iso3: str | None = Field(default=None, min_length=3, max_length=3)
    name: str
    region: str | None = None
    subregion: str | None = None

    @field_validator("iso_code")
    @classmethod
    def _upper_iso(cls, v: str) -> str:
        return v.upper()

    @field_validator("iso3")
    @classmethod
    def _upper_iso3(cls, v: str | None) -> str | None:
        return v.upper() if v else v


class EmergencyService(BaseModel):
    """Generic emergency line (police/fire/medical), separate from crisis hotlines."""

    name: str
    phone: str
    notes: str | None = None


class Metadata(BaseModel):
    """Per-country metadata."""

    last_updated: date
    last_scraped: date | None = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    data_sources: list[HttpUrl] = Field(default_factory=list)
    notes: str | None = None

    model_config = ConfigDict(use_enum_values=True)


class CountryFile(BaseModel):
    """Top-level shape of `data/countries/{ISO}.yml`."""

    country: Country
    emergency_services: list[EmergencyService] = Field(default_factory=list)
    hotlines: list[Hotline] = Field(default_factory=list)
    metadata: Metadata
