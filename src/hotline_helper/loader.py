"""Load and validate `data/countries/*.yml` into typed models."""

from __future__ import annotations

import os
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import ValidationError

from hotline_helper.models import CountryFile


class DataError(Exception):
    """Raised when a country file fails to load or validate."""


def data_dir() -> Path:
    """Resolve the dataset root.

    Honors `HOTLINE_HELPER_DATA_DIR` so the same package can serve a
    container's mounted volume, a vendored copy, or the repo's `data/`.
    """
    override = os.environ.get("HOTLINE_HELPER_DATA_DIR")
    if override:
        return Path(override)
    # repo-relative fallback: <repo>/data
    return Path(__file__).resolve().parents[2] / "data"


def country_files_dir() -> Path:
    return data_dir() / "countries"


def iter_country_paths() -> Iterator[Path]:
    """Yield every `data/countries/*.yml` path, sorted by ISO code."""
    return iter(sorted(country_files_dir().glob("*.yml")))


def load_country_file(path: Path) -> CountryFile:
    """Load one YAML file into a validated `CountryFile`."""
    try:
        with path.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
        return CountryFile.model_validate(raw)
    except yaml.YAMLError as e:
        raise DataError(f"YAML parse error in {path.name}: {e}") from e
    except ValidationError as e:
        raise DataError(f"Schema validation failed for {path.name}:\n{e}") from e


@lru_cache(maxsize=1)
def load_all() -> dict[str, CountryFile]:
    """Load every country file, keyed by ISO 3166-1 alpha-2 code.

    Cached for the lifetime of the process. Call `reload()` to refresh.
    """
    out: dict[str, CountryFile] = {}
    for path in iter_country_paths():
        cf = load_country_file(path)
        out[cf.country.iso_code] = cf
    return out


def reload() -> dict[str, CountryFile]:
    """Drop the cache and reload from disk."""
    load_all.cache_clear()
    return load_all()


def get_country(iso_code: str) -> CountryFile | None:
    return load_all().get(iso_code.upper())
