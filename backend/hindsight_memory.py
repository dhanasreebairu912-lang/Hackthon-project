import os
import sys
import time
from pathlib import Path
from typing import Optional, Union, List, Any
from dotenv import load_dotenv
from hindsight_client import Hindsight

# Ensure relative or local import works whether called as package or script
try:
    from .models import Incident, HistoricalMemory, LearningRecord
except ImportError:
    from models import Incident, HistoricalMemory, LearningRecord

# Load environment configuration
root_env = Path(__file__).resolve().parent.parent / ".env"
if root_env.exists():
    load_dotenv(dotenv_path=root_env)
else:
    load_dotenv()

HINDSIGHT_API_URL = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "recallops")

# Singleton client and initialization tracker to reuse connections
_cached_client: Optional[Hindsight] = None
_bank_ensured: bool = False

def get_hindsight_client() -> Hindsight:
    """Creates or returns the cached authenticated Hindsight client."""
    global _cached_client
    if not HINDSIGHT_API_KEY:
        raise ValueError(
            "HINDSIGHT_API_KEY is missing! Please configure it in your .env file."
        )
    if _cached_client is None:
        _cached_client = Hindsight(
            base_url=HINDSIGHT_API_URL,
            api_key=HINDSIGHT_API_KEY,
            timeout=60.0
        )
    return _cached_client

def ensure_bank_exists(client: Hindsight, bank_id: str) -> None:
    """Ensures the specified Hindsight bank is created."""
    global _bank_ensured
    if _bank_ensured:
        return
    try:
        client.create_bank(
            bank_id=bank_id,
            name="RecallOps Incident Memory",
            mission="Store and recall production incidents, postmortems, root causes, and runbook remediations."
        )
        _bank_ensured = True
    except Exception:
        # Bank already exists or is auto-managed
        _bank_ensured = True

def retain_incident(
    incident: Union[Incident, dict, str],
    bank_id: Optional[str] = None
) -> Any:
    """
    Retains a production incident into Hindsight memory.
    Accepts an Incident object, a dictionary, or raw text.
    Includes retry logic for transient connection drops.
    """
    target_bank = bank_id or HINDSIGHT_BANK_ID
    client = get_hindsight_client()
    ensure_bank_exists(client, target_bank)

    if isinstance(incident, Incident):
        content = incident.to_text()
    elif isinstance(incident, dict):
        content = "\n".join(f"{k}: {v}" for k, v in incident.items())
    else:
        content = str(incident)

    last_error = None
    for attempt in range(1, 4):
        try:
            response = client.retain(bank_id=target_bank, content=content)
            return response
        except Exception as e:
            last_error = e
            time.sleep(1.0 * attempt)

    raise RuntimeError(f"Failed to retain incident in Hindsight Cloud after 3 attempts: {last_error}")

def recall_incidents(
    query: str,
    bank_id: Optional[str] = None,
    max_results: int = 10
) -> List[HistoricalMemory]:
    """
    Recalls relevant historical incident memories from Hindsight given a query.
    Returns a list of HistoricalMemory objects.
    """
    target_bank = bank_id or HINDSIGHT_BANK_ID
    client = get_hindsight_client()

    last_error = None
    for attempt in range(1, 4):
        try:
            response = client.recall(bank_id=target_bank, query=query)
            memories: List[HistoricalMemory] = []
            if response and response.results:
                for item in response.results[:max_results]:
                    memories.append(
                        HistoricalMemory(
                            memory_id=item.id,
                            text=item.text,
                            type=getattr(item, "type", "fact")
                        )
                    )
            return memories
        except Exception as e:
            last_error = e
            time.sleep(1.0 * attempt)

    raise RuntimeError(f"Failed to recall memories from Hindsight Cloud: {last_error}")

def retain_learning(
    learning: Union[LearningRecord, dict],
    bank_id: Optional[str] = None
) -> Any:
    """
    Stores a confirmed root cause and resolution back into Hindsight
    so the system learns permanently from every resolved incident.
    """
    target_bank = bank_id or HINDSIGHT_BANK_ID
    client = get_hindsight_client()
    ensure_bank_exists(client, target_bank)

    if isinstance(learning, LearningRecord):
        content = (
            f"Postmortem Learning for {learning.incident_id} ({learning.service}):\n"
            f"Confirmed Root Cause: {learning.confirmed_root_cause}\n"
            f"Resolution: {learning.resolution}\n"
        )
        if learning.key_learnings:
            content += f"Key Learnings: {learning.key_learnings}\n"
    elif isinstance(learning, dict):
        content = "\n".join(f"{k}: {v}" for k, v in learning.items())
    else:
        content = str(learning)

    last_error = None
    for attempt in range(1, 4):
        try:
            return client.retain(bank_id=target_bank, content=content)
        except Exception as e:
            last_error = e
            time.sleep(1.0 * attempt)

    raise RuntimeError(f"Failed to retain learning in Hindsight Cloud: {last_error}")

def close_hindsight_client() -> None:
    """Closes the cached Hindsight client session cleanly."""
    global _cached_client
    if _cached_client is not None:
        try:
            _cached_client.close()
        except Exception:
            pass
        _cached_client = None
