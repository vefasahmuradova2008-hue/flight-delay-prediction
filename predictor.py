import json
from groq import Groq
from models import FlightRequest, DelayPrediction
def build_prompt(flight: FlightRequest) -> str:
    return f"""You are a flight delay prediction expert. Analyze the following flight details and predict the likelihood of a delay.

Flight details:
- Airline: {flight.airline}
- Route: {flight.route}
- Departure: {flight.departure}
- Weather: {flight.weather}
- Airport congestion: {flight.congestion}
- Aircraft age: {flight.aircraft_age if flight.aircraft_age is not None else 'unknown'} years
- Additional context: {flight.context or 'none'}

Respond ONLY with a valid JSON object (no markdown, no backticks) with exactly this structure:
{{
  "delay_probability": <number 0-100>,
  "risk_level": "<Low|Medium|High|Very High>",
  "estimated_delay_minutes": <number or null>,
  "main_factors": ["<factor 1>", "<factor 2>", "<factor 3>"],
  "recommendation": "<one actionable tip for the traveler>"
}}"""

def predict_delay(flight: FlightRequest, api_key: str) -> DelayPrediction:
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": build_prompt(flight)}]
    )

    raw_text = response.choices[0].message.content.strip()
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    data = json.loads(raw_text)
    return DelayPrediction(**data)