import os
from typing import Optional, List
from pathlib import Path
from dotenv import load_dotenv

# Support relative and absolute imports
try:
    from .models import Incident, HistoricalMemory, Diagnosis, AnalyzeIncidentResponse
    from .hindsight_memory import recall_incidents
    from .llm import analyze_with_groq
except ImportError:
    from models import Incident, HistoricalMemory, Diagnosis, AnalyzeIncidentResponse
    from hindsight_memory import recall_incidents
    from llm import analyze_with_groq

# Load environment configuration
root_env = Path(__file__).resolve().parent.parent / ".env"
if root_env.exists():
    load_dotenv(dotenv_path=root_env)
else:
    load_dotenv()

def build_recall_query(incident: Incident) -> str:
    """Constructs a natural language search query from the current incident."""
    tokens = [f"{incident.service} incident"]
    if incident.description:
        tokens.append(incident.description)
    if incident.evidence.http_500_errors:
        tokens.append(f"HTTP 500 {incident.evidence.http_500_errors}")
    if incident.evidence.cache_errors:
        tokens.append(f"cache errors {incident.evidence.cache_errors}")
    if incident.evidence.database_connections:
        tokens.append(f"database connections {incident.evidence.database_connections}")
    for symptom in incident.evidence.symptoms:
        tokens.append(symptom)

    return " ".join(tokens)

def analyze_incident(
    incident: Incident,
    bank_id: Optional[str] = None,
    groq_model: Optional[str] = None
) -> AnalyzeIncidentResponse:
    """
    Executes the RecallOps comparative reasoning loop:
    1. Recalls relevant historical incident memories from Hindsight.
    2. Sends current evidence and historical memories to Groq.
    3. Analyzes similarities and contradictions.
    4. Produces a reasoned diagnosis, recommended action, and uncertainty statement.
    """
    # 1. Build query and retrieve historical memories from Hindsight
    query = build_recall_query(incident)
    try:
        memories: List[HistoricalMemory] = recall_incidents(
            query=query,
            bank_id=bank_id,
            max_results=8
        )
    except Exception as e:
        raise RuntimeError(f"Incident reasoning aborted: Hindsight memory recall failed: {e}") from e

    # 2. Perform AI reasoning with Groq
    try:
        diagnosis: Diagnosis = analyze_with_groq(
            current_incident=incident,
            historical_memories=memories,
            model=groq_model
        )
    except Exception as e:
        raise RuntimeError(f"Incident reasoning aborted: LLM analysis failed: {e}") from e

    # 3. Assemble and return the complete response
    return AnalyzeIncidentResponse(
        incident_id=incident.incident_id,
        service=incident.service,
        severity=incident.severity,
        diagnosis=diagnosis.diagnosis,
        confidence=diagnosis.confidence,
        reasoning=diagnosis.reasoning,
        similarities=diagnosis.similarities,
        contradictions=diagnosis.contradictions,
        recommended_action=diagnosis.recommended_action,
        uncertainty=diagnosis.uncertainty,
        recalled_memories=[m.text for m in memories]
    )
