from surf_report.providers.surfline.processing import group_spot_report


def test_group_spot_report_groups_sections(load_json_fixture, monkeypatch):
    report_data = load_json_fixture("surfline/spot_report_endpoints.json")
    fake_times = {
        1001: "Sat 2024-06-01 06:00:00",
        1002: "Sat 2024-06-01 09:00:00",
        1003: "Sat 2024-06-01 12:00:00",
        2001: "Sat 2024-06-01 05:00:00",
        2002: "Sat 2024-06-01 06:30:00",
        2003: "Sat 2024-06-01 19:30:00",
        2004: "Sat 2024-06-01 20:00:00",
    }

    def fake_convert(timestamp, utc_offset):
        return fake_times.get(timestamp, "Sat 2024-06-01 00:00:00")

    monkeypatch.setattr(
        "surf_report.providers.surfline.processing.convert_timestamp_to_datetime",
        fake_convert,
    )

    grouped = group_spot_report(report_data)

    assert "2024-06-01" in grouped
    june_first = grouped["2024-06-01"]
    assert june_first["surf"][0]["time"] == "06:00:00"
    assert len(june_first["swells"]) == 1  # height == 0 entries filtered
    assert june_first["weather"][0]["temperature"] == 65
    assert {t["type"] for t in june_first["tides"]} == {"HIGH", "LOW"}
    assert june_first["wind"][0]["directionType"] == "Offshore"
    assert june_first["sunlight"][0]["sunrise"] == "06:30:00"
