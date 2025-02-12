from typing import List, Optional

import requests

from surf_report.providers.surfline_models import (
    Region,
    SpotForecast,
    SpotReport,
    SurflineSearchResult,
)
from surf_report.utils.logger import logger

BASE_URL = "https://services.surfline.com/taxonomy"
OVERVIEW_URL = "https://services.surfline.com/kbyg/regions/overview"
SEARCH_URL = "https://services.surfline.com/search/site"
SPOT_FORECAST_URL = "https://services.surfline.com/kbyg/spots/forecasts/conditions"
KBYG_URL = "https://services.surfline.com/kbyg/spots/forecasts"


class SurflineAPI:
    def __init__(self):
        logger.info("Initializing SurflineAPI")

    def search_surfline(self, query: str) -> List[SurflineSearchResult]:
        """Search for a query on the Surfline API and return structured data."""
        params = {"q": query, "querySize": 5, "suggestionSize": 5}
        try:
            response = requests.get(SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()

            # Debugging: Print the structure of API response
            logger.debug(f"API Response: {data}")

            if not isinstance(data, list):
                logger.error("Unexpected non-list response from Surfline API.")
                return []

            # Find the first valid result with "hits"
            valid_hits = []
            for entry in data:
                if (
                    "hits" in entry
                    and "hits" in entry["hits"]
                    and entry["hits"]["total"] > 0
                ):
                    valid_hits = entry["hits"]["hits"]
                    break  # Stop after finding the first valid result

            if not valid_hits:
                logger.info("No matching surf spots found.")
                return []

            # Convert raw JSON data to `SurflineSearchResult`
            search_results = [
                SurflineSearchResult(
                    id=item["_id"],
                    name=item["_source"]["name"],
                    breadcrumbs=item["_source"].get("breadCrumbs", []),
                    type=item["_type"],
                )
                for item in valid_hits
            ]

            return search_results

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching search data: {e}")
            return []

    def get_region_list(self, taxonomy_id: str, max_depth: int = 0) -> List[Region]:
        """Get a list of regions from the Surfline API and return structured data."""
        params = {"type": "taxonomy", "id": taxonomy_id, "maxDepth": max_depth}
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            raw_data = response.json()["contains"]

            # Convert raw JSON data to `Region`
            regions = [
                Region(
                    id=item["_id"],
                    name=item["name"],
                    type=item["type"],
                    subregion=item.get("subregion"),
                    spot=item.get("spot"),
                )
                for item in raw_data
            ]

            return regions

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Error fetching taxonomy data for taxonomy ID {taxonomy_id}: {e}"
            )
            return []

    def get_region_overview(self, region_id: str) -> Optional[dict]:
        """Get the overview of a region."""
        params = {"subregionId": region_id}
        try:
            response = requests.get(OVERVIEW_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Error fetching region overview for region ID {region_id}: {e}"
            )
            return None

    def get_spot_forecast(self, spot_id: str, days: int = 5) -> Optional[SpotForecast]:
        """Fetch and return a structured spot forecast."""
        params = {"spotId": spot_id, "days": days}
        try:
            response = requests.get(SPOT_FORECAST_URL, params=params)
            response.raise_for_status()
            return SpotForecast(
                spot_id=spot_id, days=days, forecast_data=response.json()
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching spot forecast for spot ID {spot_id}: {e}")
            return None

    def get_spot_report(
        self, spot_id: str, days: int = 3, intervalHours: int = 24
    ) -> Optional[SpotReport]:
        """Fetch and return a structured spot report."""
        endpoints = [
            "/wave",
            "/weather",
            "/tides",
            "/surf",
            "/sunlight",
            "/wind",
            "/swells",
        ]
        params = {"spotId": spot_id, "days": days, "intervalHours": intervalHours}
        surf_report = {}

        for endpoint in endpoints:
            try:
                response = requests.get(KBYG_URL + endpoint, params=params)
                response.raise_for_status()
                surf_report[endpoint[1:]] = response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching spot report for spot ID {spot_id}: {e}")
                surf_report[endpoint[1:]] = None

        return SpotReport(spot_id=spot_id, days=days, report_data=surf_report)
