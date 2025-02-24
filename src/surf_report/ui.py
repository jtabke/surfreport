from collections import defaultdict

from surf_report.utils.helpers import convert_timestamp_to_datetime


def display_regions(regions, verbose=False):
    """Displays a list of regions to the user."""
    print("\nSelect a Region:")
    for i, region in enumerate(regions):
        if isinstance(region, dict):
            # Support legacy dictionary format
            name = region.get("name", "Unknown")
            region_type = region.get("type", "Unknown")
            subregion = region.get("subregion", "Not specified")
            spot = region.get("spot", "Not specified")
            region_id = region.get("_id", "Unknown")
        else:
            # Use the new `Region` dataclass format
            name = region.name
            region_type = region.type
            subregion = region.subregion or "Not specified"
            spot = region.spot or "Not specified"
            region_id = region.id

        if verbose:
            print(
                f"{i + 1}. {name} ({region_type}) [ID: {region_id}] [subregionID: {subregion}] [spotID: {spot}]"
            )
        else:
            print(f"{i + 1}. {name} ({region_type})")

    print("0. Back to Main Menu")


def get_user_choice(regions):
    """Gets the user's choice from the list of regions."""
    while True:
        try:
            choice = int(input("Enter your choice: "))
            if 0 <= choice <= len(regions):
                return choice
            else:
                print("Invalid choice. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def display_region_overview(region_overview):
    """Displays the region overview."""
    highlights = (
        region_overview.get("data", {}).get("forecastSummary", {}).get("highlights", [])
    )
    print("\nRegion Overview:")
    if highlights:
        for highlight in highlights:
            print(f"* {highlight}")
        print(region_overview.get("data", {}).get("forecastSummary", {}))


def display_spot_forecast(spot_forecast):
    """Displays spot forecast observations."""
    if spot_forecast is None:
        print("\nNo forecast data available.")
        return

    # Correctly access the `forecast_data` attribute
    forecast_data = spot_forecast.forecast_data  # This is now a dictionary

    # Extract conditions safely
    conditions = forecast_data.get("data", {}).get("conditions", {})

    print("\nSpot Forecast:")
    if conditions:
        for forecast in conditions:
            forecast_day = forecast.get("forecastDay", "Forecast day not found.")
            print(f"\n{forecast_day}")
            print(f"* {forecast.get('headline', 'No headline found.')}")
            print(f"* {forecast.get('observation', 'No observation found.')}")
    else:
        print("No conditions data available.")


def display_spot_report(spot_report):
    """Displays spot report grouped by day for all endpoints."""
    if spot_report is None:
        print("\nNo spot report available.")
        return

    # Correctly access the `report_data` attribute
    spot_report = spot_report.report_data
    # Step 1: Extract data from all endpoints
    wave_data = spot_report.get("wave", {}).get("data", {}).get("wave", [])
    weather_data = spot_report.get("weather", {}).get("data", []).get("weather", [])
    tides_data = spot_report.get("tides", {}).get("data", []).get("tides", [])
    wind_data = spot_report.get("wind", {}).get("data", []).get("wind", [])
    swells_data = spot_report.get("swells", {}).get("data", []).get("swells", [])
    sunlight_data = spot_report.get("sunlight", {}).get("data", []).get("sunlight", [])

    # Step 2: Group data by day
    grouped_data = defaultdict(
        lambda: {
            "surf": [],
            "weather": [],
            "tides": [],
            "wind": [],
            "swells": [],
            "sunlight": [],
        }
    )

    # Group wave data
    for wave in wave_data:
        timestamp = wave.get("timestamp")
        utc_offset = wave.get("utcOffset")
        if timestamp is not None:
            date_str = convert_timestamp_to_datetime(timestamp, utc_offset).split()[
                1
            ]  # Extract date (e.g., "2024-01-10")
            grouped_data[date_str]["surf"].append(wave.get("surf"))

    # Group wave data
    for swell in swells_data:
        timestamp = swell.get("timestamp")
        utc_offset = swell.get("utcOffset")
        if timestamp is not None:
            date_str = convert_timestamp_to_datetime(timestamp, utc_offset).split()[
                1
            ]  # Extract date (e.g., "2024-01-10")
            grouped_data[date_str]["swells"].extend(swell.get("swells", []))

    # Group weather data
    for weather in weather_data:
        timestamp = weather.get("timestamp")
        utc_offset = weather.get("utcOffset")
        if timestamp is not None:
            date_str = convert_timestamp_to_datetime(timestamp, utc_offset).split()[
                1
            ]  # Extract date
            grouped_data[date_str]["weather"].append(
                {
                    "temperature": weather.get("temperature"),
                    "condition": weather.get("condition"),
                }
            )

    # Group tides data
    for tide in tides_data:
        timestamp = tide.get("timestamp")
        utc_offset = tide.get("utcOffset")
        tide_type = tide.get("type")
        if timestamp is not None and tide_type in [
            "HIGH",
            "LOW",
        ]:  # Only include HIGH and LOW tides
            date_str = convert_timestamp_to_datetime(timestamp, utc_offset).split()[
                1
            ]  # Extract date
            time_str = convert_timestamp_to_datetime(timestamp, utc_offset).split()[
                2
            ]  # Extract time (e.g., "12:34:56")
            grouped_data[date_str]["tides"].append(
                {
                    "height": tide.get("height"),
                    "type": tide_type,  # e.g., high tide, low tide
                    "time": time_str,  # e.g., high tide, low tide
                }
            )

    # Group wind data
    for wind in wind_data:
        timestamp = wind.get("timestamp")
        utc_offset = wind.get("utcOffset")
        if timestamp is not None:
            date_str = convert_timestamp_to_datetime(timestamp, utc_offset).split()[
                1
            ]  # Extract date
            grouped_data[date_str]["wind"].append(
                {
                    "speed": wind.get("speed"),
                    "direction": wind.get("direction"),
                    "directionType": wind.get("directionType"),
                }
            )

    # Group sunlight data
    for sunlight in sunlight_data:
        timestamp = sunlight.get("sunrise")  # Use sunrise timestamp for grouping by day
        sunrise_utc_offset = sunlight.get("sunriseUTCOffset")
        dawn_utc_offset = sunlight.get("dawnUTCOffset")
        sunset_utc_offset = sunlight.get("sunsetUTCOffset")
        dusk_utc_offset = sunlight.get("duskUTCOffset")
        if timestamp is not None:
            date_str = convert_timestamp_to_datetime(
                timestamp, sunrise_utc_offset
            ).split()[1]  # Extract date
            grouped_data[date_str]["sunlight"].append(
                {
                    "dawn": convert_timestamp_to_datetime(
                        sunlight.get("dawn"), dawn_utc_offset
                    ).split()[2],  # Extract time
                    "sunrise": convert_timestamp_to_datetime(
                        sunlight.get("sunrise"), sunrise_utc_offset
                    ).split()[2],  # Extract time
                    "sunset": convert_timestamp_to_datetime(
                        sunlight.get("sunset"), sunset_utc_offset
                    ).split()[2],  # Extract time
                    "dusk": convert_timestamp_to_datetime(
                        sunlight.get("dusk"), dusk_utc_offset
                    ).split()[2],  # Extract time
                }
            )

    # Step 3: Sort the grouped data by date
    sorted_dates = sorted(grouped_data.keys())

    # Step 4: Display the grouped data
    for date_str in sorted_dates:
        data = grouped_data[date_str]
        print(f"\n{date_str}")
        print("-----------------------------")

        # Display surf data
        if data["surf"]:
            print("Surf:")
            # We are going to not include the first midnight data point
            for surf in data["surf"][1:]:
                print(
                    f"  Min: {surf.get('min')} FT, Max: {surf.get('max')} FT, Condition: {surf.get('humanRelation')}"
                )

        # Display swells data
        if data["swells"]:
            print("Swells:")
            # We are going to not include the first midnight data point
            for swell in data["swells"][1:]:
                print(
                    f"  Height: {swell.get('height')} FT, Direction: {swell.get('direction')}°, Power: {swell.get('power')}"
                )

        # Display weather data
        if data["weather"]:
            print("Weather:")
            # We are going to not include the first midnight data point
            for weather in data["weather"][1:]:
                print(
                    f"  Temperature: {weather.get('temperature')}°F, Condition: {weather.get('condition')}"
                )

        # Display tides data
        if data["tides"]:
            print("Tides:")
            for tide in data["tides"]:
                print(f"  Height: {tide.get('height')} FT, Type: {tide.get('type')}")

        # Display wind data
        if data["wind"]:
            print("Wind:")
            # We are going to not include the first midnight data point
            for wind in data["wind"][1:]:
                print(
                    f"  Speed: {wind.get('speed')} KTS, Direction: {wind.get('direction')}° {wind.get('directionType')}"
                )

        # Display sunlight data
        if data["sunlight"]:
            print("Sunlight:")
            for sunlight in data["sunlight"]:
                print(
                    f"  Dawn: {sunlight.get('dawn')}, Sunrise: {sunlight.get('sunrise')}, Sunset: {sunlight.get('sunset')}, Dusk: {sunlight.get('dusk')}"
                )

        print("-----------------------------")


def display_combined_spot_report(spot_forecast, spot_report):
    """
    Displays a combined spot report where for each day the overview forecast
    (headline and observation) is shown above the detailed report.
    """
    # Process the overview from spot_forecast
    overview_by_day = {}
    if spot_forecast:
        forecast_data = getattr(spot_forecast, "forecast_data", {})
        # Assume conditions is a list of forecast entries
        conditions = forecast_data.get("data", {}).get("conditions", [])
        for forecast in conditions:
            day = forecast.get("forecastDay", "Unknown Day")
            overview_by_day[day] = {
                "headline": forecast.get("headline", "No headline found."),
                "observation": forecast.get("observation", "No observation found."),
            }
    else:
        print("\nNo overview forecast available.")

    # Process the detailed report from spot_report
    if not spot_report:
        print("\nNo detailed spot report available.")
        return

    report_data = getattr(spot_report, "report_data", {})
    grouped_data = defaultdict(
        lambda: {
            "surf": [],
            "weather": [],
            "tides": [],
            "wind": [],
            "swells": [],
            "sunlight": [],
        }
    )

    # Extract detailed data
    wave_data = report_data.get("wave", {}).get("data", {}).get("wave", [])
    weather_data = report_data.get("weather", {}).get("data", {}).get("weather", [])
    tides_data = report_data.get("tides", {}).get("data", {}).get("tides", [])
    wind_data = report_data.get("wind", {}).get("data", {}).get("wind", [])
    swells_data = report_data.get("swells", {}).get("data", {}).get("swells", [])
    sunlight_data = report_data.get("sunlight", {}).get("data", {}).get("sunlight", [])

    # Group wave data for surf
    for wave in wave_data:
        timestamp = wave.get("timestamp")
        utc_offset = wave.get("utcOffset")
        if timestamp:
            day = convert_timestamp_to_datetime(timestamp, utc_offset).split()[
                1
            ]  # Extract date (e.g., "2024-01-10")
            grouped_data[day]["surf"].append(wave.get("surf"))
            grouped_data[day]["swells"].extend(wave.get("swells", []))

    # Group weather data
    for weather in weather_data:
        timestamp = weather.get("timestamp")
        utc_offset = weather.get("utcOffset")
        if timestamp:
            day = convert_timestamp_to_datetime(timestamp, utc_offset).split()[
                1
            ]  # Extract date (e.g., "2024-01-10")
            grouped_data[day]["weather"].append(
                {
                    "temperature": weather.get("temperature"),
                    "condition": weather.get("condition"),
                }
            )

    # Group tides data (only HIGH and LOW tides)
    for tide in tides_data:
        timestamp = tide.get("timestamp")
        utc_offset = tide.get("utcOffset")
        tide_type = tide.get("type")
        if timestamp and tide_type in ["HIGH", "LOW"]:
            day = convert_timestamp_to_datetime(timestamp, utc_offset).split()[
                1
            ]  # Extract date (e.g., "2024-01-10")
            time_str = convert_timestamp_to_datetime(timestamp, utc_offset).split()[
                2
            ]  # Extract time (e.g., "12:34:56")
            grouped_data[day]["tides"].append(
                {
                    "height": tide.get("height"),
                    "type": tide_type,
                    "time": time_str,
                }
            )

    # Group wind data
    for wind in wind_data:
        timestamp = wind.get("timestamp")
        utc_offset = wind.get("utcOffset")
        if timestamp:
            day = convert_timestamp_to_datetime(timestamp, utc_offset).split()[
                1
            ]  # Extract date (e.g., "2024-01-10")
            grouped_data[day]["wind"].append(
                {
                    "speed": wind.get("speed"),
                    "direction": wind.get("direction"),
                    "directionType": wind.get("directionType"),
                }
            )

    # Group sunlight data
    for sunlight in sunlight_data:
        timestamp = sunlight.get("sunrise")  # Use sunrise timestamp for grouping by day
        sunrise_utc_offset = sunlight.get("sunriseUTCOffset")
        dawn_utc_offset = sunlight.get("dawnUTCOffset")
        sunset_utc_offset = sunlight.get("sunsetUTCOffset")
        dusk_utc_offset = sunlight.get("duskUTCOffset")
        if timestamp is not None:
            date_str = convert_timestamp_to_datetime(
                timestamp, sunrise_utc_offset
            ).split()[1]  # Extract date
            grouped_data[date_str]["sunlight"].append(
                {
                    "dawn": convert_timestamp_to_datetime(
                        sunlight.get("dawn"), dawn_utc_offset
                    ).split()[2],  # Extract time
                    "sunrise": convert_timestamp_to_datetime(
                        sunlight.get("sunrise"), sunrise_utc_offset
                    ).split()[2],  # Extract time
                    "sunset": convert_timestamp_to_datetime(
                        sunlight.get("sunset"), sunset_utc_offset
                    ).split()[2],  # Extract time
                    "dusk": convert_timestamp_to_datetime(
                        sunlight.get("dusk"), dusk_utc_offset
                    ).split()[2],  # Extract time
                }
            )

    # Get the union of all days from both sources
    all_days = set(grouped_data.keys()) | set(overview_by_day.keys())
    for day in sorted(all_days):
        print(f"\n{day}")
        print("=" * 30)

        # Display overview forecast for the day (if available)
        if day in overview_by_day:
            print("Overview Forecast:")
            print(f"  Headline: {overview_by_day[day]['headline']}")
            print(f"  Observation: {overview_by_day[day]['observation']}")
        else:
            print("No overview forecast available for this day.")

        print("-" * 30)
        data = grouped_data.get(day, {})

        # Display surf data
        if data["surf"]:
            print("Surf:")
            # We are going to not include the first midnight data point
            for surf in data["surf"][1:]:
                print(
                    f"  Min: {surf.get('min')} FT, Max: {surf.get('max')} FT, Condition: {surf.get('humanRelation')}"
                )

        # Display swells data
        if data["swells"]:
            print("Swells:")
            # We are going to not include the first midnight data point
            for swell in data["swells"][1:]:
                print(
                    f"  Height: {swell.get('height')} FT, Direction: {swell.get('direction')}°, Power: {swell.get('power')}"
                )

        # Display weather data
        if data["weather"]:
            print("Weather:")
            # We are going to not include the first midnight data point
            for weather in data["weather"][1:]:
                print(
                    f"  Temperature: {weather.get('temperature')}°F, Condition: {weather.get('condition')}"
                )

        # Display tides data
        if data["tides"]:
            print("Tides:")
            for tide in data["tides"]:
                print(f"  Height: {tide.get('height')} FT, Type: {tide.get('type')}")

        # Display wind data
        if data["wind"]:
            print("Wind:")
            # We are going to not include the first midnight data point
            for wind in data["wind"][1:]:
                print(
                    f"  Speed: {wind.get('speed')} KTS, Direction: {wind.get('direction')}° {wind.get('directionType')}"
                )
        # Display detailed sunlight data
        if data.get("sunlight"):
            print("Sunlight:")
            for sunlight in data["sunlight"]:
                print(
                    f"  Dawn: {sunlight.get('dawn')}, Sunrise: {sunlight.get('sunrise')}, Sunset: {sunlight.get('sunset')}, Dusk: {sunlight.get('dusk')}"
                )
        print("=" * 30)
