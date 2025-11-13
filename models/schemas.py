from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class TravelerSchema(BaseModel):
    """
    Schema for validating traveler information.
    """
    name: str = Field(..., description="The name of the traveler")
    email: str = Field(..., description="The email address of the traveler")
    phone: Optional[str] = Field(None, description="The phone number of the traveler")
    preferences: Optional[List[str]] = Field(None, description="A list of travel preferences for the traveler (e.g., 'window seat', 'vegetarian meals')")

class FlightOption(BaseModel):
    airline: str
    price: float
    duration: str
    stops: int
    departure: str
    arrival: str
    departure_fullname: Optional[str] = None
    arrival_fullname: Optional[str] = None

    class Config:
        from_attributes = True

class FlightOptions(BaseModel):
    outbound: List[FlightOption]
    return_: Optional[List[FlightOption]] = Field(default=None, alias="return")

    class Config:
        from_attributes = True
        populate_by_name = True

class HotelOption(BaseModel):
    name: str
    price_per_night: float
    rating: float
    location: str
    amenities: List[str]

    class Config:
        from_attributes = True

class Activity(BaseModel):
    time: str
    activity: str
    location: str
    cost_estimate: float
    duration_hours: float

    class Config:
        from_attributes = True

class DayPlan(BaseModel):
    day: int
    activities: List[Activity]

    class Config:
        from_attributes = True

class ItineraryResponse(BaseModel):
    summary: str
    total_estimated_cost: float
    flights: FlightOptions
    hotels: List[HotelOption]
    daily_plan: List[DayPlan]
    recommendations: List[str]

    class Config:
        from_attributes = True
        populate_by_name = True
    
class ItineraryRequest(BaseModel):
    origin: str
    destination: str
    duration_days: int
    budget: float
    mood: str
    travelers: Optional[List[TravelerSchema]] = []
    travel_dates: Optional[str] = None
    return_flight: Optional[bool] = True