import json
import random

airport_details_map_path = 'mock_data/airport_details_map.json'
hotels_json_path = 'mock_data/hotels.json'

with open(airport_details_map_path, 'r') as f:
    airport_details = json.load(f)

# Extract unique countries and some major cities from airport details
cities_and_countries = set()
for code, details in airport_details.items():
    cities_and_countries.add(details['country'])
    if "International Airport" in details['name']:
        city = details['name'].split(" International Airport")[0]
        if "Airport" in city:
            city = city.split(" Airport")[0]
        cities_and_countries.add(city.strip())

# Add popular cities
cities_and_countries.update([
    "Paris", "London", "Rome", "New York City", "Tokyo", "Dubai", "Sydney",
    "Rio de Janeiro", "Barcelona", "Amsterdam", "Singapore", "Hong Kong",
    "Bangkok", "Istanbul", "Venice", "Madrid", "Berlin", "Vienna"
])

destinations = list(cities_and_countries)

# Define hotel categories with their chains and price/rating ranges
hotel_categories = {
    "luxury": {
        "chains": [
            "Four Seasons", "Ritz-Carlton", "Mandarin Oriental", "Peninsula",
            "Shangri-La", "Aman", "Rosewood", "St. Regis", "Park Hyatt",
            "Waldorf Astoria"
        ],
        "price_range": (500, 2000),
        "rating_range": (4.3, 5.0),
        "min_amenities": 5
    },
    "upscale": {
        "chains": [
            "JW Marriott", "Grand Hyatt", "InterContinental", "Westin",
            "Sofitel", "W Hotels", "Kimpton", "Conrad", "Le Meridien"
        ],
        "price_range": (300, 800),
        "rating_range": (4.0, 4.8),
        "min_amenities": 4
    },
    "midscale": {
        "chains": [
            "Hilton", "Marriott", "Hyatt", "Sheraton", "Renaissance",
            "Crowne Plaza", "Radisson", "Novotel", "DoubleTree"
        ],
        "price_range": (150, 400),
        "rating_range": (3.8, 4.5),
        "min_amenities": 3
    },
    "economy": {
        "chains": [
            "Holiday Inn", "Best Western", "Comfort Inn", "Hampton Inn",
            "Ibis", "La Quinta", "Days Inn", "Quality Inn", "Travelodge"
        ],
        "price_range": (50, 200),
        "rating_range": (3.0, 4.2),
        "min_amenities": 2
    }
}

amenities_by_category = {
    "luxury": [
        "WiFi", "Breakfast Included", "Pool", "Spa", "Fitness Center",
        "Fine Dining Restaurant", "Bar & Lounge", "24/7 Room Service",
        "Concierge", "Valet Parking", "Business Center", "Ocean View",
        "City View", "Penthouse Suite", "Private Balcony", "Butler Service",
        "Executive Lounge", "Michelin-Star Restaurant", "Rooftop Bar"
    ],
    "upscale": [
        "WiFi", "Breakfast Included", "Pool", "Spa", "Fitness Center",
        "Restaurant", "Bar", "Room Service", "Concierge", "Parking",
        "Business Center", "City View", "Balcony", "Club Lounge",
        "Airport Shuttle"
    ],
    "midscale": [
        "WiFi", "Breakfast Included", "Pool", "Fitness Center",
        "Restaurant", "Bar", "Room Service", "Parking",
        "Business Center", "Airport Shuttle", "Family Rooms"
    ],
    "economy": [
        "WiFi", "Breakfast Included", "Parking", "Vending Machines",
        "Basic Fitness Room", "Business Corner", "Airport Shuttle",
        "Family Rooms"
    ]
}

def generate_price_per_night(category):
    min_price, max_price = hotel_categories[category]["price_range"]
    # Add location-based price variation (±20%)
    variation = random.uniform(0.8, 1.2)
    price = random.uniform(min_price, max_price) * variation
    return round(price, 2)

def generate_rating(category):
    min_rating, max_rating = hotel_categories[category]["rating_range"]
    return round(random.uniform(min_rating, max_rating), 1)

def select_amenities(category):
    available_amenities = amenities_by_category[category]
    min_amenities = hotel_categories[category]["min_amenities"]
    max_amenities = len(available_amenities)
    num_amenities = random.randint(min_amenities, max(min_amenities + 3, max_amenities - 2))
    return random.sample(available_amenities, num_amenities)

# Generate 500 hotels
generated_hotels = []
for _ in range(500):
    # Select category with weighted distribution
    category = random.choices(
        ["luxury", "upscale", "midscale", "economy"],
        weights=[0.1, 0.2, 0.4, 0.3],  # 10% luxury, 20% upscale, 40% midscale, 30% economy
        k=1
    )[0]
    
    location = random.choice(destinations)
    chain = random.choice(hotel_categories[category]["chains"])
    
    hotel = {
        "name": f"{chain} {location}",
        "price_per_night": generate_price_per_night(category),
        "rating": generate_rating(category),
        "location": location,
        "amenities": select_amenities(category),
        "category": category  # Include category in the data for reference
    }
    generated_hotels.append(hotel)

# Write to hotels.json
with open(hotels_json_path, 'w') as f:
    json.dump({"hotels": generated_hotels}, f, indent=2)
