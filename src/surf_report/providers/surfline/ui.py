import sys

from surf_report.providers.surfline.processing import (
    group_spot_report,
)


def display_regions(regions, verbose=False):
    """Displays a list of regions to the user."""
    print("\nSelect a Region:")
    for i, region in enumerate(regions, start=1):
        subregion = region.subregion or "Not specified"
        spot = region.spot or "Not specified"
        if verbose:
            print(
                f"{i}. {region.name} ({region.type}) [ID: {region.id}] [subregionID: {subregion}] [spotID: {spot}]"
            )
        else:
            print(f"{i}. {region.name} ({region.type})")
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
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)


def display_region_overview(region_overview):
    """Displays the region overview."""
    forecast_summary = region_overview.get("data", {}).get("forecastSummary", {})
    highlights = forecast_summary.get("highlights", [])
    print("\nRegion Overview:")
    if highlights:
        for highlight in highlights:
            print(f"* {highlight}")
    print(forecast_summary)


def display_spot_forecast(spot_forecast):
    """Displays spot forecast observations."""
    if spot_forecast is None:
        print("\nNo forecast data available.")
        return

    forecast_data = spot_forecast.forecast_data
    conditions = forecast_data.get("data", {}).get("conditions", {})
    print("\nSpot Forecast:")
    if conditions:
        for forecast in conditions:
            day = forecast.get("forecastDay", "Forecast day not found.")
            print(f"\n{day}")
            print(f"* {forecast.get('headline', 'No headline found.')}")
            print(f"* {forecast.get('observation', 'No observation found.')}")
    else:
        print("No conditions data available.")


# Define individual functions for each section of the spot report.
def display_surf(surf_list):
    if surf_list:
        print("Surf:")
        # Optionally skip the first data point if it represents midnight
        for surf in surf_list[1:]:
            print(
                f"  [{surf.get('time')}] Min: {surf.get('min')} FT, Max: {surf.get('max')} FT, Condition: {surf.get('humanRelation')}"
            )


def display_wind(wind_list):
    if wind_list:
        print("Wind:")
        # Optionally skip the first data point if it represents midnight
        for wind in wind_list[1:]:
            print(
                f"  [{wind.get('time')}] Speed: {wind.get('speed')} KTS, Direction: {wind.get('direction')}° {wind.get('directionType')}"
            )


def display_weather(weather_list):
    if weather_list:
        print("Weather:")
        for weather in weather_list[1:]:
            print(
                f"  [{weather.get('time')}] Temperature: {weather.get('temperature')}°F, Condition: {weather.get('condition')}"
            )


def display_tides(tides_list):
    if tides_list:
        print("Tides:")
        for tide in tides_list:
            print(
                f"  [{tide.get('time')}] Height: {tide.get('height')} FT, Type: {tide.get('type')}"
            )


def display_swells(swells_list):
    if swells_list:
        print("Swells:")
        for swell in swells_list:
            if swell.get("time") == "00:00:00":
                continue
            print(
                f"  [{swell.get('time')}] Height: {swell.get('height')} FT, Direction: {swell.get('direction')}°, Power: {swell.get('power')}"
            )


def display_sunlight(sunlight_list):
    if sunlight_list:
        print("Sunlight:")
        for sunlight in sunlight_list:
            print(
                f"  Dawn: {sunlight.get('dawn')}, Sunrise: {sunlight.get('sunrise')}, Sunset: {sunlight.get('sunset')}, Dusk: {sunlight.get('dusk')}"
            )


def display_grouped_data_modular(grouped_data, sections=None):
    """
    Prints the grouped spot report data for each day.
    The sections parameter is a list that can contain any combination of:
    'surf', 'wind', 'weather', 'tides', 'swells', 'sunlight'.
    If sections is None, all sections will be printed.
    """
    # If no sections specified, print everything.
    if sections is None:
        sections = ["surf", "swells", "weather", "tides", "wind", "sunlight"]

    # Map section names to display functions.
    section_functions = {
        "surf": display_surf,
        "wind": display_wind,
        "weather": display_weather,
        "tides": display_tides,
        "swells": display_swells,
        "sunlight": display_sunlight,
    }

    for day in sorted(grouped_data.keys()):
        data = grouped_data[day]
        print(f"\n{day}")
        print("-" * 30)
        for section in sections:
            # Call the display function for the section if it exists.
            if section in section_functions and data.get(section):
                section_functions[section](data[section])


def display_spot_report(spot_report, sections=None):
    """Displays the spot report grouped by day.
    The sections parameter allows printing only specific sections.
    """
    if spot_report is None:
        print("\nNo spot report available.")
        return

    report_data = getattr(spot_report, "report_data", {})
    grouped_data = group_spot_report(report_data)
    display_grouped_data_modular(grouped_data, sections)


def display_combined_spot_report(spot_forecast, spot_report, sections=None):
    """
    Displays a combined spot report where for each day the overview forecast
    is shown above the detailed report. The sections parameter allows printing only
    specific parts of the detailed report.
    """
    overview_by_day = {}
    if spot_forecast:
        forecast_data = getattr(spot_forecast, "forecast_data", {})
        conditions = forecast_data.get("data", {}).get("conditions", [])
        for forecast in conditions:
            day = forecast.get("forecastDay", "Unknown Day")
            overview_by_day[day] = {
                "headline": forecast.get("headline", "No headline found."),
                "observation": forecast.get("observation", "No observation found."),
            }
    else:
        print("\nNo overview forecast available.")

    if not spot_report:
        print("\nNo detailed spot report available.")
        return

    report_data = getattr(spot_report, "report_data", {})
    grouped_data = group_spot_report(report_data)
    all_days = set(grouped_data.keys()) | set(overview_by_day.keys())
    for day in sorted(all_days):
        print(f"\n{day}")
        print("=" * 30)
        if day in overview_by_day:
            print("Overview Forecast:")
            print(f"  Headline: {overview_by_day[day]['headline']}")
            print(f"  Observation: {overview_by_day[day]['observation']}")
        else:
            print("No overview forecast available for this day.")
        print("-" * 30)
        day_data = grouped_data.get(
            day,
            {
                "surf": [],
                "swells": [],
                "weather": [],
                "tides": [],
                "wind": [],
                "sunlight": [],
            },
        )
        # Print only the specified sections.
        display_grouped_data_modular({day: day_data}, sections)
        print("=" * 30)
