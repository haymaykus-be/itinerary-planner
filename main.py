from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import itinerary_routes
from routes import foursquare_routes

app = FastAPI(
    title="Itinerary Planner API",
    description="API for generating travel itineraries, including flights, hotels, and activities.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(itinerary_routes.router)
app.include_router(foursquare_routes.router)