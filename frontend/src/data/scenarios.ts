import { Incident } from "../types/incident";

export interface DemoScenario {
  id: string;
  name: string;
  badge: string;
  description: string;
  incident: Incident;
}

export const DEMO_SCENARIOS: DemoScenario[] = [
  {
    id: "contradictory",
    name: "3. Contradictory Incident (Primary Demo)",
    badge: "INC-004",
    description: "Tests contradiction detection: 29% DB connections contradict DB pool exhaustion, pointing to cache regression.",
    incident: {
      incident_id: "INC-004",
      service: "Payment API",
      severity: "SEV-2",
      description: "High HTTP 500 failure rate and latency spike observed in Payment API.",
      recent_changes: "Cache configuration change deployed 20 minutes prior to alert.",
      evidence: {
        http_500_errors: "79%",
        latency: "4.5 seconds",
        database_connections: "29%",
        cache_errors: "HIGH",
        recent_configuration_change: "YES",
        symptoms: [
          "HTTP 500 errors: 79%",
          "latency: 4.5 seconds",
          "database connections: 29%",
          "cache errors: HIGH",
          "recent configuration change: YES"
        ]
      }
    }
  },
  {
    id: "cold-start",
    name: "1. Cold Start Incident",
    badge: "INC-000",
    description: "New failure mode on Auth Gateway without prior historical postmortems in Hindsight.",
    incident: {
      incident_id: "INC-000",
      service: "Auth Gateway",
      severity: "SEV-3",
      description: "Sudden spike in 401 Unauthorized responses across all external client integrations.",
      recent_changes: "TLS certificate rotated 1 hour ago.",
      evidence: {
        http_500_errors: "0%",
        latency: "1.1 seconds",
        database_connections: "18%",
        cache_errors: "NONE",
        recent_configuration_change: "YES",
        symptoms: [
          "HTTP 401 errors: 72%",
          "token validation errors: HIGH",
          "database connections: 18%",
          "TLS certificate rotated: YES"
        ]
      }
    }
  },
  {
    id: "similar",
    name: "2. Similar Incident",
    badge: "INC-005",
    description: "Matches historical INC-001: 96% DB connections and high 500s indicate DB connection pool exhaustion.",
    incident: {
      incident_id: "INC-005",
      service: "Payment API",
      severity: "SEV-1",
      description: "Payment API critical outage with database timeout warnings.",
      recent_changes: "Flash sale campaign traffic started 15 minutes ago.",
      evidence: {
        http_500_errors: "84%",
        latency: "6.2 seconds",
        database_connections: "96%",
        cache_errors: "LOW",
        recent_configuration_change: "NO",
        symptoms: [
          "HTTP 500 errors: 84%",
          "latency: 6.2 seconds",
          "database connections: 96%",
          "cache errors: LOW",
          "recent configuration change: NO"
        ]
      }
    }
  },
  {
    id: "learned",
    name: "4. Learned Incident",
    badge: "INC-006",
    description: "Tests recall of the newly confirmed INC-004 postmortem saved back into Hindsight.",
    incident: {
      incident_id: "INC-006",
      service: "Payment API",
      severity: "SEV-2",
      description: "Another cache error burst following microservice update.",
      recent_changes: "Feature flag toggled and cache TTL adjusted.",
      evidence: {
        http_500_errors: "76%",
        latency: "4.1 seconds",
        database_connections: "25%",
        cache_errors: "HIGH",
        recent_configuration_change: "YES",
        symptoms: [
          "HTTP 500 errors: 76%",
          "latency: 4.1 seconds",
          "database connections: 25%",
          "cache errors: HIGH",
          "recent configuration change: YES"
        ]
      }
    }
  }
];
