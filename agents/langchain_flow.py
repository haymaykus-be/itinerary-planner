import json
from typing import List
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.tools import tool
from langchain_core.output_parsers import PydanticOutputParser

from agents.flight_agent import FlightAgent
from agents.hotel_agent import HotelAgent
from agents.itinerary_agent import ItineraryAgent
from models.schemas import ItineraryRequest, ItineraryResponse


# Initialize LLMs with specific configurations
orchestration_llm = OllamaLLM(
    model="tinyllama",
    temperature=0.7,
    stop=["</s>", "Human:", "Assistant:"],
    system="You are an English-speaking AI travel assistant. Always respond in English. Be concise and practical."
)

parsing_llm = OllamaLLM(
    model="tinyllama",
    temperature=0,
    stop=["</s>", "Human:", "Assistant:"],
    system="You are an English-speaking JSON formatting assistant. Always output valid JSON in English. Be precise and follow the schema exactly."
)

# Initialize simplified agent logic classes
flight_agent_logic = FlightAgent()
hotel_agent_logic = HotelAgent()
itinerary_agent_logic = ItineraryAgent()

agent_prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""You are an English-speaking AI travel assistant. Your goal is to plan a detailed itinerary.
                First, analyze the flight and hotel information provided.
                Then, create a comprehensive day-by-day plan that matches the user's preferences.
                
                Focus on providing:
                1. A clear summary of the trip
                2. Specific flight recommendations
                3. Hotel suggestions
                4. Daily activities with timing
                5. Cost estimates for everything
                6. Key travel recommendations
                
                Current Flight Information:
                {flights_result_str}

                Current Hotel Information:
                {hotels_result_str}
                Budget: ${budget}
                """),
    HumanMessagePromptTemplate.from_template("""Create a {duration_days}-day itinerary for {destination}.
                Requirements:
                - Mood: {mood}
                - Budget: ${budget}
                - Origin: {origin}
                - Travel Dates: {travel_dates}
                
                Please provide a detailed plan with specific times, locations, and cost estimates.
                """)
])

# --- Define LangChain Tools ---
@tool
async def search_flights_tool(query: str, budget: float = None) -> str:
    """Search for flight options.
    The query should be a comma-separated string like 'origin:New York,destination:Paris,depart_date:2024-07-20,return_date:2024-07-27'.
    It returns a formatted string of flight options."""
    params = dict(item.split(":") for item in query.split(","))
    return await flight_agent_logic.search_flights_logic(
        origin=params.get("origin"),
        destination=params.get("destination"), 
        depart_date=params.get("depart_date"),
        return_date=params.get("return_date"),
        budget=budget # Pass budget here
    )

@tool
async def search_hotels_tool(query: str, budget: float = None) -> str:
    """Search for hotel options.
    The query should be a comma-separated string like 'destination:Paris,check_in:2024-07-20,check_out:2024-07-27'.
    It returns a formatted string of hotel options."""
    params = dict(item.split(":") for item in query.split(","))
    return await hotel_agent_logic.search_hotels_logic(
        destination=params.get("destination"),
        check_in=params.get("check_in"),
        check_out=params.get("check_out"), 
        budget=budget  # Use the float budget parameter
    )

@tool
async def search_activities_tool(query: str) -> str:
    """Search for activities, restaurants, and attractions.
    The query should be a comma-separated string like 'mood:romantic,location:Paris,lat:48.8566,lon:2.3522'.
    It returns a JSON string of available places."""
    params = dict(item.split(":") for item in query.split(","))
    
    mood = params.get("mood", "cultural")
    categories = await itinerary_agent_logic.get_place_categories_by_mood_logic(mood)
    
    return await itinerary_agent_logic.search_activities_logic(
        categories=categories,
        lat=float(params.get("lat", 0)), 
        lon=float(params.get("lon", 0)),
        radius=int(params.get("radius", 10000)),
        limit=int(params.get("limit", 15))
    )

@tool
async def create_daily_schedule_tool(requirements: str) -> str:
    """Creates a detailed daily schedule based on provided requirements and available activities.
    Returns a structured daily plan."""
    return await itinerary_agent_logic.create_daily_schedule_logic(requirements)

# Combine all tools for the agent
all_tools = [search_flights_tool, search_hotels_tool, search_activities_tool, create_daily_schedule_tool]

# Helper function for structured data extraction
async def extract_structured_data(text: str, llm) -> dict:
    """Extract structured data from text using a step-by-step approach."""
    extraction_prompt = PromptTemplate.from_template(
        """Extract specific information from the following text and format it as JSON.
        Follow these steps:
        1. First, create a brief summary of the itinerary
        2. Calculate the total estimated cost from all mentioned prices
        3. Extract flight information (airline, price, duration, stops, departure, arrival)
        4. Extract hotel information (name, price per night, rating, location, amenities)
        5. Create a daily plan with activities (time, activity, location, cost, duration)
        6. List key recommendations

        Text to analyze:
        {text}

        Format your response EXACTLY like this example, with no additional text:
        {{
            "summary": "A 3-day romantic trip to Paris",
            "total_estimated_cost": 1500.0,
            "flights": [
                {{
                    "airline": "Air France",
                    "price": 800.0,
                    "duration": "8h",
                    "stops": 1,
                    "departure": "JFK",
                    "arrival": "CDG"
                }}
            ],
            "hotels": [
                {{
                    "name": "Paris Hotel",
                    "price_per_night": 200.0,
                    "rating": 4.5,
                    "location": "City Center",
                    "amenities": ["WiFi", "Breakfast"]
                }}
            ],
            "daily_plan": [
                {{
                    "time": "09:00",
                    "activity": "Visit Eiffel Tower",
                    "location": "Champ de Mars",
                    "cost_estimate": 25.0,
                    "duration_hours": 2.0
                }}
            ],
            "recommendations": [
                "Visit the Louvre",
                "Try local cuisine"
            ]
        }}"""
    )

    try:
        messages = extraction_prompt.format_messages(text=text)
        result = await llm.ainvoke(messages)
        
        # Parse the result as JSON
        parsed_json = json.loads(result)
        
        # Ensure all required fields are present with defaults if missing
        return {
            "summary": parsed_json.get("summary", ""),
            "total_estimated_cost": float(parsed_json.get("total_estimated_cost", 0.0)),
            "flights": parsed_json.get("flights", []),
            "hotels": parsed_json.get("hotels", []),
            "daily_plan": parsed_json.get("daily_plan", []),
            "recommendations": parsed_json.get("recommendations", [])
        }
    except Exception as e:
        print(f"Error in extract_structured_data: {e}")
        return {
            "summary": "Failed to parse itinerary data",
            "total_estimated_cost": 0.0,
            "flights": [],
            "hotels": [],
            "daily_plan": [],
            "recommendations": []
        }

# --- Orchestration Logic ---
async def run_itinerary_agent_flow(request: ItineraryRequest) -> ItineraryResponse:
    try:
        # Step 1: Get flight and hotel data
        flight_query = f"origin:{request.origin},destination:{request.destination},depart_date:{request.travel_dates},return_date:None"
        hotel_query = f"destination:{request.destination},check_in:{request.travel_dates},check_out:{request.travel_dates}"

        flights_result_str = await search_flights_tool.ainvoke(flight_query, budget=request.budget)
        hotels_result_str = await search_hotels_tool.ainvoke(hotel_query, budget=request.budget)

        # Step 2: Get activities data first
        activity_query = f"mood:{request.mood},location:{request.destination}"
        activities_json_str = await search_activities_tool.ainvoke(activity_query)

        # Step 3: Create daily schedule
        schedule_query = f"days:{request.duration_days},mood:{request.mood},budget:{request.budget}"
        daily_schedule = await create_daily_schedule_tool.ainvoke(schedule_query)

        # Step 4: Combine all data and create structured response directly
        try:
            # Calculate total cost
            flights_data = json.loads(flights_result_str) if flights_result_str else {"flights": []}
            hotels_data = json.loads(hotels_result_str) if hotels_result_str else {"hotels": []}
            schedule_data = json.loads(daily_schedule) if daily_schedule else []

            # Get the cheapest flight and hotel
            flight_cost = min([f.get("price", 0) for f in flights_data.get("flights", [])], default=0)
            hotel_cost = min([h.get("price_per_night", 0) for h in hotels_data.get("hotels", [])], default=0) * request.duration_days
            
            # Estimate activity costs from schedule
            activity_costs = sum([
                sum([act.get("cost_estimate", 0) for act in day.get("activities", [])])
                for day in schedule_data
            ])

            total_cost = flight_cost + hotel_cost + activity_costs

            return ItineraryResponse(
                summary=f"{request.duration_days}-day {request.mood} trip to {request.destination} from {request.origin}",
                total_estimated_cost=total_cost,
                flights=flights_data.get("flights", [])[:3],  # Top 3 flights
                hotels=hotels_data.get("hotels", [])[:3],    # Top 3 hotels
                daily_plan=schedule_data,
                recommendations=[
                    f"Book flights early to get the best price (found from ${flight_cost})",
                    f"Hotel costs will be around ${hotel_cost} for {request.duration_days} nights",
                    "Consider purchasing a city pass for attractions",
                    "Make restaurant reservations in advance"
                ]
            )
        except Exception as e:
            print(f"Error creating structured response: {e}")
            return ItineraryResponse(
                summary=f"Error creating itinerary: {str(e)}",
                total_estimated_cost=0.0,
                flights=[],
                hotels=[],
                daily_plan=[],
                recommendations=[]
            )

    # 
    except Exception as e:
        print(f"Error in run_itinerary_agent_flow: {e}")
        return ItineraryResponse(
            summary=f"Failed to generate itinerary due to unexpected error: {str(e)}",
            total_estimated_cost=0.0,
            flights=[],
            hotels=[],
            daily_plan=[],
            recommendations=[]
        )