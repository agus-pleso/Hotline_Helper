"""End-to-end: every shipped country YAML loads and validates."""

from __future__ import annotations

import pytest

from hotline_helper.loader import country_files_dir, iter_country_paths, load_country_file


@pytest.mark.parametrize("path", list(iter_country_paths()), ids=lambda p: p.name)
def test_country_file_loads(path):
    """Every YAML under data/countries/ must parse and validate."""
    cf = load_country_file(path)
    assert cf.country.iso_code == path.stem.upper()


def test_data_dir_present():
    assert country_files_dir().exists(), "data/countries/ missing — run scripts/seed_countries.py"


def test_at_least_one_verified_country():
    """Sanity: the seed includes verified entries."""
    from hotline_helper.loader import load_all

    statuses = {iso: cf.metadata.verification_status for iso, cf in load_all().items()}
    verified = [iso for iso, s in statuses.items() if s in {"verified", "VERIFIED"}]
    assert len(verified) >= 5, f"Expected ≥5 verified countries, got {len(verified)}"


def test_no_duplicate_hotline_ids_within_country():
    from hotline_helper.loader import load_all

    for iso, cf in load_all().items():
        ids = [h.id for h in cf.hotlines]
        assert len(ids) == len(set(ids)), f"Duplicate hotline id in {iso}.yml: {ids}"


def test_verified_countries_have_hotlines():
    from hotline_helper.loader import load_all

    for iso, cf in load_all().items():
        status = (
            cf.metadata.verification_status
            if isinstance(cf.metadata.verification_status, str)
            else cf.metadata.verification_status.value
        )
        if status == "verified":
            assert cf.hotlines, f"{iso}.yml is marked verified but has no hotlines"
