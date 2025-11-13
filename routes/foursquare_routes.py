from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from services.foursquare_client import FoursquareClient

router = APIRouter()
foursquare_client = FoursquareClient()

@router.get("/foursquare/search", response_model=List[Dict[str, Any]])
async def foursquare_search(
    query: str = Query(..., description="Search query for places"),
    ll: Optional[str] = Query(None, description="Latitude,longitude for search area (e.g., \"40.7128,-74.0060\")"),
    near: Optional[str] = Query(None, description="City,state,country for search area (e.g., \"New York,NY,US\")"),
    radius: Optional[int] = Query(None, description="Radius in meters for search"),
    categories: Optional[str] = Query(None, description="Comma-separated Foursquare category IDs"),
    limit: int = Query(10, description="Maximum number of results to return")
):
    """
    Searches for places using the Foursquare Places API.
    """
    try:
        results = await foursquare_client.search_places(query, ll, near, radius, categories, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Foursquare search failed: {str(e)}")

