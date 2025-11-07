from types import SimpleNamespace

from surf_report.providers.surfline.ui import display_combined_spot_report


def make_spot_report(load_json_fixture):
    payload = load_json_fixture("surfline/spot_report_endpoints.json")
    return SimpleNamespace(report_data=payload)


def make_spot_forecast(load_json_fixture):
    payload = load_json_fixture("surfline/spot_forecast.json")
    return SimpleNamespace(forecast_data=payload)


def test_display_combined_spot_report_uses_pager(monkeypatch, load_json_fixture):
    called = {}

    def fake_should_use_pager():
        return True

    def fake_page_output(text):
        called["text"] = text

    monkeypatch.setattr(
        "surf_report.providers.surfline.ui.pager.should_use_pager",
        fake_should_use_pager,
    )
    monkeypatch.setattr(
        "surf_report.providers.surfline.ui.pager.page_output",
        fake_page_output,
    )

    display_combined_spot_report(
        make_spot_forecast(load_json_fixture),
        make_spot_report(load_json_fixture),
    )

    assert "Overview Forecast" in called["text"]
    assert "Surf:" in called["text"]


def test_display_combined_spot_report_prints_without_pager(
    monkeypatch, load_json_fixture, capsys
):
    monkeypatch.setattr(
        "surf_report.providers.surfline.ui.pager.should_use_pager",
        lambda: False,
    )

    display_combined_spot_report(
        make_spot_forecast(load_json_fixture),
        make_spot_report(load_json_fixture),
    )

    output = capsys.readouterr().out
    assert "Overview Forecast:" in output
    assert "Surf:" in output
