import logging

from data.surfline import (
    get_region_list,
    get_region_overview,
    get_spot_forecast,
    search_surfline,
)
from utils.helpers import parse_arguments, sort_regions

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
            print(f"{i + 1}. {region['name']} ({region['type']}) [ID: {region['_id']}]")
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
        print(
            region_overview.get("data", {})
            .get("forecastSummary", {})
            .get("shortTermForecast", "No short term forecast available.")
        )


def display_spot_forecast(spot_forecast):
    """Displays spot forecast observations"""
    conditions = spot_forecast.get("data", {}).get("conditions", {})
    print("\nSpot Forecast:")
    if conditions:
        for forecast in conditions:
            print(f"\n{forecast.get("forecastDay", "forecastDay not found.")}")
            print(f"* {forecast.get("headline", "No headline found.")}")
            print(f"* {forecast.get("observation", "No observation found.")}")


def handle_search(search: str, verbose=False):
    """Displays a list of search results from the users query."""
    print("\nSelect a spot:")
    search_results = search_surfline(search)[0]["hits"]["hits"]
    # print out the search results
    for i, search_result in enumerate(search_results):
        breadcrumbs = search_result.get("_source").get("breadCrumbs")
        breadcrumb_string = " > ".join(breadcrumbs)
        name = search_result.get("_source").get("name")
        type = search_result.get("_type")
        id = search_result.get("_id")
        if verbose:
            print(f"{i + 1}. {breadcrumb_string} > {name} ({type}) [ID: {id}]")
        else:
            print(f"{i + 1}. {breadcrumb_string} > {name}")
    print("0. Back to Main Menu")
    # get the selection from the user, maybe add modify search option
    # store and return the selected ID to pass on to application and get forecast
    choice = get_user_choice(search_results)
    spot_id = search_results[choice - 1].get("_id")

    spot_forecast = get_spot_forecast(spot_id)

    return display_spot_forecast(spot_forecast)


def main():
    args = parse_arguments()

    if args.search:
        handle_search(args.search_string)
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
