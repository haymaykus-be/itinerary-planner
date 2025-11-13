from fastapi import APIRouter, HTTPException
from models.schemas import ItineraryRequest, ItineraryResponse, Activity, DayPlan, FlightOptions
import json

# New imports for LLM parsing
# from langchain_ollama import OllamaLLM
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser

router = APIRouter()

# Instantiate an LLM specifically for parsing
# This LLM should ideally be consistent with the one used by the crew
# settings = Settings()
# parsing_llm = OllamaLLM(
#     model="qwen:0.5b", # You can use a smaller model for parsing if desired
#     # temperature=0, # Low temperature for consistent JSON output
#     # openai_api_key=settings.OPENAI_API_KEY
# )

# def parse_crewai_result(crew_result: str, request: ItineraryRequest) -> ItineraryResponse:
#     # Define the parser for ItineraryResponse
#     parser = PydanticOutputParser(pydantic_object=ItineraryResponse)

#     # Define the prompt for the LLM to parse the crew result
#     # ENHANCED PROMPT WITH EXAMPLE
#     prompt = PromptTemplate(
#         template="""You are an expert JSON parsing assistant. Your task is to extract information
#         from a natural language travel itinerary and strictly format it as a JSON object
#         that precisely conforms to the provided Pydantic schema.

#         **CRITICAL RULES:**
#         1.  The output MUST be a valid JSON object. Do NOT include any text, conversation, or markdown
#             fences (like '```json' or '```') outside the JSON object itself.
#         2.  All fields specified in the schema MUST be present, even if empty (use [], "", or 0.0).
#         3.  Ensure numerical fields (like 'price', 'rating', 'cost_estimate', 'duration_hours', 'total_estimated_cost')
#             are actual numbers (floats or integers), NOT strings with currency symbols or units.
#         4.  For nested objects (e.g., within 'flights', 'hotels', 'daily_plan'), ensure each sub-object
#             fully conforms to its respective schema (e.g., FlightOption, HotelOption).

#         <schema>
#         {format_instructions}
#         </schema>

#         Here is an EXAMPLE of a PERFECTLY FORMATTED JSON output:
#         {{
#           "summary": "A romantic 5-day trip to Paris with flights from New York, a stay at Hotel George V, and visits to iconic landmarks.",
#           "total_estimated_cost": 2500.50,
#           "flights": [
#             {{
#               "airline": "Air France",
#               "price": 750.0,
#               "duration": "7h 30m",
#               "stops": 0,
#               "departure": "JFK",
#               "arrival": "CDG"
#             }}
#           ],
#           "hotels": [
#             {{
#               "name": "Hotel George V Paris",
#               "price_per_night": 500.0,
#               "rating": 4.8,
#               "location": "Champs-Élysées, Paris",
#               "amenities": ["Spa", "Pool", "Michelin-star restaurant"]
#             }}
#           ],
#           "daily_plan": [
#             {{
#               "time": "09:00",
#               "activity": "Visit Eiffel Tower and Trocadéro Gardens",
#               "location": "Champ de Mars, Paris",
#               "cost_estimate": 25.0,
#               "duration_hours": 3.0
#             }},
#             {{
#               "time": "13:00",
#               "activity": "Lunch at a traditional Parisian bistro",
#               "location": "Le Marais, Paris",
#               "cost_estimate": 40.0,
#               "duration_hours": 1.5
#             }}
#           ],
#           "recommendations": [
#             "Explore the Louvre Museum",
#             "Take a Seine River cruise",
#             "Enjoy a pastry at a local patisserie"
#           ]
#         }}
        
#         Now, parse the following Crew Result into the EXACT JSON format shown in the example:
        
#         Crew Result:
#         {crew_result}

#         JSON Output:
#         """,
#         input_variables=["crew_result"],
#         partial_variables={"format_instructions": parser.get_format_instructions()},
#     )

#     # Chain the prompt and parser with the parsing LLM
#     chain = prompt | parsing_llm | parser

#     try:
#         # Invoke the chain to parse the crew_result
#         parsed_response = chain.invoke({"crew_result": crew_result})
#         return parsed_response
#     except Exception as e:
#         print(f"Error parsing CrewAI result: {e}")
#         # Fallback to a default response if parsing fails
#         return ItineraryResponse(
#             summary=f"Failed to parse itinerary for {request.destination}. Original crew output: {crew_result}",
#             total_estimated_cost=0.0,
#             flights=[],
#             hotels=[],
#             daily_plan=[],
#             recommendations=[]
#         )

# @router.post("/generate-itinerary", response_model=ItineraryResponse)
# async def generate_itinerary(request: ItineraryRequest):
#     try:
#         # Create and run the crew
#         crew = create_itinerary_crew(request)
#         result = crew.kickoff()
        
#         # Parse the result into structured response
#         return parse_crewai_result(result, request)
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating itinerary: {str(e)}")

# @router.get("/search-flights")
# async def search_flights(origin: str, destination: str, depart_date: str, return_date: str = None):
#     serpapi = SerpApiClient()
#     flights = await serpapi.search_flights(origin, destination, depart_date, return_date)
#     return {"flights": flights}

# @router.get("/search-hotels") 
# async def search_hotels(destination: str, check_in: str, check_out: str, budget: str = "medium"):
#     serpapi = SerpApiClient()
#     hotels = await serpapi.search_hotels(destination, check_in, check_out, budget)
#     return {"hotels": hotels}
@router.post("/generate-itinerary", response_model=ItineraryResponse)
async def generate_itinerary(request: ItineraryRequest):
    from utils.mock_data_loader import MockDataLoader
    from agents.itinerary_agent import ItineraryAgent
    import time
    try:
        start_time = time.time()
        # 1. Get flights (both outbound and return)
        flights_data = MockDataLoader.get_mock_flights(
            origin=request.origin,
            destination=request.destination,
            budget=request.budget,
            return_flight=request.return_flight
        )
        
        # 2. Get hotels
        hotels = MockDataLoader.get_mock_hotels(
            destination=request.destination,
            budget=request.budget,
            mood=request.mood
        )

        # 3. Generate AI-powered activities
        from agents.ai_activity_planner import AIActivityPlanner
        activity_planner = AIActivityPlanner()
        
        # Generate activities using AI
        activities_data = await activity_planner.generate_activities(
            destination=request.destination,
            mood=request.mood,
            budget=request.budget,
            days=request.duration_days,
            activities_per_day=3
        )

        # Transform AI-generated activities into daily plan
        daily_plan = []
        activity_costs = 0
        
        # Process each day's activities
        for day_data in activities_data:
            day_activities = day_data["activities"]
            
            # Calculate costs
            for activity in day_activities:
                activity_costs += activity.cost_estimate
            
            # Create day plan
            day_plan = DayPlan(
                day=day_data["day"],
                activities=day_activities
            )
            daily_plan.append(day_plan)

        # 4. Calculate and adjust costs to meet budget
        remaining_budget = request.budget

        # Start with flights (30-50% of budget)
        max_flight_budget = request.budget * (0.5 if request.return_flight else 0.4)
        
        # Handle outbound flight (15-25% of budget)
        outbound_max = max_flight_budget * 0.5 if request.return_flight else max_flight_budget
        outbound_options = [(f.price, f.stops) for f in flights_data["outbound"] if f.price <= outbound_max]
        if outbound_options:
            # Prioritize flights with fewer stops when prices are similar
            best_outbound = min(outbound_options, key=lambda x: (x[0] * (1 + 0.1 * x[1])))  # 10% penalty per stop
            outbound_cost = best_outbound[0]
        else:
            # If no flights within budget, try up to 30% of total budget
            outbound_options = [(f.price, f.stops) for f in flights_data["outbound"] if f.price <= request.budget * 0.3]
            if outbound_options:
                best_outbound = min(outbound_options, key=lambda x: x[0])
                outbound_cost = best_outbound[0]
            else:
                outbound_cost = 0

        # Handle return flight if requested (15-25% of budget)
        return_cost = 0
        if request.return_flight and flights_data["return"]:
            return_max = max_flight_budget * 0.5
            return_options = [(f.price, f.stops) for f in flights_data["return"] if f.price <= return_max]
            if return_options:
                best_return = min(return_options, key=lambda x: (x[0] * (1 + 0.1 * x[1])))
                return_cost = best_return[0]
            else:
                # Try up to 30% of total budget
                return_options = [(f.price, f.stops) for f in flights_data["return"] if f.price <= request.budget * 0.3]
                if return_options:
                    best_return = min(return_options, key=lambda x: x[0])
                    return_cost = best_return[0]

        flight_cost = outbound_cost + return_cost
        
        remaining_budget -= flight_cost

        # Allocate budget for hotel (30-40% of remaining budget)
        daily_hotel_budget = (remaining_budget * 0.4) / request.duration_days
        hotel_options = [(h.price_per_night, h.rating) for h in hotels if h.price_per_night <= daily_hotel_budget]
        if hotel_options:
            # Prioritize hotels with better ratings within budget
            best_hotel = max(hotel_options, key=lambda x: x[1])  # Choose highest rated within budget
            hotel_cost = best_hotel[0] * request.duration_days
        else:
            # If no hotels within ideal budget, try up to 50% of remaining budget
            daily_hotel_budget = (remaining_budget * 0.5) / request.duration_days
            hotel_options = [(h.price_per_night, h.rating) for h in hotels if h.price_per_night <= daily_hotel_budget]
            if hotel_options:
                best_hotel = min(hotel_options, key=lambda x: x[0])
                hotel_cost = best_hotel[0] * request.duration_days
            else:
                hotel_cost = 0

        remaining_budget -= hotel_cost

        # Adjust activity costs if needed
        if activity_costs > remaining_budget:
            # Scale down activity costs to fit remaining budget
            scale_factor = remaining_budget / activity_costs
            activity_costs = round(activity_costs * scale_factor, 2)
            # Adjust individual activity costs
            for day in daily_plan:
                for activity in day.activities:
                    activity.cost_estimate = round(activity.cost_estimate * scale_factor, 2)

        # Calculate final total cost
        total_cost = round(flight_cost + hotel_cost + activity_costs, 2)

        # Verify we're within budget
        if total_cost > request.budget:
            # If still over budget, reduce activity costs further
            excess = total_cost - request.budget
            activity_reduction = min(activity_costs, excess)
            activity_costs -= activity_reduction
            scale_factor = (activity_costs + activity_reduction) / activity_costs if activity_costs > 0 else 0
            # Adjust individual activity costs
            for day in daily_plan:
                for activity in day.activities:
                    activity.cost_estimate = round(activity.cost_estimate * scale_factor, 2)
            total_cost = round(flight_cost + hotel_cost + activity_costs, 2)

        # 5. Create response
        return ItineraryResponse(
            summary=f"{request.duration_days}-day {request.mood} trip to {request.destination} from {request.origin}",
            total_estimated_cost=total_cost,
            flights=FlightOptions(
                outbound=flights_data["outbound"][:3],  # Top 3 outbound flights
                return_=flights_data["return"][:3] if request.return_flight and flights_data["return"] else []  # Top 3 return flights if requested
            ),
            hotels=hotels[:3],    # Top 3 hotels
            daily_plan=daily_plan,
            recommendations=[
                f"Book flights early to get the best price (outbound from ${outbound_cost}" + 
                (f", return from ${return_cost})" if request.return_flight else ")"),
                f"Hotel costs will be around ${min([h.price_per_night for h in hotels], default=0) * request.duration_days:.2f} for {request.duration_days} nights",
                "Consider purchasing a city pass for attractions",
                "Make restaurant reservations in advance"
            ]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating itinerary: {str(e)}")

@router.get("/search-flights")
async def search_flights(origin: str = None, destination: str = None, depart_date: str = None, return_date: str = None, budget: float = None):
    from utils.mock_data_loader import MockDataLoader
    try:
        flights = MockDataLoader.get_mock_flights(origin, destination, budget=budget)
        # Convert to dict for response
        flight_dicts = [flight.model_dump() for flight in flights]
        return {"flights": flight_dicts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching flights: {str(e)}")

@router.get("/search-hotels") 
async def search_hotels(destination: str, check_in: str, check_out: str, budget: float = 500.0): # Changed budget type to float with a default
    from utils.mock_data_loader import MockDataLoader
    try:
        hotels = MockDataLoader.get_mock_hotels(destination, budget)
        # Convert to dict for response
        hotel_dicts = [hotel.model_dump() for hotel in hotels]
        return {"hotels": hotel_dicts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching hotels: {str(e)}")