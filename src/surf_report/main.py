from surf_report.providers.surfline import SurflineAPI
from surf_report.ui import (
    display_region_overview,
    display_regions,
    display_spot_forecast,
    display_spot_report,
    get_user_choice,
)
from surf_report.utils.helpers import (
    parse_arguments,
    sort_regions,
)
from surf_report.utils.logger import setup_logger

logger = setup_logger()
surfline = SurflineAPI()


def handle_search(search: str, verbose=False):
    """Displays a list of search results from the users query."""
    search_results = surfline.search_surfline(search)[0]["hits"]["hits"]

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
            spot_forecast = surfline.get_spot_forecast(spot_id, args.days)
            spot_report = surfline.get_spot_report(spot_id, args.days)
            display_spot_forecast(spot_forecast)
            display_spot_report(spot_report)
    else:
        current_region_id = "58f7ed51dadb30820bb38782"
        while True:
            region_data = surfline.get_region_list(current_region_id)
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
                        region_overview = surfline.get_region_overview(
                            current_region["subregion"]
                        )
                        if region_overview is not None:
                            display_region_overview(region_overview)
                    current_region_id = current_region["_id"]
                    if current_region["type"] == "spot":
                        spot_forecast = surfline.get_spot_forecast(
                            current_region["spot"]
                        )
                        if spot_forecast is not None:
                            display_spot_forecast(spot_forecast)
            else:
                print("Failed to fetch region data.")
                continue


if __name__ == "__main__":
    main()
