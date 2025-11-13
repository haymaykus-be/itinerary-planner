from typing import List, Dict, Optional
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import json
import random
from models.schemas import Activity
from models.activity_definitions import ActivityDefinitions
from models.activity_definitions import ActivityDefinitions

class AIActivityPlanner:
    def __init__(self):
        self.llm = OllamaLLM(
            model="qwen:0.5b",
            temperature=0.3,  # Lower temperature for faster, more focused responses
            num_ctx=256,      # Smaller context window
            num_predict=128,  # Shorter predictions
            repeat_penalty=1.1,
            top_k=10,        # Limit token choices for faster sampling
            top_p=0.8,       # Limit token choices for faster sampling
            system="You are an expert travel activity planner. Generate engaging and realistic activities that match the destination's culture and the traveler's preferences."
        )
        self.activity_definitions = ActivityDefinitions()

    async def generate_activities(
        self,
        destination: str,
        mood: str,
        budget: float,
        days: int,
        activities_per_day: int = 3
    ) -> List[Dict[str, List[Activity]]]:
        import time
        start_time = time.time()
        """
        Generate activities for the entire trip using AI.
        Returns a list of daily activities that match the mood and destination.
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """Generate a {days}-day schedule for a {mood} trip to {destination}.
                Activities per day: {activities_per_day}
                Budget per activity: ${budget_per_activity}

                Available activities: {available_activities}

                RESPOND WITH ONLY A JSON OBJECT IN THIS EXACT FORMAT (no other text):
                {{"daily_activities":[{{"day":1,"activities":[{{"activity":"Activity Name","time":"09:00","duration_hours":2.5}}]}}]}}
                
                RULES:
                1. Use ONLY activities from the available list
                2. Each day needs exactly {activities_per_day} activities
                3. Use times between 09:00-22:00
                4. Duration must be a number (2.5, not "2.5 hours")
                5. NO extra fields or text
                """
            ),
            HumanMessagePromptTemplate.from_template(
                "Generate a {days}-day schedule of activities in {destination} that match a {mood} theme. Each day should have {activities_per_day} activities."
            )
        ])

        # Get available activities
        available_activities = []
        mood_activities = self.activity_definitions.get_activities_by_mood(mood)
        for time_slot, activities in mood_activities.items():
            available_activities.extend(activities)

        # Calculate budget per activity
        total_activities = days * activities_per_day
        budget_per_activity = budget * 0.4 / total_activities  # 40% of budget for activities

        # Generate activities using LLM
        messages = prompt.format_messages(
            mood=mood,
            destination=destination,
            days=days,
            activities_per_day=activities_per_day,
            budget_per_activity=budget_per_activity,
            available_activities=", ".join(available_activities)
        )

        response = await self.llm.ainvoke(messages[0].content)
        try:
            # Clean and parse LLM response
            response_text = response.strip()
            
            # Remove any markdown code block markers and extra whitespace
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            # Try to find JSON object if there's extra text
            try:
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx]
            except Exception:
                pass
            # Parse JSON response
            try:
                activities_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                return self._generate_fallback_activities(
                    destination=destination,
                    mood=mood,
                    budget_per_activity=budget_per_activity,
                    days=days,
                    activities_per_day=activities_per_day
                )
            
            # Validate response structure
            if "daily_activities" not in activities_data:
                return self._generate_fallback_activities(
                    destination=destination,
                    mood=mood,
                    budget_per_activity=budget_per_activity,
                    days=days,
                    activities_per_day=activities_per_day
                )
            
            # Process and validate activities
            processed_activities = []
            try:
                for day_data in activities_data["daily_activities"]:
                    if "day" not in day_data or "activities" not in day_data:
                        raise ValueError(f"Invalid day data structure: {day_data}")
                    
                    day_activities = []
                    for activity in day_data["activities"]:
                        if "activity" not in activity or "time" not in activity:
                            raise ValueError(f"Invalid activity structure: {activity}")
                        
                        # Get realistic cost and duration
                        cost = self.activity_definitions.get_activity_cost(
                            activity=activity["activity"],
                            city=destination,
                            category=mood,
                            budget_per_activity=budget_per_activity
                        )
                        
                        # Use provided duration or get from definitions
                        duration = activity.get(
                            "duration_hours",
                            self.activity_definitions.get_activity_duration(activity["activity"])
                        )
                        
                        # Create Activity object
                        activity_obj = Activity(
                            time=activity["time"],
                            activity=activity["activity"],
                            location=f"{destination} - {activity['activity']}",
                            cost_estimate=cost,
                            duration_hours=duration
                        )
                        day_activities.append(activity_obj)
                    
                    processed_activities.append({
                        "day": day_data["day"],
                        "activities": day_activities
                    })
                
                return processed_activities
                
            except (KeyError, ValueError) as e:
                return self._generate_fallback_activities(
                    destination=destination,
                    mood=mood,
                    budget_per_activity=budget_per_activity,
                    days=days,
                    activities_per_day=activities_per_day
                )
                
        except Exception as e:
            return self._generate_fallback_activities(
                destination=destination,
                mood=mood,
                budget_per_activity=budget_per_activity,
                days=days,
                activities_per_day=activities_per_day
            )

    def _generate_fallback_activities(
        self,
        destination: str,
        mood: str,
        budget_per_activity: float,
        days: int,
        activities_per_day: int
    ) -> List[Dict[str, List[Activity]]]:
        """
        Fallback method to generate activities using rule-based approach.
        """
        processed_activities = []
        mood_activities = self.activity_definitions.get_activities_by_mood(mood)
        
        for day in range(1, days + 1):
            day_activities = []
            used_activities = set()
            
            # Standard time slots
            time_slots = {
                "morning": "09:00",
                "afternoon": "14:00",
                "evening": "19:00"
            }
            
            for slot, time in time_slots.items():
                # Get available activities for this time slot
                available = mood_activities.get(slot, [])
                if not available:
                    available = mood_activities.get("morning", [])  # Fallback to morning activities
                
                # Filter out already used activities
                available = [a for a in available if a not in used_activities]
                if not available:
                    available = mood_activities.get("morning", [])  # Reset if no activities left
                
                # Select random activity
                activity_name = random.choice(available)
                used_activities.add(activity_name)
                
                # Get cost and duration
                cost = self.activity_definitions.get_activity_cost(
                    activity=activity_name,
                    city=destination,
                    category=mood,
                    budget_per_activity=budget_per_activity
                )
                duration = self.activity_definitions.get_activity_duration(activity_name)
                
                # Create Activity object
                activity_obj = Activity(
                    time=time,
                    activity=activity_name,
                    location=f"{destination} - {activity_name}",
                    cost_estimate=cost,
                    duration_hours=duration
                )
                day_activities.append(activity_obj)
            
            processed_activities.append({
                "day": day,
                "activities": day_activities
            })
        
        return processed_activities