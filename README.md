# Itinerary Planner Backend

A FastAPI-based backend service for generating comprehensive travel itineraries with AI-powered activity planning, flight options, and hotel recommendations.

## Features

- **AI-Powered Itinerary Generation**: Generate complete travel itineraries based on destination, budget, mood, and duration
- **Flight Search**: Search and compare flight options for outbound and return trips
- **Hotel Recommendations**: Get hotel suggestions based on budget and preferences
- **Activity Planning**: AI-generated daily activity schedules that match your travel mood (romantic, adventure, family-friendly, etc.)
- **Budget Management**: Intelligent budget allocation across flights, hotels, and activities
- **Foursquare Integration**: Search for places and venues using the Foursquare Places API
- **Mock Data Support**: Development-friendly mock data for testing without external API calls

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **CrewAI**: Multi-agent AI framework for complex task orchestration
- **LangChain**: LLM application framework for AI-powered features
- **Ollama**: Local LLM integration for activity planning
- **Pydantic**: Data validation using Python type annotations
- **Python 3.12+**: Core programming language

## Installation

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Ollama installed and running (for AI activity planning)
- API keys for external services (optional, for production use)

### Setup

1. **Clone the repository** (if applicable):

   ```bash
   git clone <repository-url>
   cd itinerary_planner_BE
   ```

2. **Create a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory:

   ```env
   SERPAPI_API_KEY=your_serpapi_key
   GEOAPIFY_API_KEY=your_geoapify_key
   OPENAI_API_KEY=your_openai_key
   FOURSQUARE_API_KEY=your_foursquare_key
   CACHE_TTL=3600
   ```

5. **Install and configure Ollama** (for AI activity planning):
   ```bash
   # Install Ollama from https://ollama.ai
   # Pull the required model
   ollama pull qwen:0.5b
   ```

## Running the Application

### Development Server

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Itinerary Generation

#### `POST /generate-itinerary`

Generate a complete travel itinerary with flights, hotels, and activities.

**Request Body**:

```json
{
  "origin": "New York",
  "destination": "Paris",
  "duration_days": 5,
  "budget": 3000.0,
  "mood": "romantic",
  "return_flight": true,
  "travelers": [
    {
      "name": "John Doe",
      "email": "john@example.com"
    }
  ],
  "travel_dates": "2024-06-01"
}
```

**Response**:

```json
{
  "summary": "5-day romantic trip to Paris from New York",
  "total_estimated_cost": 2850.50,
  "flights": {
    "outbound": [...],
    "return": [...]
  },
  "hotels": [...],
  "daily_plan": [
    {
      "day": 1,
      "activities": [...]
    }
  ],
  "recommendations": [...]
}
```

### Flight Search

#### `GET /search-flights`

Search for flight options.

**Query Parameters**:

- `origin` (optional): Origin city/airport
- `destination` (optional): Destination city/airport
- `depart_date` (optional): Departure date
- `return_date` (optional): Return date
- `budget` (optional): Budget constraint

### Hotel Search

#### `GET /search-hotels`

Search for hotel options.

**Query Parameters**:

- `destination` (required): Destination city
- `check_in` (required): Check-in date
- `check_out` (required): Check-out date
- `budget` (optional): Budget constraint (default: 500.0)

### Foursquare Integration

#### `GET /foursquare/search`

Search for places using Foursquare Places API.

**Query Parameters**:

- `query` (required): Search query
- `ll` (optional): Latitude,longitude
- `near` (optional): City,state,country
- `radius` (optional): Search radius in meters
- `categories` (optional): Comma-separated category IDs
- `limit` (optional): Maximum results (default: 10)

## Project Structure

```
itinerary_planner_BE/
├── agents/                 # AI agents for itinerary planning
│   ├── ai_activity_planner.py
│   ├── crew_setup.py
│   ├── flight_agent.py
│   ├── hotel_agent.py
│   ├── itinerary_agent.py
│   └── langchain_flow.py
├── config/                 # Configuration settings
│   └── settings.py
├── models/                 # Data models and schemas
│   ├── activity_categories.py
│   ├── activity_definitions.py
│   └── schemas.py
├── routes/                 # API route handlers
│   ├── foursquare_routes.py
│   └── itinerary_routes.py
├── services/               # External service clients
│   ├── cache_manager.py
│   ├── foursquare_client.py
│   ├── geoapify_client.py
│   └── serpapi_client.py
├── utils/                  # Utility functions
│   └── mock_data_loader.py
├── mock_data/              # Mock data for development
│   ├── airport_details_map.json
│   ├── flights.json
│   ├── hotels.json
│   └── itinerary.json
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Usage Examples

### Generate a Romantic Getaway Itinerary

```python
import requests

response = requests.post(
    "http://localhost:8000/generate-itinerary",
    json={
        "origin": "New York",
        "destination": "Paris",
        "duration_days": 5,
        "budget": 3000.0,
        "mood": "romantic",
        "return_flight": True
    }
)

itinerary = response.json()
print(f"Total Cost: ${itinerary['total_estimated_cost']}")
print(f"Summary: {itinerary['summary']}")
```

### Search for Hotels

```python
response = requests.get(
    "http://localhost:8000/search-hotels",
    params={
        "destination": "Paris",
        "check_in": "2024-06-01",
        "check_out": "2024-06-06",
        "budget": 500.0
    }
)

hotels = response.json()
```

## Configuration

### Environment Variables

| Variable             | Description                          | Required            |
| -------------------- | ------------------------------------ | ------------------- |
| `SERPAPI_API_KEY`    | SerpAPI key for flight/hotel search  | No (uses mock data) |
| `GEOAPIFY_API_KEY`   | Geoapify key for geocoding           | No                  |
| `OPENAI_API_KEY`     | OpenAI API key for LLM features      | No (uses Ollama)    |
| `FOURSQUARE_API_KEY` | Foursquare API key for places search | No                  |
| `CACHE_TTL`          | Cache time-to-live in seconds        | No (default: 3600)  |

### Activity Moods

The system supports various travel moods for activity planning:

- `romantic`
- `adventure`
- `family-friendly`
- `luxury`
- `budget`
- `cultural`

## Development

### Mock Data

The application uses mock data by default, making it easy to develop and test without external API dependencies. Mock data files are located in the `mock_data/` directory.

### Adding New Features

1. **New API Endpoints**: Add routes in the `routes/` directory
2. **New Agents**: Create agent files in the `agents/` directory
3. **New Services**: Add service clients in the `services/` directory
4. **Data Models**: Update schemas in `models/schemas.py`

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

For issues and questions, please [open an issue](link-to-issues) or contact the development team.
