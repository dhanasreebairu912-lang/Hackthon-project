from typing import Any, Optional, Union
from pydantic import BaseModel, Field

class IncidentEvidence(BaseModel):
    """Evidence metrics and symptoms observed during an incident."""
    metrics: dict[str, Any] = Field(default_factory=dict, description="Dictionary of observed metric values")
    symptoms: list[str] = Field(default_factory=list, description="Observed symptom statements")
    cache_errors: Optional[str] = None
    database_connections: Optional[str] = None
    http_500_errors: Optional[str] = None
    latency: Optional[str] = None
    recent_configuration_change: Optional[Union[str, bool]] = None

    def to_summary(self) -> str:
        """Format evidence into a concise human-readable summary."""
        parts = []
        if self.http_500_errors:
            parts.append(f"HTTP 500 errors: {self.http_500_errors}")
        if self.latency:
            parts.append(f"Latency: {self.latency}")
        if self.database_connections:
            parts.append(f"Database connections: {self.database_connections}")
        if self.cache_errors:
            parts.append(f"Cache errors: {self.cache_errors}")
        if self.recent_configuration_change is not None:
            parts.append(f"Recent configuration change: {self.recent_configuration_change}")

        # Include any extra custom metrics
        for key, value in self.metrics.items():
            readable_key = key.replace("_", " ").title()
            parts.append(f"{readable_key}: {value}")

        # Include symptoms
        for symptom in self.symptoms:
            if symptom not in parts:
                parts.append(symptom)

        return "\n".join(f"- {p}" for p in parts) if parts else "No detailed metrics recorded."


class Incident(BaseModel):
    """Representation of an active or historical production incident."""
    incident_id: str = Field(..., description="Unique incident identifier, e.g. INC-004")
    service: str = Field(..., description="Target service or microservice name, e.g. Payment API")
    severity: str = Field(..., description="Incident severity level, e.g. SEV-1, SEV-2")
    description: Optional[str] = Field(default="", description="Incident summary or alert context")
    evidence: IncidentEvidence = Field(default_factory=IncidentEvidence, description="Observed evidence")
    recent_changes: Optional[str] = Field(default=None, description="Recent deployments or config changes")

    def to_text(self) -> str:
        """Formats the incident as a clear document for retaining or LLM context."""
        text = [
            f"Incident ID: {self.incident_id}",
            f"Service: {self.service}",
            f"Severity: {self.severity}",
        ]
        if self.description:
            text.append(f"Description: {self.description}")
        if self.recent_changes:
            text.append(f"Recent Changes: {self.recent_changes}")
        text.append("Evidence:")
        text.append(self.evidence.to_summary())
        return "\n".join(text)


class HistoricalMemory(BaseModel):
    """Memory item recalled from Vectorize Hindsight."""
    memory_id: str
    text: str
    type: Optional[str] = "fact"
    relevance_score: Optional[float] = None


class Diagnosis(BaseModel):
    """AI reasoning output comparing historical memories against current evidence."""
    diagnosis: str = Field(..., description="Likely root cause diagnosis")
    confidence: str = Field(..., description="Confidence level: HIGH, MEDIUM, or LOW")
    reasoning: str = Field(..., description="Detailed comparative reasoning")
    similarities: list[str] = Field(default_factory=list, description="Evidence points matching historical incidents")
    contradictions: list[str] = Field(default_factory=list, description="Evidence points contradicting historical diagnoses")
    recommended_action: str = Field(..., description="Next operational investigation or remediation step")
    uncertainty: Optional[str] = Field(default=None, description="Explicit statement of uncertainty or alternative hypotheses")


class AnalyzeIncidentResponse(BaseModel):
    """Complete response returned by the RecallOps reasoning API."""
    incident_id: str
    service: str
    severity: str
    diagnosis: str
    confidence: str
    reasoning: str
    similarities: list[str]
    contradictions: list[str]
    recommended_action: str
    uncertainty: Optional[str] = None
    recalled_memories: list[str] = Field(default_factory=list)


class LearningRecord(BaseModel):
    """Postmortem learning or confirmed resolution to retain in Hindsight."""
    incident_id: str
    service: str
    confirmed_root_cause: str
    resolution: str
    key_learnings: Optional[str] = None
