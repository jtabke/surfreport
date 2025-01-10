import logging
from collections import defaultdict

from surf_report.data.surfline import (
    get_region_list,
    get_region_overview,
    get_spot_forecast,
    get_spot_report,
    search_surfline,
)
from surf_report.utils.helpers import (
    convert_timestamp_to_datetime,
    parse_arguments,
    sort_regions,
)

# Constants
LOG_LEVEL = logging.NOTSET
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE = "error.log"
LOG_FILE_MODE = "a"

# Logger configuration
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    filename=LOG_FILE,
    filemode=LOG_FILE_MODE,
)


def display_regions(regions, verbose=False):
    """Displays a list of regions to the user."""
    print("\nSelect a Region:")
    for i, region in enumerate(regions):
        if verbose:
            subregion = region.get("subregion", "Not specified")
            spot = region.get("spot", "Not specified")
            print(
                f"{i + 1}. {region['name']} ({region['type']}) [ID: {region['_id']}] [subregionID: {subregion}] [spotID: {spot}]"
            )
        else:
            print(f"{i + 1}.  {region['name']} ({region['type']})")
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
    """Displays spot forecast observations"""
    conditions = spot_forecast.get("data", {}).get("conditions", {})
    print("\nSpot Forecast:")
    if conditions:
        for forecast in conditions:
            forecast_day = forecast.get("forecastDay", "forecastDay not found.")
            print(f"\n{forecast_day}")
            print(f"* {forecast.get("headline", "No headline found.")}")
            print(f"* {forecast.get("observation", "No observation found.")}")


def display_spot_report(spot_report):
    """Displays spot report grouped by day for all endpoints."""
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
        if timestamp is not None:
            date_str = convert_timestamp_to_datetime(timestamp, -8).split()[
                1
            ]  # Extract date (e.g., "2024-01-10")
            grouped_data[date_str]["surf"].append(wave.get("surf"))
            grouped_data[date_str]["swells"].extend(wave.get("swells", []))

    # Group weather data
    for weather in weather_data:
        timestamp = weather.get("timestamp")
        if timestamp is not None:
            date_str = convert_timestamp_to_datetime(timestamp, -8).split()[
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
        tide_type = tide.get("type")
        if timestamp is not None and tide_type in [
            "HIGH",
            "LOW",
        ]:  # Only include HIGH and LOW tides
            date_str = convert_timestamp_to_datetime(timestamp, -8).split()[
                1
            ]  # Extract date
            time_str = convert_timestamp_to_datetime(timestamp, -8).split()[
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
        if timestamp is not None:
            date_str = convert_timestamp_to_datetime(timestamp, -8).split()[
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
        if timestamp is not None:
            date_str = convert_timestamp_to_datetime(timestamp, -8).split()[
                1
            ]  # Extract date
            grouped_data[date_str]["sunlight"].append(
                {
                    "dawn": convert_timestamp_to_datetime(
                        sunlight.get("dawn"), -8
                    ).split()[2],  # Extract time
                    "sunrise": convert_timestamp_to_datetime(
                        sunlight.get("sunrise"), -8
                    ).split()[2],  # Extract time
                    "sunset": convert_timestamp_to_datetime(
                        sunlight.get("sunset"), -8
                    ).split()[2],  # Extract time
                    "dusk": convert_timestamp_to_datetime(
                        sunlight.get("dusk"), -8
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
            for surf in data["surf"]:
                print(
                    f"  Min: {surf.get('min')} FT, Max: {surf.get('max')} FT, Condition: {surf.get('humanRelation')}"
                )

        # Display swells data
        if data["swells"]:
            print("Swells:")
            for swell in data["swells"]:
                print(
                    f"  Height: {swell.get('height')} FT, Direction: {swell.get('direction')}°, Power: {swell.get('power')}"
                )

        # Display weather data
        if data["weather"]:
            print("Weather:")
            for weather in data["weather"]:
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
            for wind in data["wind"]:
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


def handle_search(search: str, verbose=False):
    """Displays a list of search results from the users query."""
    search_results = search_surfline(search)[0]["hits"]["hits"]

    def _join_breadcrumbs(search_result):
        breadcrumbs = search_result.get("_source").get("breadCrumbs")
        breadcrumb_string = " > ".join(breadcrumbs)
        name = search_results[0].get("_source").get("name")
        return breadcrumb_string + " > " + name

    # print out the search results
    if len(search_results) == 0:
        return print(f"No spots found for {search}")
    if len(search_results) == 1:
        breadcrumb_string = _join_breadcrumbs(search_results[0])
        type = search_results[0].get("_type")
        spot_id = search_results[0].get("_id")
        if verbose:
            print(f"{breadcrumb_string} ({type}) [ID: {spot_id}]")
        else:
            print(f"{breadcrumb_string}")
    else:
        print("\nSelect a spot:")
        for i, search_result in enumerate(search_results):
            breadcrumb_string = _join_breadcrumbs(search_result)
            type = search_result.get("_type")
            id = search_result.get("_id")
            if verbose:
                print(f"{i + 1}. {breadcrumb_string} ({type}) [ID: {id}]")
            else:
                print(f"{i + 1}. {breadcrumb_string}")
        print("0. Back to Main Menu")
        # get the selection from the user, maybe add modify search option
        # store and return the selected ID to pass on to application and get forecast
        choice = get_user_choice(search_results)
        breadcrumb_string = _join_breadcrumbs(search_results[choice - 1])
        type = search_results[choice - 1].get("_type")
        spot_id = search_results[choice - 1].get("_id")
        if verbose:
            print(f"\n{breadcrumb_string} ({type}) [ID: {spot_id}]")
        else:
            print(f"\n{breadcrumb_string}")

    return spot_id


def main():
    args = parse_arguments()

    if args.search:
        spot_id = handle_search(args.search_string)
        if spot_id is not None:
            spot_forecast = get_spot_forecast(spot_id)
            spot_report = get_spot_report(spot_id)
            display_spot_forecast(spot_forecast)
            display_spot_report(spot_report)
    else:
        current_region_id = "58f7ed51dadb30820bb38782"
        while True:
            region_data = get_region_list(current_region_id)
            if region_data is not None:
                regions = sort_regions(region_data.get("contains", []))
                display_regions(regions, args.verbose)
                choice = get_user_choice(regions)
                if choice == 0:
                    if "liesIn" in region_data and region_data["liesIn"]:
                        current_region_id = region_data["liesIn"][-1]
                    else:
                        print("You are already at the top level.")
                else:
                    current_region = regions[choice - 1]
                    if current_region["type"] == "subregion":
                        region_overview = get_region_overview(
                            current_region["subregion"]
                        )
                        if region_overview is not None:
                            display_region_overview(region_overview)
                    current_region_id = current_region["_id"]
                    if current_region["type"] == "spot":
                        spot_forecast = get_spot_forecast(current_region["spot"])
                        if spot_forecast is not None:
                            display_spot_forecast(spot_forecast)
            else:
                print("Failed to fetch region data.")
                continue


if __name__ == "__main__":
    main()
