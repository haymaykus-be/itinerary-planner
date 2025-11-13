
import requests
import os
from typing import List, Dict
from config.settings import Settings
from services.cache_manager import CacheManager

class GeoapifyClient:
    def __init__(self):
        settings = Settings()
        self.api_key = settings.GEOAPIFY_API_KEY
        self.base_url = "https://api.geoapify.com/v2/places"
        self.cache = CacheManager()
    
    async def search_places(self, categories: List[str], lat: float, lon: float, radius: int = 5000, limit: int = 20):
        cache_key = f"places_{'_'.join(categories)}_{lat}_{lon}_{radius}_{limit}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data

        categories_str = ",".join(categories)
        
        params = {
            "categories": categories_str,
            "filter": f"circle:{lon},{lat},{radius}",
            "bias": f"proximity:{lon},{lat}",
            "limit": limit,
            "apiKey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        places = []
        for feature in data.get("features", []):
            props = feature["properties"]
            places.append({
                "name": props.get("name"),
                "category": props.get("categories", [""])[0],
                "address": props.get("formatted"),
                "distance": props.get("distance"),
                "rating": props.get("rate", {}).get("rating"),
                "website": props.get("website"),
                "opening_hours": props.get("opening_hours")
            })
        
        self.cache.set(cache_key, places)
        return places
    
    async def get_place_categories_by_mood(self, mood: str) -> List[str]:
        cache_key = f"mood_categories_{mood}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data

        mood_categories = {
            "adventure": ["adventure", "natural", "sport", "mountain", "water"],
            "romantic": ["entertainment", "catering.restaurant", "tourism", "adult"],
            "family": ["entertainment", "catering", "tourism", "leisure", "amusement"],
            "relaxing": ["leisure", "wellness", "natural", "catering.cafe"],
            "cultural": ["tourism", "cultural", "religion", "museum", "historical"]
        }
        self.cache.set(cache_key, mood_categories.get(mood, ["tourism", "catering", "entertainment"]))
        return mood_categories.get(mood, ["tourism", "catering", "entertainment"])