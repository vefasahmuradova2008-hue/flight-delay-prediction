import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from models import FlightRequest, DelayPrediction
from predictor import predict_delay
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

stats = {
    "total_requests": 0,
    "high_risk": 0,
    "medium_risk": 0,
    "low_risk": 0,
    "total_delay_minutes": 0
}

app = FastAPI(title="Flight Delay Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Flight Delay API is running"}

@app.get("/metrics-json")
def metrics_json():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_requests": stats["total_requests"],
        "high_risk_count": stats["high_risk"],
        "medium_risk_count": stats["medium_risk"],
        "low_risk_count": stats["low_risk"],
        "avg_delay_minutes": round(stats["total_delay_minutes"] / max(stats["total_requests"], 1), 1)
    }

@app.post("/predict", response_model=DelayPrediction)
def predict(flight: FlightRequest):
    try:
        result = predict_delay(flight, GROQ_API_KEY)

        stats["total_requests"] += 1
        stats["total_delay_minutes"] += result.estimated_delay_minutes or 0
        if result.risk_level in ["High", "Very High"]:
            stats["high_risk"] += 1
        elif result.risk_level == "Medium":
            stats["medium_risk"] += 1
        else:
            stats["low_risk"] += 1

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)