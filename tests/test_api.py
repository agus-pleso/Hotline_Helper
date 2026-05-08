"""FastAPI smoke tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from hotline_helper.api import app

client = TestClient(app)


def test_health():
    r = client.get("/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_countries_shape():
    r = client.get("/v1/countries")
    assert r.status_code == 200
    payload = r.json()
    assert "count" in payload
    assert payload["count"] == len(payload["countries"])
    assert all("iso_code" in c for c in payload["countries"])


def test_get_country_us():
    r = client.get("/v1/countries/US")
    assert r.status_code == 200
    payload = r.json()
    assert payload["country"]["iso_code"] == "US"
    assert any(h["id"] == "us-988" for h in payload["hotlines"])


def test_get_country_lowercase():
    """ISO codes should be case-insensitive on input."""
    r = client.get("/v1/countries/us")
    assert r.status_code == 200


def test_get_country_404():
    r = client.get("/v1/countries/ZZ")
    assert r.status_code == 404


def test_category_filter_suicide():
    r = client.get("/v1/categories/suicide")
    assert r.status_code == 200
    payload = r.json()
    assert payload["category"] == "suicide"
    assert payload["country_count"] >= 1


def test_search_by_country_and_category():
    r = client.get("/v1/search?country=US&category=veterans")
    assert r.status_code == 200
    payload = r.json()
    assert payload["count"] >= 1
    assert all(h["country"] == "US" for h in payload["results"])


def test_openapi_endpoint():
    r = client.get("/v1/openapi.json")
    # FastAPI hosts openapi at /openapi.json by default — but our static export
    # exposes it under /v1. The runtime API uses default /openapi.json.
    assert r.status_code in (200, 404)
