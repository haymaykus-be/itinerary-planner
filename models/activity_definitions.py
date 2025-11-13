"""
Activity definitions with realistic costs and durations for different cities and activity types.
"""

from typing import Dict, List, Union
import random

class ActivityDefinitions:
    # Base costs for different activity types (in USD)
    BASE_COSTS = {
        "luxury": {
            "Michelin Star Dining": (200, 400),
            "Private Tour": (150, 300),
            "Spa Treatment": (150, 300),
            "Helicopter Tour": (300, 600),
            "Wine Tasting": (100, 200),
            "Cooking Class": (150, 250),
            "Theater Show": (100, 200),
            "Private Shopping": (0, 0),  # Cost varies by purchases
            "Yacht Experience": (500, 1000),
        },
        "cultural": {
            "Museum Visit": (15, 30),
            "Historical Tour": (30, 60),
            "Art Gallery": (15, 25),
            "Local Market": (0, 20),
            "Cultural Workshop": (40, 80),
            "Temple/Church Visit": (0, 10),
            "Food Tour": (60, 120),
            "Traditional Show": (40, 80),
        },
        "adventure": {
            "Hiking": (20, 50),
            "Bike Tour": (30, 70),
            "Water Sports": (50, 150),
            "Rock Climbing": (40, 80),
            "Zip Lining": (50, 100),
            "Kayaking": (40, 80),
            "Surfing Lesson": (60, 120),
            "Scuba Diving": (100, 200),
        },
        "relaxation": {
            "Spa Day": (80, 200),
            "Beach Time": (0, 20),
            "Yoga Class": (20, 40),
            "Garden Visit": (10, 25),
            "Meditation Session": (30, 60),
            "Thermal Bath": (40, 80),
            "Massage": (60, 150),
            "Scenic Drive": (50, 100),
        },
        "romantic": {
            "Sunset Cruise": (60, 120),
            "Couples Massage": (150, 250),
            "Rooftop Dinner": (100, 200),
            "Wine Tasting": (60, 120),
            "Private Picnic": (50, 100),
            "Dance Class": (50, 100),
            "Cooking Class": (80, 150),
            "Evening Concert": (50, 150),
        },
        "family": {
            "Theme Park": (50, 120),
            "Zoo Visit": (25, 50),
            "Aquarium": (25, 50),
            "Family Workshop": (30, 60),
            "Mini Golf": (20, 40),
            "Science Museum": (20, 40),
            "Water Park": (40, 80),
            "Family Show": (40, 80),
        }
    }

    # City-specific cost multipliers
    CITY_MULTIPLIERS = {
        "New York": 1.5,
        "Tokyo": 1.4,
        "London": 1.4,
        "Paris": 1.3,
        "Singapore": 1.3,
        "Hong Kong": 1.3,
        "Dubai": 1.3,
        "Sydney": 1.2,
        "Los Angeles": 1.2,
        "San Francisco": 1.4,
        "Zurich": 1.5,
        "Oslo": 1.4,
        "Copenhagen": 1.3,
        "Amsterdam": 1.2,
        "default": 1.0  # For cities not listed
    }

    # Typical durations for activities (in hours)
    ACTIVITY_DURATIONS = {
        "short": (1, 2),     # Quick activities
        "medium": (2, 4),    # Half-day activities
        "long": (4, 6),      # Full-day activities
    }

    @classmethod
    def get_activity_cost(cls, activity: str, city: str, category: str = None, budget_per_activity: float = None) -> float:
        """
        Calculate realistic cost for an activity based on type and city, respecting budget constraints.
        """
        # Find the category containing this activity
        if not category:
            category = next(
                (cat for cat, acts in cls.BASE_COSTS.items() if activity in acts),
                "cultural"  # Default to cultural if not found
            )
        
        # Get base cost range
        base_min, base_max = cls.BASE_COSTS.get(category, {}).get(
            activity,
            cls.BASE_COSTS["cultural"]["Museum Visit"]  # Default if not found
        )
        
        # Apply city multiplier
        multiplier = cls.CITY_MULTIPLIERS.get(city, cls.CITY_MULTIPLIERS["default"])
        
        # Calculate cost range
        min_cost = base_min * multiplier
        max_cost = base_max * multiplier
        
        # If budget constraint provided, adjust the range
        if budget_per_activity:
            # Ensure minimum viable experience
            min_viable = min_cost * 0.6  # Allow up to 40% discount on minimum
            if budget_per_activity < min_viable:
                # If can't afford minimum viable cost, return the minimum possible
                return round(min_viable, 2)
            
            # Cap maximum at budget
            max_cost = min(max_cost, budget_per_activity)
            
        # Calculate final cost with some randomization
        return round(random.uniform(min_cost, max_cost), 2)

    @classmethod
    def get_activity_duration(cls, activity: str) -> float:
        """
        Get a realistic duration for an activity.
        """
        # Map activities to duration categories
        long_activities = {"Private Tour", "Food Tour", "Theme Park", "Spa Day", "Yacht Experience"}
        short_activities = {"Local Market", "Temple/Church Visit", "Garden Visit", "Mini Golf"}
        
        if activity in long_activities:
            duration_range = cls.ACTIVITY_DURATIONS["long"]
        elif activity in short_activities:
            duration_range = cls.ACTIVITY_DURATIONS["short"]
        else:
            duration_range = cls.ACTIVITY_DURATIONS["medium"]
        
        return round(random.uniform(*duration_range), 1)

    @classmethod
    def get_activities_by_mood(cls, mood: str) -> Dict[str, List[str]]:
        """
        Get appropriate activities for different times of day based on mood.
        """
        if mood.lower() == "luxury":
            return {
                "morning": ["Private Tour", "Spa Treatment", "Private Shopping"],
                "afternoon": ["Wine Tasting", "Yacht Experience", "Helicopter Tour"],
                "evening": ["Michelin Star Dining", "Theater Show", "Private Tour"]
            }
        elif mood.lower() == "romantic":
            return {
                "morning": ["Garden Visit", "Couples Massage", "Private Picnic"],
                "afternoon": ["Wine Tasting", "Cooking Class", "Cultural Workshop"],
                "evening": ["Sunset Cruise", "Rooftop Dinner", "Evening Concert"]
            }
        elif mood.lower() == "adventure":
            return {
                "morning": ["Hiking", "Surfing Lesson", "Rock Climbing"],
                "afternoon": ["Water Sports", "Bike Tour", "Scuba Diving"],
                "evening": ["Food Tour", "Traditional Show", "Local Market"]
            }
        elif mood.lower() == "cultural":
            return {
                "morning": ["Museum Visit", "Historical Tour", "Temple/Church Visit"],
                "afternoon": ["Art Gallery", "Cultural Workshop", "Local Market"],
                "evening": ["Traditional Show", "Food Tour", "Evening Concert"]
            }
        elif mood.lower() == "relaxation":
            return {
                "morning": ["Yoga Class", "Beach Time", "Garden Visit"],
                "afternoon": ["Spa Day", "Thermal Bath", "Meditation Session"],
                "evening": ["Sunset Cruise", "Massage", "Scenic Drive"]
            }
        else:  # Default to cultural activities
            return {
                "morning": ["Museum Visit", "Historical Tour", "Local Market"],
                "afternoon": ["Art Gallery", "Cultural Workshop", "Food Tour"],
                "evening": ["Traditional Show", "Local Dining", "Evening Walk"]
            }
