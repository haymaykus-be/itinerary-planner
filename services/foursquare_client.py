


import os
import sys
import httpx
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.settings import Settings


class FoursquareClient:
    def __init__(self):
        settings = Settings()
    
        self.api_key = settings.FOURSQUARE_API_KEY
        self.base_url = "https://api.foursquare.com/v3/places"
        self.headers = {
            "Accept": "application/json",
            "Authorization": self.api_key
        }

    async def search_places(
        self,
        query: str,
        ll: Optional[str] = None, # latitude,longitude e.g., "40.7128,-74.0060"
        near: Optional[str] = None, # city,state,country e.g. "New York,NY,US"
        radius: Optional[int] = None, # in meters
        categories: Optional[str] = None, # comma-separated category IDs
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Searches for places using the Foursquare Places API.
        """
        if not self.api_key:
            print("Foursquare API key not found. Please set FOURSQUARE_API_KEY environment variable.")
            return []

        params = {
            "query": query,
            "limit": limit
        }
        if ll: params["ll"] = ll
        if near: params["near"] = near
        if radius: params["radius"] = radius
        if categories: params["categories"] = categories

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/search", headers=self.headers, params=params)
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()
                return data.get("results", [])
            except httpx.HTTPStatusError as e:
                print(f"Foursquare API HTTP error: {e.response.status_code} - {e.response.text}")
                return []
            except httpx.RequestError as e:
                print(f"Foursquare API request error: {e}")
                return []
            except Exception as e:
                print(f"An unexpected error occurred with Foursquare API: {e}")
                return []

