import argparse


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Surf Region Explorer")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity"
    )
    return parser.parse_args()


def sort_regions(regions):
    return sorted(regions, key=lambda x: x.get("name", "").lower())
