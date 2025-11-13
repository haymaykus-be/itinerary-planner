from typing import List, Dict, Any
import json
import random
from services.geoapify_client import GeoapifyClient
from models.activity_definitions import ActivityDefinitions

class ItineraryAgent:
    def __init__(self):
        self.geoapify = GeoapifyClient()
        self.used_activities = set()  # Track used activities to prevent duplicates

    def _is_activity_compatible(self, current_activity: str, previous_activities: List[str], time_of_day: str) -> bool:
        """
        Check if an activity is compatible with previous activities.
        Prevents similar activities on consecutive days or duplicate activities.
        """
        # Don't allow exact duplicates in the last 3 days
        if current_activity in previous_activities[-9:]:  # 3 days * 3 activities
            return False
        
        # Check for similar activities (e.g., different types of tours)
        similar_keywords = {
            "tour": ["tour", "guided", "walking"],
            "class": ["class", "workshop", "lesson"],
            "cruise": ["cruise", "boat", "sailing", "yacht"],
            "show": ["show", "concert", "performance", "theater"],
            "spa": ["spa", "massage", "wellness", "treatment"],
            "dining": ["dining", "restaurant", "culinary", "dinner"],
            "shopping": ["shopping", "boutique", "market"],
            "helicopter": ["helicopter", "aerial", "flight"],
        }
        
        # Get activities from the same time slot in the last 2 days
        day_length = 3  # activities per day
        time_slots = {"morning": 0, "afternoon": 1, "evening": 2}
        time_idx = time_slots.get(time_of_day, 0)
        
        # Check the same time slot from previous days
        for day_offset in range(1, 3):  # Check last 2 days
            idx = -(day_length * day_offset + time_idx)
            if abs(idx) <= len(previous_activities):
                prev_activity = previous_activities[idx]
                
                # Check exact match
                if prev_activity == current_activity:
                    return False
                
                # Check similar activities
                activity_lower = prev_activity.lower()
                current_lower = current_activity.lower()
                
                for category, keywords in similar_keywords.items():
                    if any(keyword in activity_lower for keyword in keywords) and \
                       any(keyword in current_lower for keyword in keywords):
                        return False
        
        return True

    async def create_daily_schedule_logic(self, requirements: str) -> str:
        """Create a structured daily schedule based on requirements."""
        try:
            # Parse requirements
            params = dict(item.split(":") for item in requirements.split(","))
            days = int(params.get("days", 3))
            mood = params.get("mood", "cultural").lower()
            budget = float(params.get("budget", 1000))

            schedule = []
            all_activities = []  # Track all selected activities
            
            # Get mood-specific activities
            activities_by_time = ActivityDefinitions.get_activities_by_mood(mood)

            # Generate schedule for each day
            for day in range(1, days + 1):
                daily_activities = []
                
                # Time slots with slight variations to avoid exact same times
                time_slots = {
                    "morning": f"{9 + random.randint(-1, 1):02d}:00",
                    "afternoon": f"{14 + random.randint(-1, 1):02d}:00",
                    "evening": f"{19 + random.randint(-1, 1):02d}:00"
                }
                
                # Process each time slot
                for time_of_day, base_time in time_slots.items():
                    available_activities = activities_by_time.get(time_of_day, [])
                    
                    # Filter activities for compatibility
                    compatible_activities = [
                        activity for activity in available_activities
                        if self._is_activity_compatible(activity, all_activities, time_of_day)
                    ]
                    
                    # If no compatible activities, use all activities
                    if not compatible_activities:
                        compatible_activities = available_activities
                    
                    activity_name = random.choice(compatible_activities)
                    all_activities.append(activity_name)
                    
                    # Calculate budget per activity
                    total_activities = days * 3  # 3 activities per day
                    budget_per_activity = float(params.get("budget", 1000)) * 0.4 / total_activities  # 40% of budget for activities
                    
                    # Get realistic cost and duration
                    cost = ActivityDefinitions.get_activity_cost(
                        activity=activity_name,
                        city=params.get("destination", "Paris"),
                        category=mood,
                        budget_per_activity=budget_per_activity
                    )
                    duration = ActivityDefinitions.get_activity_duration(activity_name)
                    
                    activity = {
                        "time": base_time,
                        "activity": activity_name,
                        "cost_estimate": cost,
                        "duration_hours": duration
                    }
                    daily_activities.append(activity)

                schedule.append({
                    "day": day,
                    "activities": daily_activities
                })

            return json.dumps(schedule)
            
        except Exception as e:
            print(f"Error in create_daily_schedule_logic: {e}")
            return json.dumps([])  # Return empty schedule on error

    async def get_place_categories_by_mood_logic(self, mood: str) -> List[str]:
        """Get relevant place categories based on mood."""
        mood_categories = {
            "luxury": ["catering.restaurant.fine_dining", "entertainment.culture.theatre", "commercial.shopping_mall"],
            "romantic": ["catering.restaurant.fine_dining", "entertainment.culture.theatre", "natural"],
            "adventure": ["sport.fitness_center", "natural", "entertainment.water_park"],
            "cultural": ["entertainment.culture.museum", "entertainment.culture.theatre", "tourism.sights"],
            "relaxation": ["natural", "commercial.spa", "leisure.park"],
            "family": ["entertainment.water_park", "entertainment.theme_park", "entertainment.aquarium"]
        }
        return mood_categories.get(mood.lower(), ["tourism.sights"])