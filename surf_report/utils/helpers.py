import argparse


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Surf Region Explorer")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity"
    )
    parser.add_argument("-s", "--search", action="store_true", help="Search for spot")
    parser.add_argument(
        "search_string",
        type=str,
        default=None,
        nargs="?",
        help="An optional string value passed from the CLI",
    )
    return parser.parse_args()


def sort_regions(regions):
    """Sort list of regions alphabetically."""
    return sorted(regions, key=lambda x: x.get("name", "").lower())
