import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# Support relative and absolute imports
try:
    from .models import Incident, AnalyzeIncidentResponse, LearningRecord
    from .agent import analyze_incident
    from .hindsight_memory import retain_learning
except ImportError:
    from models import Incident, AnalyzeIncidentResponse, LearningRecord
    from agent import analyze_incident
    from hindsight_memory import retain_learning

# Load environment configuration
root_env = Path(__file__).resolve().parent.parent / ".env"
if root_env.exists():
    load_dotenv(dotenv_path=root_env)
else:
    load_dotenv()

app = FastAPI(
    title="RecallOps API",
    description="AI Incident Commander that learns from previous production incidents using Vectorize Hindsight.",
    version="0.1.0"
)

# Enable CORS for future frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Healthcheck endpoint reporting service status and configuration."""
    hindsight_configured = bool(os.getenv("HINDSIGHT_API_KEY"))
    groq_configured = bool(os.getenv("GROQ_API_KEY"))
    groq_model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

    return {
        "status": "healthy",
        "service": "RecallOps Reasoning Engine",
        "hindsight_connected": hindsight_configured,
        "groq_configured": groq_configured,
        "active_groq_model": groq_model
    }

@app.post(
    "/api/incidents/analyze",
    response_model=AnalyzeIncidentResponse,
    status_code=status.HTTP_200_OK
)
def analyze_incident_endpoint(incident: Incident):
    """
    Analyzes an incoming production incident by:
    1. Recalling historical memories from Vectorize Hindsight
    2. Contrasting current evidence with past resolutions
    3. Generating an evidence-based diagnosis with explicit similarities and contradictions
    """
    try:
        result = analyze_incident(incident)
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except RuntimeError as re:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(re)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during incident analysis: {str(e)}"
        )

@app.post(
    "/api/incidents/learn",
    status_code=status.HTTP_200_OK
)
def learn_incident_endpoint(learning: LearningRecord):
    """
    Stores human-confirmed resolution, root cause, and takeaways into Hindsight
    so the AI incident commander learns permanently from this experience.
    """
    try:
        retain_learning(learning)
        return {
            "status": "success",
            "message": f"Experience for incident {learning.incident_id} successfully stored in Hindsight.",
            "learning": learning.model_dump()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retain learning in Hindsight: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
