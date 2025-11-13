import json
import random
import math
from typing import Dict, Tuple

# File paths
airport_details_map_path = 'mock_data/airport_details_map.json'
flights_json_path = 'mock_data/flights.json'

# Load airport details
with open(airport_details_map_path, 'r') as f:
    airport_details = json.load(f)

# Major airline alliances and their member airlines
airline_alliances = {
    "Star Alliance": [
        "United Airlines", "Lufthansa", "Air Canada", "ANA", "Singapore Airlines",
        "Turkish Airlines", "Swiss Air", "Austrian Airlines", "LOT Polish Airlines",
        "TAP Air Portugal", "Air New Zealand"
    ],
    "Oneworld": [
        "American Airlines", "British Airways", "Qantas", "Cathay Pacific",
        "Japan Airlines", "Qatar Airways", "Finnair", "Iberia", "Malaysia Airlines"
    ],
    "SkyTeam": [
        "Delta Air Lines", "Air France", "KLM", "Korean Air", "China Airlines",
        "Aeroméxico", "Alitalia", "Vietnam Airlines", "China Eastern"
    ],
    "Independent": [
        "Emirates", "Etihad Airways", "Virgin Atlantic", "Norwegian Air",
        "Ryanair", "EasyJet", "Southwest Airlines", "JetBlue"
    ]
}

# Flatten airline list while preserving alliance grouping
airlines = [(airline, alliance) for alliance, members in airline_alliances.items() 
            for airline in members]

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers

    # Convert coordinates to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def get_route_category(distance: float) -> str:
    """
    Categorize route based on distance.
    """
    if distance <= 1500:  # ~2 hours flight
        return "short_haul"
    elif distance <= 3500:  # ~4-5 hours flight
        return "medium_haul"
    else:
        return "long_haul"

def generate_price(distance: float, alliance: str, stops: int) -> float:
    """
    Generate realistic price based on distance, airline alliance, and number of stops.
    """
    # Base price calculations (USD per km)
    base_rates = {
        "short_haul": (0.15, 0.25),    # $150-250 per 1000km
        "medium_haul": (0.12, 0.20),   # $120-200 per 1000km
        "long_haul": (0.10, 0.18),     # $100-180 per 1000km
    }
    
    # Alliance multipliers
    alliance_multipliers = {
        "Star Alliance": (1.1, 1.3),
        "Oneworld": (1.1, 1.3),
        "SkyTeam": (1.0, 1.2),
        "Independent": (0.8, 1.0)  # Generally cheaper
    }
    
    # Stops discount/premium
    stops_multipliers = {
        0: (1.1, 1.3),    # Direct flight premium
        1: (0.9, 1.1),    # Standard pricing
        2: (0.7, 0.9)     # Multiple stops discount
    }
    
    route_category = get_route_category(distance)
    base_min, base_max = base_rates[route_category]
    alliance_min, alliance_max = alliance_multipliers[alliance]
    stops_min, stops_max = stops_multipliers[stops]
    
    # Calculate price range
    min_price = distance * base_min * alliance_min * stops_min
    max_price = distance * base_max * alliance_max * stops_max
    
    # Add some randomization within the range
    price = random.uniform(min_price, max_price)
    
    # Round to nearest 0.01
    return round(price, 2)

def generate_duration(distance: float, stops: int) -> str:
    """
    Generate realistic flight duration based on distance and stops.
    """
    # Average commercial aircraft speed: ~850 km/h
    base_hours = distance / 850
    
    # Add time for each stop (1-2 hours per stop)
    stop_hours = sum(random.uniform(1, 2) for _ in range(stops))
    
    # Add some variation for routes/winds/etc
    variation = random.uniform(-0.5, 1)
    
    total_hours = base_hours + stop_hours + variation
    hours = int(total_hours)
    minutes = int((total_hours - hours) * 60)
    
    # Round minutes to nearest 5
    minutes = round(minutes / 5) * 5
    
    return f"{hours}h {minutes:02d}m"

# Generate 500 flights
generated_flights = []
for _ in range(500):
    # Select random origin and destination airports
    origin_code = random.choice(list(airport_details.keys()))
    destination_code = random.choice(list(airport_details.keys()))
    
    while destination_code == origin_code:  # Ensure different airports
        destination_code = random.choice(list(airport_details.keys()))
    
    # Get airport details
    origin_details = airport_details[origin_code]
    dest_details = airport_details[destination_code]
    
    # Calculate distance
    distance = calculate_distance(
        float(origin_details['latitude']),
        float(origin_details['longitude']),
        float(dest_details['latitude']),
        float(dest_details['longitude'])
    )
    
    # Determine number of stops based on distance
    if distance <= 1500:  # Short haul
        stops_weights = [0.7, 0.25, 0.05]  # 70% direct, 25% 1 stop, 5% 2 stops
    elif distance <= 3500:  # Medium haul
        stops_weights = [0.4, 0.5, 0.1]   # 40% direct, 50% 1 stop, 10% 2 stops
    else:  # Long haul
        stops_weights = [0.2, 0.6, 0.2]   # 20% direct, 60% 1 stop, 20% 2 stops
    
    num_stops = random.choices([0, 1, 2], weights=stops_weights, k=1)[0]
    
    # Select airline and get its alliance
    airline, alliance = random.choice(airlines)
    
    # Generate flight details
    flight = {
        "airline": airline,
        "price": generate_price(distance, alliance, num_stops),
        "duration": generate_duration(distance, num_stops),
        "stops": num_stops,
        "departure": origin_code,
        "arrival": destination_code,
        "departure_fullname": origin_details['name'],
        "arrival_fullname": dest_details['name'],
        "distance_km": round(distance, 2)
    }
    generated_flights.append(flight)

# Write to flights.json
with open(flights_json_path, 'w') as f:
    json.dump({"flights": generated_flights}, f, indent=2)
