from crewai.tools.base_tool import BaseTool
from utils.mock_data_loader import MockDataLoader

class HotelSearchTool(BaseTool):
    name: str = "Search Hotels"
    description: str = "Search for hotels in a destination with check-in/check-out dates"
    # serpapi: SerpApiClient = Field(description="SerpAPI client for hotel searches") # Removed

    def __init__(self, **kwargs):
        super().__init__(**kwargs) # serpapi removed from here

    def _run(self, query: str) -> str:
        params = dict(item.split(":") for item in query.split(","))
        
        hotels = MockDataLoader.get_mock_hotels(
            destination=params.get("destination"),
        ) # Simplified to only use destination for mock data
        
        return self._format_hotel_results(hotels)

    def _format_hotel_results(self, hotels):
        if not hotels:
            return "No hotels found for the given criteria."
        
        result = "HOTEL OPTIONS:\n"
        for i, hotel in enumerate(hotels, 1):
            result += f"{i}. {hotel.name}: ${hotel.price_per_night} | Rating: {hotel.rating} | Location: {hotel.location}\n"
        return result

class HotelAgent:
    def __init__(self):
        pass # serpapi initialization removed
        
    # def create_agent(self, llm=None):
    #     hotel_tools = [
    #         HotelSearchTool(serpapi=self.serpapi)
    #     ]
        
    #     return Agent(
    #         role="Hotel Accommodation Specialist", 
    #         goal="Find the best hotel options matching the user's budget and preferences",
    #         backstory="""You are a luxury hotel consultant with expertise in finding 
    #         accommodations that match specific budgets, locations, and amenity requirements.""",
    #         tools=hotel_tools,
    #         verbose=True,
    #         allow_delegation=False,
    #         llm=llm
    #     )
    async def search_hotels_logic(self, destination: str, check_in: str, check_out: str, budget: float = 500.0) -> str:
        # Directly use MockDataLoader
        hotels = MockDataLoader.get_mock_hotels(destination=destination, budget=budget)
        return self._format_hotel_results(hotels)

    def _format_hotel_results(self, hotels):
        if not hotels:
            return "No hotels found for the given criteria."
        
        result = "HOTEL OPTIONS:\n"
        for i, hotel in enumerate(hotels, 1):
            result += f"{i}. {hotel.name}: ${hotel.price_per_night} | Rating: {hotel.rating} | Location: {hotel.location}\n"
        return result