from pydantic_settings import BaseSettings, SettingsConfigDict

import os
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra='ignore')

    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY")
    GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    FOURSQUARE_API_KEY: str = os.getenv("FOURSQUARE_API_KEY")
    
    CACHE_TTL: int = 3600  # Default to 3600 seconds (1 hour) if not set

