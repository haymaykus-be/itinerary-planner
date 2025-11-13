import json
import os
from typing import List, Dict, Any
from models.schemas import FlightOption, HotelOption, Activity, DayPlan, ItineraryResponse
import random

class MockDataLoader:
    _airport_details_map: Dict[str, Dict[str, Any]] = {}
    
    # List of major airlines for flight generation
    _airlines = [
        "Air France", "British Airways", "Lufthansa", "Delta Air Lines",
        "United Airlines", "American Airlines", "KLM", "Swiss Air",
        "Qatar Airways", "Emirates", "Singapore Airlines", "Cathay Pacific"
    ]

    @staticmethod
    def _load_json_file(filename: str) -> Dict[str, Any]:
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mock_data', filename)
        with open(file_path, 'r') as f:
            return json.load(f)

    @staticmethod
    def _load_airport_details_map():
        if not MockDataLoader._airport_details_map:
            MockDataLoader._airport_details_map = MockDataLoader._load_json_file('airport_details_map.json')

    @staticmethod
    def get_country_from_airport_code(airport_code: str) -> str | None:
        MockDataLoader._load_airport_details_map()
        return MockDataLoader._airport_details_map.get(airport_code.upper(), {}).get('country')

    @staticmethod
    def get_airport_fullname(airport_code: str) -> str | None:
        MockDataLoader._load_airport_details_map()
        return MockDataLoader._airport_details_map.get(airport_code.upper(), {}).get('name')

    @staticmethod
    def _get_airport_code_for_city(city: str) -> str:
        """Convert city name to primary airport code."""
        city_to_airport = {
            "NEW YORK": "JFK",
            "PARIS": "CDG",
            "LONDON": "LHR",
            "TOKYO": "NRT",
            "DUBAI": "DXB",
            "SINGAPORE": "SIN",
            "HONG KONG": "HKG",
            "SYDNEY": "SYD",
            "LOS ANGELES": "LAX",
            "CHICAGO": "ORD",
            "MIAMI": "MIA",
            "TORONTO": "YYZ",
            "VANCOUVER": "YVR",
            "AMSTERDAM": "AMS",
            "FRANKFURT": "FRA",
            "ROME": "FCO",
            "MADRID": "MAD",
            "BARCELONA": "BCN",
            "BERLIN": "BER",
            "MUNICH": "MUC"
        }
        return city_to_airport.get(city.upper())

    @staticmethod
    def get_mock_flights(origin: str = None, destination: str = None, budget: float = None, return_flight: bool = True) -> Dict[str, List[FlightOption]]:
        """
        Get flights for both outbound and return journeys.
        Returns a dictionary with 'outbound' and 'return' flights.
        """
        data = MockDataLoader._load_json_file('flights.json')
        all_flights_raw = [FlightOption(**flight) for flight in data['flights']]
        
        # Split budget between outbound and return if needed
        flight_budget = budget * 0.5 if budget and return_flight else budget
        
        # Convert input to uppercase
        origin = origin.upper() if origin else None
        destination = destination.upper() if destination else None
        
        def generate_flight(from_city: str, to_city: str, budget: float = None) -> FlightOption:
            """Helper function to generate a flight with proper airport codes"""
            if budget:
                min_price = budget * 0.4
                max_price = budget * 0.95
                price = round(random.uniform(min_price, max_price), 2)
            else:
                price = round(random.uniform(300, 1200), 2)
            
            duration_hours = random.randint(6, 15)
            duration_mins = random.choice([0, 15, 30, 45])
            duration = f"{duration_hours}h {duration_mins}m"
            
            # Convert city names to airport codes
            departure_code = (
                "JFK" if from_city.upper() == "NEW YORK" else
                "CDG" if from_city.upper() == "PARIS" else
                MockDataLoader._get_airport_code_for_city(from_city) or from_city
            )
            
            arrival_code = (
                "JFK" if to_city.upper() == "NEW YORK" else
                "CDG" if to_city.upper() == "PARIS" else
                MockDataLoader._get_airport_code_for_city(to_city) or to_city
            )
            
            return FlightOption(
                airline=random.choice(MockDataLoader._airlines),
                price=price,
                duration=duration,
                stops=random.randint(0, 2),
                departure=departure_code,
                arrival=arrival_code,
                departure_fullname=(
                    MockDataLoader.get_airport_fullname(departure_code) or
                    "John F. Kennedy International Airport" if departure_code == "JFK" else
                    "Charles de Gaulle Airport" if departure_code == "CDG" else
                    f"{departure_code} International Airport"
                ),
                arrival_fullname=(
                    MockDataLoader.get_airport_fullname(arrival_code) or
                    "John F. Kennedy International Airport" if arrival_code == "JFK" else
                    "Charles de Gaulle Airport" if arrival_code == "CDG" else
                    f"{arrival_code} International Airport"
                )
            )
        
        # Generate outbound flights
        outbound_flights = []
        for _ in range(5):
            flight = generate_flight(origin, destination, flight_budget)
            outbound_flights.append(flight)
        
        # Sort outbound flights by price
        outbound_flights.sort(key=lambda x: x.price)
        # Generate return flights if requested
        return_flights = []
        if return_flight:
            for _ in range(5):
                flight = generate_flight(destination, origin, flight_budget)
                return_flights.append(flight)
            # Sort return flights by price
            return_flights.sort(key=lambda x: x.price)
        
        return {
            "outbound": outbound_flights[:10],
            "return": return_flights[:10]
        }

    @staticmethod
    def get_mock_hotels(destination: str = None, budget: float = None, mood: str = "cultural") -> List[HotelOption]:
        data = MockDataLoader._load_json_file('hotels.json')
        all_hotels = [HotelOption(**hotel) for hotel in data['hotels']]

        matching_hotels = []

        # Define hotel categories based on mood
        mood_categories = {
            "luxury": ["luxury"],  # Only luxury hotels
            "romantic": ["luxury", "upscale"],  # Luxury and upscale hotels
            "cultural": ["upscale", "midscale"],  # Mix of upscale and midscale
            "adventure": ["midscale", "economy"],  # More affordable options
            "relaxation": ["upscale", "midscale"],  # Comfortable but not necessarily luxury
            "family": ["midscale", "economy"]  # Family-friendly options
        }

        # Get appropriate categories for the mood
        target_categories = mood_categories.get(mood.lower(), ["midscale"])

        # 1. First filter by category and budget
        budget_filtered = []
        for hotel in all_hotels:
            if hasattr(hotel, 'category') and hotel.category in target_categories:
                if budget is None or hotel.price_per_night <= budget:
                    budget_filtered.append(hotel)

        # If we don't have enough hotels in the preferred categories, include hotels from adjacent categories
        if len(budget_filtered) < 5:
            # Add hotels from other categories based on rating and price
            for hotel in all_hotels:
                if hotel not in budget_filtered:
                    if budget is None or hotel.price_per_night <= budget:
                        if mood.lower() == "luxury" and hotel.rating >= 4.5:
                            budget_filtered.append(hotel)
                        elif mood.lower() in ["romantic", "relaxation"] and hotel.rating >= 4.0:
                            budget_filtered.append(hotel)

        # 2. Then filter by destination
        if destination:
            for hotel in budget_filtered:
                if destination.lower() in hotel.location.lower():
                    matching_hotels.append(hotel)
        else:
            matching_hotels = budget_filtered

        # 3. If we have fewer than 5 matches and have a destination, generate additional hotels
        if len(matching_hotels) < 5 and destination:
            num_to_generate = 5 - len(matching_hotels)
            for _ in range(num_to_generate):
                if budget:
                    # Simple range from 40% to 95% of budget
                    min_price = budget * 0.4  # 40% of budget
                    max_price = budget * 0.95  # 95% of budget
                    price = round(random.uniform(min_price, max_price), 2)
                else:
                    # No budget constraint
                    price = round(random.uniform(100, 500), 2)

                hotel_names = ["Grand Hotel", "Luxury Suites", "City Center Inn", "Plaza Hotel", "Royal Palace Hotel", 
                             "Boutique Hotel", "Riverside Lodge", "Metropolitan Hotel", "Park View Hotel", "Ocean Breeze Resort"]
                amenities = ["WiFi", "Pool", "Spa", "Restaurant", "Gym", "Room Service", "Bar", "Business Center", 
                           "Parking", "Airport Shuttle", "Concierge", "24/7 Front Desk"]

                new_hotel = HotelOption(
                    name=f"{random.choice(hotel_names)} {destination}",
                    price_per_night=price,
                    rating=round(random.uniform(3.5, 5.0), 1),
                    location=f"{destination} City Center",
                    amenities=random.sample(amenities, random.randint(3, 6))
                )
                matching_hotels.append(new_hotel)

        # 4. Apply final quality filters based on mood
        if mood.lower() == "luxury":
            matching_hotels = [h for h in matching_hotels if h.rating >= 4.5]
        elif mood.lower() in ["romantic", "relaxation"]:
            matching_hotels = [h for h in matching_hotels if h.rating >= 4.0]

        # 5. Sort hotels optimally based on mood
        if mood.lower() == "luxury":
            # For luxury, prioritize higher-rated hotels when prices are similar
            matching_hotels.sort(key=lambda x: (-(x.rating / 5.0) * 0.7 + (x.price_per_night / budget if budget else 0) * 0.3))
        else:
            # For other moods, sort primarily by price
            matching_hotels.sort(key=lambda x: x.price_per_night)

        result = matching_hotels[:10]
        return result

    @staticmethod
    def get_mock_itinerary(
        origin: str = None,
        destination: str = None,
        duration_days: int = 3,
        budget: str = "luxury"
    ) -> ItineraryResponse:
        data = MockDataLoader._load_json_file('itinerary.json')
        
        # Convert the data to our Pydantic models
        return ItineraryResponse(
            summary=data['summary'],
            total_estimated_cost=data['total_estimated_cost'],
            flights=[FlightOption(**f) for f in data['flights']],
            hotels=[HotelOption(**h) for h in data['hotels']],
            daily_plan=[DayPlan(day=idx+1, activities=[Activity(**a) for a in day.get('activities', [])]) for idx, day in enumerate(data.get('daily_plan', []))],
            recommendations=data['recommendations']
        )