from crewai import Crew, Process, LLM
from .flight_agent import FlightAgent
from .hotel_agent import HotelAgent  
from .itinerary_agent import ItineraryAgent
from config.settings import Settings

def create_itinerary_crew(itinerary_request):
    settings = Settings()

    # Initialize local Hugging Face model using transformers pipeline
    # We'll use TinyLlama for its smaller size, but you can swap for others.
    model_llm = LLM(
    model="ollama/qwen:0.5b",
    base_url="http://localhost:11434"
    )

    

    # Initialize agents with explicit local LLM
    flight_agent = FlightAgent().create_agent(llm=model_llm)
    hotel_agent = HotelAgent().create_agent(llm=model_llm)
    itinerary_agent = ItineraryAgent().create_agent(llm=model_llm)
    # Define tasks for each agent
    from crewai import Task
    
    flight_task = Task(
        description=f"""Search for flights from {itinerary_request.origin} to {
            itinerary_request.destination} for the trip duration. 
            Consider budget level: {itinerary_request.budget}""",
        agent=flight_agent,
        expected_output="A list of 3-5 best flight options with prices, durations, and airlines"
    )
    
    hotel_task = Task(
        description=f"""Find hotels in {itinerary_request.destination} for {
            itinerary_request.duration_days} nights. Budget level: {
            itinerary_request.budget}. Look for hotels that match the {
            itinerary_request.mood} mood.""",
        agent=hotel_agent, 
        expected_output="A list of 3-5 hotel options with prices, ratings, and key amenities"
    )
    
    itinerary_task = Task(
        description=f"""Create a {itinerary_request.duration_days}-day itinerary for {
            itinerary_request.destination} with a {itinerary_request.mood} mood and {
            itinerary_request.budget} budget. Use the flight and hotel information, 
            and create a detailed daily schedule with activities, restaurants, 
            and sightseeing that match the traveler's preferences.""",
        agent=itinerary_agent,
        expected_output="A comprehensive day-by-day itinerary with timing, activities, costs, and recommendations",
        context=[flight_task, hotel_task]
    )
    
    # Create and return the crew
    return Crew(
        agents=[flight_agent, hotel_agent, itinerary_agent],
        tasks=[flight_task, hotel_task, itinerary_task],
        process=Process.sequential,
        llm=model_llm, # Explicitly set the LLM for the Crew itself
        verbose=True
    )