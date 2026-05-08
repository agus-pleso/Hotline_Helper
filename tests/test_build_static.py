"""Static build smoke test."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.build_static import build


def test_build_full_tree(tmp_path: Path):
    build(tmp_path)
    api = tmp_path / "api" / "v1"

    assert (api / "health.json").exists()
    assert (api / "countries.json").exists()
    assert (api / "countries" / "US.json").exists()
    assert (api / "categories.json").exists()
    assert (api / "categories" / "suicide.json").exists()
    assert (api / "index.json").exists()
    assert (api / "openapi.json").exists()
    assert (tmp_path / "index.html").exists()

    us = json.loads((api / "countries" / "US.json").read_text(encoding="utf-8"))
    assert us["country"]["iso_code"] == "US"
    assert any(h["id"] == "us-988" for h in us["hotlines"])

    suicide = json.loads((api / "categories" / "suicide.json").read_text(encoding="utf-8"))
    assert suicide["category"] == "suicide"
    assert "US" in suicide["results"]
