from types import SimpleNamespace

import pytest
import requests

from surf_report.providers.surfline.surfline import SurflineAPI


class DummySession:
    """Simple session stand-in for injecting responses."""

    def __init__(self, responder):
        self._responder = responder
        self.headers = {}

    def get(self, url, params):
        return self._responder(url, params)


class DummyResponse:
    """Lightweight stand-in for `requests.Response`."""

    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test__get_returns_json_on_success():
    api = SurflineAPI(session=DummySession(lambda *_: DummyResponse({"ok": True})))
    response = api._get("https://example.com", {"q": "test"})

    assert response == {"ok": True}


def test__get_returns_none_on_request_exception():
    def responder(*_):
        raise requests.exceptions.RequestException("boom")

    api = SurflineAPI(session=DummySession(responder))
    response = api._get("https://example.com", {"q": "test"})

    assert response is None


def test_search_surfline_returns_structured_results(
    load_json_fixture, monkeypatch
):
    payload = load_json_fixture("surfline/search_success.json")
    api = SurflineAPI()

    def fake_get(url, params):
        assert params["q"] == "mavs"
        return payload

    monkeypatch.setattr(api, "_get", fake_get)

    results = api.search_surfline("mavs")

    assert len(results) == 2
    assert results[0].name == "Mavericks"
    assert results[0].breadcrumbs[-1] == "Mavericks"


def test_search_surfline_handles_no_hits(monkeypatch):
    api = SurflineAPI()
    monkeypatch.setattr(api, "_get", lambda *_, **__: [])

    assert api.search_surfline("nowhere") == []


def test_get_region_list_returns_regions(load_json_fixture, monkeypatch):
    payload = load_json_fixture("surfline/taxonomy_response.json")
    api = SurflineAPI()
    monkeypatch.setattr(api, "_get", lambda *_, **__: payload)

    regions = api.get_region_list("root-id")

    assert len(regions) == 2
    assert regions[0].name == "Northern California"
    assert regions[1].type == "spot"


def test_get_region_list_handles_invalid_response(monkeypatch):
    api = SurflineAPI()
    monkeypatch.setattr(api, "_get", lambda *_, **__: {})

    assert api.get_region_list("root-id") == []


def test_get_spot_forecast_wraps_response(load_json_fixture, monkeypatch):
    payload = load_json_fixture("surfline/spot_forecast.json")
    api = SurflineAPI()
    monkeypatch.setattr(api, "_get", lambda *_, **__: payload)

    forecast = api.get_spot_forecast("spot-1", days=2)

    assert forecast is not None
    assert forecast.spot_id == "spot-1"
    assert forecast.days == 2
    assert forecast.forecast_data["data"]["conditions"][0]["headline"].startswith(
        "Solid"
    )


def test_get_spot_forecast_returns_none_when_missing(monkeypatch):
    api = SurflineAPI()
    monkeypatch.setattr(api, "_get", lambda *_, **__: None)

    assert api.get_spot_forecast("spot-1") is None


def test_get_spot_report_collects_each_endpoint(load_json_fixture, monkeypatch):
    endpoint_payloads = load_json_fixture("surfline/spot_report_endpoints.json")
    api = SurflineAPI()
    requested = []

    def fake_get(url, params):
        slug = url.rsplit("/", 1)[-1]
        requested.append(slug)
        return endpoint_payloads[slug]

    monkeypatch.setattr(api, "_get", fake_get)

    report = api.get_spot_report("spot-99", days=4, interval_hours=3)

    assert report.spot_id == "spot-99"
    assert set(requested) == {"wave", "weather", "tides", "surf", "sunlight", "wind", "swells"}
    assert report.report_data["sunlight"]["data"]["sunlight"]


def test_get_spot_report_handles_partial_failures(load_json_fixture, monkeypatch):
    endpoint_payloads = load_json_fixture("surfline/spot_report_endpoints.json")
    api = SurflineAPI()

    def fake_get(url, params):
        slug = url.rsplit("/", 1)[-1]
        if slug == "wind":
            return None
        return endpoint_payloads[slug]

    monkeypatch.setattr(api, "_get", fake_get)

    report = api.get_spot_report("spot-99")

    assert report.report_data["wind"] is None
    assert report.report_data["wave"]["data"]["wave"][0]["surf"]["min"] == 2
