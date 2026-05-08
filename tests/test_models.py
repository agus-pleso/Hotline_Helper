"""Schema validation tests."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from hotline_helper.models import (
    Category,
    Contacts,
    Country,
    CountryFile,
    Hotline,
    Hours,
    HoursType,
    Metadata,
    OperatorType,
    Source,
    SourceType,
    VerificationStatus,
)


def _valid_source() -> Source:
    return Source(
        name="Test Ministry of Health",
        url="https://example.gov/hotlines",
        type=SourceType.GOVERNMENT,
        last_verified=date(2026, 1, 1),
    )


def _valid_hotline(**overrides) -> Hotline:
    base = dict(
        id="xx-test",
        name="Test Hotline",
        categories=[Category.SUICIDE],
        contacts=Contacts(phone="123"),
        hours=Hours(type=HoursType.TWENTY_FOUR_SEVEN),
        operator=OperatorType.GOVERNMENT,
        source=_valid_source(),
    )
    base.update(overrides)
    return Hotline(**base)


def test_hotline_requires_at_least_one_contact():
    with pytest.raises(ValidationError, match="at least one contact"):
        Hotline(
            id="xx-bad",
            name="Bad",
            categories=[Category.SUICIDE],
            contacts=Contacts(),
            source=_valid_source(),
        )


def test_hotline_id_must_be_slug():
    with pytest.raises(ValidationError):
        _valid_hotline(id="Not_A_Slug")


def test_hotline_categories_must_be_nonempty():
    with pytest.raises(ValidationError):
        _valid_hotline(categories=[])


def test_iso_code_uppercased():
    c = Country(iso_code="us", name="United States")
    assert c.iso_code == "US"


def test_languages_normalized():
    h = _valid_hotline(languages=[" EN ", "Es", ""])
    assert h.languages == ["en", "es"]


def test_country_file_round_trip():
    cf = CountryFile(
        country=Country(iso_code="XX", name="Testland"),
        hotlines=[_valid_hotline()],
        metadata=Metadata(
            last_updated=date(2026, 1, 1),
            verification_status=VerificationStatus.VERIFIED,
        ),
    )
    dumped = cf.model_dump(mode="json")
    reloaded = CountryFile.model_validate(dumped)
    assert reloaded.country.iso_code == "XX"
    assert len(reloaded.hotlines) == 1
