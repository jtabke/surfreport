import logging

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
            print(f"\n{forecast.get("forecastDay", "forecastDay not found.")}")
            print(f"* {forecast.get("headline", "No headline found.")}")
            print(f"* {forecast.get("observation", "No observation found.")}")


def display_spot_report(spot_report):
    """Displays spot surf report"""
    waves = spot_report.get("data", {}).get("surf", {})
    print("\nSurf Report:")
    if waves:
        for wave in waves:
            report_date = convert_timestamp_to_datetime(
                wave.get("timestamp"), wave.get("utcOffset")
            )
            print(f"\n{report_date}")
            print(f"{wave.get("surf").get("min")} - {wave.get("surf").get("max")} FT")
            print(f"{wave.get("surf").get("humanRelation")}")


def handle_search(search: str, verbose=False):
    """Displays a list of search results from the users query."""
    search_results = search_surfline(search)[0]["hits"]["hits"]
    # print out the search results
    if len(search_results) == 0:
        return print(f"No spots found for {search}")
    if len(search_results) == 1:
        breadcrumbs = search_results[0].get("_source").get("breadCrumbs")
        breadcrumb_string = " > ".join(breadcrumbs)
        name = search_results[0].get("_source").get("name")
        type = search_results[0].get("_type")
        spot_id = search_results[0].get("_id")
        if verbose:
            print(f"{breadcrumb_string} > {name} ({type}) [ID: {spot_id}]")
        else:
            print(f"{breadcrumb_string} > {name}")
    else:
        print("\nSelect a spot:")
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
        # TODO: put the breadcrumbs printing into a function
        breadcrumbs = search_results[choice - 1].get("_source").get("breadCrumbs")
        breadcrumb_string = " > ".join(breadcrumbs)
        name = search_results[choice - 1].get("_source").get("name")
        type = search_results[choice - 1].get("_type")
        spot_id = search_results[choice - 1].get("_id")
        if verbose:
            print(f"\n{breadcrumb_string} > {name} ({type}) [ID: {spot_id}]")
        else:
            print(f"\n{breadcrumb_string} > {name}")

    spot_forecast = get_spot_forecast(spot_id)
    spot_report = get_spot_report(spot_id)

    return display_spot_forecast(spot_forecast), display_spot_report(spot_report)


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
