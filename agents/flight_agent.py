# from crewai import Agent
# from crewai.tools import tool
from services.serpapi_client import SerpApiClient
from models.schemas import FlightOption

class FlightAgent:
    def __init__(self):
        self.serpapi = SerpApiClient()
        
    # def create_agent(self, llm=None):
    #     # Create the tool using CrewAI's @tool decorator
    #     @tool("Search Flights")
    #     def search_flights(query: str) -> str:
    #         """Search for flights between two cities on specific dates. Input should be in format: origin:Paris,destination:Tokyo,departure:2024-03-15,return:2024-03-22"""
    #         try:
    #             params = dict(item.split(":") for item in query.split(","))
                
    #             flights = self.serpapi.search_flights(
    #                 origin=params.get("origin"),
    #                 destination=params.get("destination"), 
    #                 depart_date=params.get("departure"),
    #                 return_date=params.get("return")
    #             )
                
    #             return format_flight_results(flights)
    #         except Exception as e:
    #             return f"Error searching flights: {str(e)}"
        
    #     def format_flight_results(flights):
    #         if not flights:
    #             return "No flights found for the given criteria."
            
    #         result = "FLIGHT OPTIONS:\n"
    #         for i, flight in enumerate(flights, 1):
    #             result += f"{i}. {flight.airline}: ${flight.price} | {flight.duration} | {flight.stops} stops\n"
    #         return result

    #     flight_tools = [search_flights]
        
    #     return Agent(
    #         role="Flight Search Specialist",
    #         goal="Find the best flight options based on budget, dates, and user preferences",
    #         backstory="""You are an expert travel agent specializing in finding the 
    #         best flight deals. You consider budget constraints, travel duration, 
    #         number of stops, and airline preferences to recommend optimal flights.""",
    #         tools=flight_tools,
    #         verbose=True,
    #         allow_delegation=False,
    #         llm=llm
    #     )
    
    async def search_flights_logic(self, origin: str, destination: str, depart_date: str, return_date: str = None, budget: float = None) -> str:
        from utils.mock_data_loader import MockDataLoader
        mock_flights = MockDataLoader.get_mock_flights(origin, destination, budget=budget)
        return self._format_flight_results(mock_flights)
    
    def _format_flight_results(self, flights):
        if not flights:
            return "No flights found for the given criteria."
        
        result = "FLIGHT OPTIONS:\n"
        for i, flight in enumerate(flights, 1):
            departure_info = flight.departure_fullname if flight.departure_fullname else flight.departure
            arrival_info = flight.arrival_fullname if flight.arrival_fullname else flight.arrival
            result += f"{i}. {flight.airline}: ${flight.price} | {flight.duration} | {flight.stops} stops | From: {departure_info} To: {arrival_info}\n"
        return result