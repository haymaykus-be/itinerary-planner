
import requests
from typing import List
from models.schemas import FlightOption, HotelOption
from config.settings import Settings
from services.cache_manager import CacheManager

class SerpApiClient:
    def __init__(self):
        settings = Settings()
        self.api_key = settings.SERPAPI_API_KEY
        self.base_url = "https://serpapi.com/search"
        self.cache = CacheManager() # Initialize CacheManager
    
    async def search_flights(self, origin: str, destination: str, depart_date: str, return_date: str = None) -> List[FlightOption]:
        cache_key = f"flights_{origin}_{destination}_{depart_date}_{return_date}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return [FlightOption(**f) for f in cached_data] # Reconstruct objects from cached dicts

        params = {
            "engine": "google_flights",
            "departure_id": self._get_airport_code(origin),
            "arrival_id": self._get_airport_code(destination),
            "outbound_date": depart_date,
            "return_date": return_date,
            "currency": "USD",
            "hl": "en",
            "api_key": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            flights = []
            for flight in data.get("best_flights", [])[:5]:  # Top 5 flights
                flights.append(FlightOption(
                    airline=flight["flights"][0]["airline"],
                    price=flight["price"],
                    duration=flight["total_duration"],
                    stops=len(flight["flights"]) - 1,
                    departure=flight["flights"][0]["departure_airport"]["name"],
                    arrival=flight["flights"][-1]["arrival_airport"]["name"]
                ))
            self.cache.set(cache_key, [f.dict() for f in flights]) # Cache the results
            return flights
        except Exception as e:
            print(f"Flight search error: {e}")
            return []

    async def search_hotels(self, destination: str, check_in: str, check_out: str, budget: str) -> List[HotelOption]:
        cache_key = f"hotels_{destination}_{check_in}_{check_out}_{budget}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return [HotelOption(**h) for h in cached_data] # Reconstruct objects from cached dicts

        budget_map = {"low": 1, "medium": 2, "high": 3, "luxury": 4}
        
        params = {
            "engine": "google_hotels",
            "q": f"hotels in {destination}",
            "check_in_date": check_in,
            "check_out_date": check_out,
            "currency": "USD",
            "hl": "en",
            "api_key": self.api_key
        }
        
        # Implementation similar to flights...
        # return hotels

        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()

            hotels = []
            for hotel in data.get("hotels", [])[:5]: # Top 5 hotels
                hotels.append(HotelOption(
                    name=hotel["name"],
                    price_per_night=hotel.get("price", 0.0),
                    rating=hotel.get("rating", 0.0),
                    location=hotel["address"],
                    amenities=hotel.get("amenities", [])
                ))
            self.cache.set(cache_key, [h.dict() for h in hotels]) # Cache the results
            return hotels
        except Exception as e:
            print(f"Hotel search error: {e}")
            return []
    
    def _get_airport_code(self, city: str) -> str:
        # Simple mapping - in production, use a proper airport database
        codes = {
            "new york": "JFK",
            "paris": "CDG", 
            "london": "LHR",
            "tokyo": "NRT",
            "lagos": "LOS"
        }
        return codes.get(city.lower(), city)