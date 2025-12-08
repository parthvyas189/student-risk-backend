import os
import httpx
from dotenv import load_dotenv

load_dotenv()

# Get the URL from environment variables
# Default to localhost for testing if not set
MODEL_URL = os.getenv("MODEL_SERVICE_URL", "http://localhost:5001/predict")

async def get_risk_prediction(student_id: int, attendance: int, homework: int, test_score: float, behavior: bool):
    """
    Sends data to the external Model Service and returns the risk analysis.
    """
    payload = {
        "student_id": student_id,
        "attendance_score": attendance,
        "homework_submission_rate": homework,
        "test_score_average": test_score,
        "behavior_flag": behavior
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(MODEL_URL, json=payload, timeout=10.0)
            response.raise_for_status() # Raise error if status is 4xx or 5xx
            return response.json()
        except Exception as e:
            print(f"Error calling Model Service: {e}")
            # Fallback if model is down (prevents Backend crash)
            return {
                "risk_score": -1.0, 
                "risk_level": "Unknown", 
                "risk_reasons": ["Model Service Unavailable"]
            }