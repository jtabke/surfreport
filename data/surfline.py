import logging

import requests

BASE_URL = "https://services.surfline.com/taxonomy"
OVERVIEW_URL = "https://services.surfline.com/kbyg/regions/overview"


class RegionOverviewError(Exception):
    """Custom exception for region overview errors."""

    pass


class TaxonomyError(Exception):
    """Custom exception for taxonomy errors."""

    pass


def get_region_list(taxonomy_id, max_depth=0):
    params = {"type": "taxonomy", "id": taxonomy_id, "maxDepth": max_depth}
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching taxonomy data: {e}")
        raise TaxonomyError("Failed to fetch taxonomy data") from e


def get_region_overview(region_id):
    params = {"subregionId": region_id}
    try:
        response = requests.get(OVERVIEW_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching region overview: {e}")
        raise RegionOverviewError("Failed to fetch region overview") from e


if __name__ == "__main__":
    earth_id = "58f7ed51dadb30820bb38782"  # Earth as starting point
    try:
        print(get_region_list(earth_id))
    except TaxonomyError as e:
        logging.error(f"Taxonomy error: {e}")
        print(f"Error: {e}")

    la_subregion_id = "58581a836630e24c4487900b"
    try:
        print(get_region_overview(la_subregion_id))
    except RegionOverviewError as e:
        logging.error(f"Region overview error: {e}")
        print(f"Error: {e}")
