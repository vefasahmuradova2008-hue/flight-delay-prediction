from pydantic import BaseModel
from typing import Optional, List

class FlightRequest(BaseModel):
    airline: str
    route: str
    departure: str
    weather: str
    congestion: str
    aircraft_age: Optional[int] = None
    context: Optional[str] = None

class DelayPrediction(BaseModel):
    delay_probability: int
    risk_level: str
    estimated_delay_minutes: Optional[int]
    main_factors: List[str]
    recommendation: str