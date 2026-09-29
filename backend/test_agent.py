import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models import Incident, IncidentEvidence
from hindsight_memory import retain_incident, close_hindsight_client
from agent import analyze_incident

# Load environment configuration
root_env = backend_dir.parent / ".env"
if root_env.exists():
    load_dotenv(dotenv_path=root_env)
else:
    load_dotenv()

def seed_historical_incidents():
    """Seeds Hindsight Cloud with historical incident postmortems."""
    print("------------------------------------------------------------")
    print("1. Seeding Historical Incidents into Vectorize Hindsight...")
    print("------------------------------------------------------------")

    incidents_to_seed = [
        (
            "INC-001",
            "Incident INC-001:\n"
            "Service: Payment API\n"
            "Severity: SEV-1\n"
            "Evidence: HTTP 500 errors: 82%, DB connections: 98%\n"
            "Root cause: database connection pool exhaustion\n"
            "Resolution: rollback and increase connection pool"
        ),
        (
            "INC-002",
            "Incident INC-002:\n"
            "Service: Payment API\n"
            "Severity: SEV-2\n"
            "Evidence: HTTP 500 errors: 73%, Cache errors: HIGH\n"
            "Root cause: cache configuration regression\n"
            "Resolution: restore cache configuration"
        ),
        (
            "INC-003",
            "Incident INC-003:\n"
            "Service: Payment API\n"
            "Severity: SEV-2\n"
            "Evidence: HTTP 500 errors: 61%, Dependency errors: HIGH\n"
            "Root cause: dependency version mismatch\n"
            "Resolution: pin dependency and rollback"
        )
    ]

    for inc_id, content in incidents_to_seed:
        print(f"-> Retaining historical incident: {inc_id}...")
        retain_incident(content)

    print("All historical incidents retained in Hindsight memory.\n")

def main():
    print("=" * 60)
    print("RecallOps AI Reasoning Engine - End-to-End Test")
    print("=" * 60)

    # 1. Seed historical incidents
    seed_historical_incidents()

    # 2. Define the active incident INC-004
    print("------------------------------------------------------------")
    print("2. Defining Current Production Incident (INC-004)...")
    print("------------------------------------------------------------")

    inc_004 = Incident(
        incident_id="INC-004",
        service="Payment API",
        severity="SEV-2",
        description="High HTTP 500 failure rate and latency spike observed in Payment API.",
        recent_changes="Cache configuration change deployed 20 minutes prior to alert.",
        evidence=IncidentEvidence(
            http_500_errors="79%",
            latency="4.5 seconds",
            database_connections="29%",
            cache_errors="HIGH",
            recent_configuration_change="YES",
            symptoms=[
                "HTTP 500 errors: 79%",
                "latency: 4.5 seconds",
                "database connections: 29%",
                "cache errors: HIGH",
                "recent configuration change: YES"
            ]
        )
    )

    print(inc_004.to_text())
    print("\n------------------------------------------------------------")
    print("3. Executing RecallOps Comparative Reasoning...")
    print("------------------------------------------------------------")
    print("Recalling memories from Hindsight & contrasting with Groq...")

    # 3. Run reasoning engine
    result = analyze_incident(inc_004)

    # 4. Display results
    print("\n" + "=" * 60)
    print("RECALLOPS INCIDENT DIAGNOSIS & REASONING REPORT")
    print("=" * 60)
    print(f"Incident:    {result.incident_id} ({result.service})")
    print(f"Severity:    {result.severity}")
    print(f"Diagnosis:   {result.diagnosis}")
    print(f"Confidence:  {result.confidence}")

    print("\n[Identified Similarities with Historical Incidents]")
    for s in result.similarities:
        print(f"  + {s}")

    print("\n[Identified Contradictions with Historical Incidents]")
    for c in result.contradictions:
        print(f"  - {c}")

    print("\n[Detailed Reasoning]")
    print(result.reasoning)

    print("\n[Recommended Immediate Action]")
    print(f"  -> {result.recommended_action}")

    if result.uncertainty:
        print("\n[Uncertainty & Verification Notes]")
        print(f"  ? {result.uncertainty}")

    print("\n[Recalled Historical Memories Count]")
    print(f"  Total memories retrieved from Hindsight: {len(result.recalled_memories)}")
    for i, mem in enumerate(result.recalled_memories[:3], 1):
        print(f"  ({i}) {mem}")

    print("\n" + "=" * 60)
    print("End-to-End Test Completed Successfully!")
    print("=" * 60)
    close_hindsight_client()

if __name__ == "__main__":
    try:
        main()
    finally:
        close_hindsight_client()
