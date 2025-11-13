"""
Activity categories and metadata for better activity planning and variety.
"""
from typing import Dict, List, Optional
from enum import Enum

class ActivityCategory(str, Enum):
    CULTURAL = "cultural"
    ADVENTURE = "adventure"
    RELAXATION = "relaxation"
    DINING = "dining"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    NATURE = "nature"
    EDUCATIONAL = "educational"

class ActivityEnergy(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ActivityTime(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    ANY = "any"

class ActivityMetadata:
    def __init__(
        self,
        name: str,
        category: ActivityCategory,
        energy_level: ActivityEnergy,
        preferred_times: List[ActivityTime],
        duration_range: tuple[float, float],
        indoor: bool = True,
        requires_booking: bool = False,
        weather_dependent: bool = False,
        typical_cost_range: tuple[float, float] = (0, 0)
    ):
        self.name = name
        self.category = category
        self.energy_level = energy_level
        self.preferred_times = preferred_times
        self.duration_range = duration_range
        self.indoor = indoor
        self.requires_booking = requires_booking
        self.weather_dependent = weather_dependent
        self.typical_cost_range = typical_cost_range

# Activity metadata for better planning
ACTIVITY_METADATA: Dict[str, ActivityMetadata] = {
    # Luxury Activities
    "Michelin Star Dining": ActivityMetadata(
        name="Michelin Star Dining",
        category=ActivityCategory.DINING,
        energy_level=ActivityEnergy.LOW,
        preferred_times=[ActivityTime.EVENING],
        duration_range=(2.0, 4.0),
        indoor=True,
        requires_booking=True,
        weather_dependent=False,
        typical_cost_range=(200, 500)
    ),
    "Private Tour": ActivityMetadata(
        name="Private Tour",
        category=ActivityCategory.CULTURAL,
        energy_level=ActivityEnergy.MEDIUM,
        preferred_times=[ActivityTime.MORNING, ActivityTime.AFTERNOON],
        duration_range=(3.0, 6.0),
        indoor=False,
        requires_booking=True,
        weather_dependent=True,
        typical_cost_range=(150, 400)
    ),
    "Spa Treatment": ActivityMetadata(
        name="Spa Treatment",
        category=ActivityCategory.RELAXATION,
        energy_level=ActivityEnergy.LOW,
        preferred_times=[ActivityTime.MORNING, ActivityTime.AFTERNOON],
        duration_range=(1.5, 4.0),
        indoor=True,
        requires_booking=True,
        weather_dependent=False,
        typical_cost_range=(150, 400)
    ),
    "Wine Tasting": ActivityMetadata(
        name="Wine Tasting",
        category=ActivityCategory.CULTURAL,
        energy_level=ActivityEnergy.LOW,
        preferred_times=[ActivityTime.AFTERNOON],
        duration_range=(2.0, 4.0),
        indoor=True,
        requires_booking=True,
        weather_dependent=False,
        typical_cost_range=(100, 300)
    ),
    "Theater Show": ActivityMetadata(
        name="Theater Show",
        category=ActivityCategory.ENTERTAINMENT,
        energy_level=ActivityEnergy.LOW,
        preferred_times=[ActivityTime.EVENING],
        duration_range=(2.0, 4.0),
        indoor=True,
        requires_booking=True,
        weather_dependent=False,
        typical_cost_range=(100, 300)
    ),
    "Private Shopping": ActivityMetadata(
        name="Private Shopping",
        category=ActivityCategory.SHOPPING,
        energy_level=ActivityEnergy.MEDIUM,
        preferred_times=[ActivityTime.MORNING, ActivityTime.AFTERNOON],
        duration_range=(2.0, 4.0),
        indoor=True,
        requires_booking=False,
        weather_dependent=False,
        typical_cost_range=(0, 0)  # Cost depends on purchases
    ),
    "Yacht Experience": ActivityMetadata(
        name="Yacht Experience",
        category=ActivityCategory.ADVENTURE,
        energy_level=ActivityEnergy.MEDIUM,
        preferred_times=[ActivityTime.AFTERNOON],
        duration_range=(4.0, 6.0),
        indoor=False,
        requires_booking=True,
        weather_dependent=True,
        typical_cost_range=(500, 2000)
    ),
    "Helicopter Tour": ActivityMetadata(
        name="Helicopter Tour",
        category=ActivityCategory.ADVENTURE,
        energy_level=ActivityEnergy.LOW,
        preferred_times=[ActivityTime.MORNING, ActivityTime.AFTERNOON],
        duration_range=(1.5, 4.0),
        indoor=False,
        requires_booking=True,
        weather_dependent=True,
        typical_cost_range=(300, 800)
    ),
    
    # Cultural Activities
    "Museum Visit": ActivityMetadata(
        name="Museum Visit",
        category=ActivityCategory.CULTURAL,
        energy_level=ActivityEnergy.LOW,
        preferred_times=[ActivityTime.MORNING, ActivityTime.AFTERNOON],
        duration_range=(2.0, 4.0),
        indoor=True,
        requires_booking=False,
        weather_dependent=False,
        typical_cost_range=(15, 30)
    ),
    "Historical Tour": ActivityMetadata(
        name="Historical Tour",
        category=ActivityCategory.CULTURAL,
        energy_level=ActivityEnergy.MEDIUM,
        preferred_times=[ActivityTime.MORNING, ActivityTime.AFTERNOON],
        duration_range=(2.0, 4.0),
        indoor=False,
        requires_booking=True,
        weather_dependent=True,
        typical_cost_range=(30, 60)
    ),
    "Local Market": ActivityMetadata(
        name="Local Market",
        category=ActivityCategory.CULTURAL,
        energy_level=ActivityEnergy.MEDIUM,
        preferred_times=[ActivityTime.MORNING],
        duration_range=(1.5, 3.0),
        indoor=False,
        requires_booking=False,
        weather_dependent=True,
        typical_cost_range=(0, 20)
    ),
    
    # Adventure Activities
    "Hiking": ActivityMetadata(
        name="Hiking",
        category=ActivityCategory.ADVENTURE,
        energy_level=ActivityEnergy.HIGH,
        preferred_times=[ActivityTime.MORNING],
        duration_range=(3.0, 6.0),
        indoor=False,
        requires_booking=False,
        weather_dependent=True,
        typical_cost_range=(20, 50)
    ),
    "Bike Tour": ActivityMetadata(
        name="Bike Tour",
        category=ActivityCategory.ADVENTURE,
        energy_level=ActivityEnergy.HIGH,
        preferred_times=[ActivityTime.MORNING, ActivityTime.AFTERNOON],
        duration_range=(2.0, 4.0),
        indoor=False,
        requires_booking=True,
        weather_dependent=True,
        typical_cost_range=(30, 70)
    ),
    
    # Relaxation Activities
    "Garden Visit": ActivityMetadata(
        name="Garden Visit",
        category=ActivityCategory.RELAXATION,
        energy_level=ActivityEnergy.LOW,
        preferred_times=[ActivityTime.MORNING, ActivityTime.AFTERNOON],
        duration_range=(1.5, 3.0),
        indoor=False,
        requires_booking=False,
        weather_dependent=True,
        typical_cost_range=(10, 25)
    ),
    "Thermal Bath": ActivityMetadata(
        name="Thermal Bath",
        category=ActivityCategory.RELAXATION,
        energy_level=ActivityEnergy.LOW,
        preferred_times=[ActivityTime.ANY],
        duration_range=(2.0, 4.0),
        indoor=True,
        requires_booking=True,
        weather_dependent=False,
        typical_cost_range=(40, 80)
    )
}

def get_activity_metadata(activity_name: str) -> Optional[ActivityMetadata]:
    """Get metadata for a specific activity."""
    return ACTIVITY_METADATA.get(activity_name)

def get_activities_by_category(category: ActivityCategory) -> List[str]:
    """Get all activities in a specific category."""
    return [name for name, meta in ACTIVITY_METADATA.items() if meta.category == category]

def get_activities_by_time(time: ActivityTime) -> List[str]:
    """Get all activities suitable for a specific time."""
    return [name for name, meta in ACTIVITY_METADATA.items() if time in meta.preferred_times]

def get_activities_by_energy(energy: ActivityEnergy) -> List[str]:
    """Get all activities with a specific energy level."""
    return [name for name, meta in ACTIVITY_METADATA.items() if meta.energy_level == energy]

def get_indoor_activities() -> List[str]:
    """Get all indoor activities."""
    return [name for name, meta in ACTIVITY_METADATA.items() if meta.indoor]

def get_outdoor_activities() -> List[str]:
    """Get all outdoor activities."""
    return [name for name, meta in ACTIVITY_METADATA.items() if not meta.indoor]

def get_weather_dependent_activities() -> List[str]:
    """Get all weather-dependent activities."""
    return [name for name, meta in ACTIVITY_METADATA.items() if meta.weather_dependent]
