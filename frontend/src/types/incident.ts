export interface IncidentEvidence {
  http_500_errors?: string;
  latency?: string;
  database_connections?: string;
  cache_errors?: string;
  recent_configuration_change?: string | boolean;
  metrics?: Record<string, any>;
  symptoms?: string[];
}

export interface Incident {
  incident_id: string;
  service: string;
  severity: string;
  description: string;
  recent_changes?: string;
  evidence: IncidentEvidence;
}

export interface AnalyzeResponse {
  incident_id: string;
  service: string;
  severity: string;
  diagnosis: string;
  confidence: string;
  reasoning: string;
  similarities: string[];
  contradictions: string[];
  recommended_action: string;
  uncertainty?: string;
  recalled_memories: string[];
}

export interface LearningRecord {
  incident_id: string;
  service: string;
  confirmed_root_cause: string;
  resolution: string;
  key_learnings?: string;
}

export interface HealthStatus {
  status: string;
  service: string;
  hindsight_connected: boolean;
  groq_configured: boolean;
  active_groq_model: string;
}
