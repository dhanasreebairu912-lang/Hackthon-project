import os
import json
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv
from groq import Groq

# Support relative and absolute imports
try:
    from .models import Incident, HistoricalMemory, Diagnosis
except ImportError:
    from models import Incident, HistoricalMemory, Diagnosis

# Load environment configuration
root_env = Path(__file__).resolve().parent.parent / ".env"
if root_env.exists():
    load_dotenv(dotenv_path=root_env)
else:
    load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Default to a verified active model, easily overridable via .env
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

def get_groq_client() -> Groq:
    """Creates and returns an authenticated Groq client."""
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing! Please configure it in your .env file."
        )
    return Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are RecallOps, an expert AI Incident Commander.
Your job is to perform evidence-based comparative incident diagnosis.

Core Principle:
"Historical memory should influence reasoning, not replace reasoning."

CRITICAL RULES:
1. Do NOT blindly copy historical diagnoses.
2. Compare the current metrics and symptoms against recalled historical memories.
3. Explicitly identify SIMILARITIES (which current metrics or symptoms match past incidents).
4. Explicitly identify CONTRADICTIONS (which current metrics or symptoms directly contradict past incidents or their root causes).
   For example, if a past incident had 98% DB connections indicating DB connection pool exhaustion, but the current incident has only 29% DB connections and high cache errors, DB connection pool exhaustion is CONTRADICTED by the data. The evidence indicates a cache issue instead.
5. Provide a likely diagnosis based on the surviving evidence.
6. Provide clear supporting reasoning.
7. Recommend the next immediate investigation or mitigation action.
8. State any uncertainty or alternative hypotheses when appropriate.

You must respond ONLY with a valid JSON object with the following structure:
{
  "diagnosis": "Clear root cause statement",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "reasoning": "Detailed comparative analysis contrasting past memories with current metrics",
  "similarities": ["Similarity point 1", "Similarity point 2"],
  "contradictions": ["Contradiction point 1", "Contradiction point 2"],
  "recommended_action": "Specific investigation or remediation action",
  "uncertainty": "Uncertainty notes or factors requiring manual confirmation"
}
"""

def analyze_with_groq(
    current_incident: Incident,
    historical_memories: List[HistoricalMemory],
    model: Optional[str] = None
) -> Diagnosis:
    """
    Sends the current incident and recalled historical memories to Groq for comparative reasoning.
    Returns a validated Diagnosis object.
    Raises clear errors if the model is unavailable or credentials fail.
    """
    active_model = model or os.getenv("GROQ_MODEL", GROQ_MODEL)
    client = get_groq_client()

    # Format historical memories
    if historical_memories:
        memories_text = "\n".join(
            f"[{i}] {m.text}" for i, m in enumerate(historical_memories, 1)
        )
    else:
        memories_text = "No previous historical memories found for this incident query."

    user_prompt = f"""=== CURRENT INCIDENT ===
{current_incident.to_text()}

=== RECALLED HISTORICAL MEMORIES ===
{memories_text}

Analyze the current incident against the historical memories. Remember: Historical memory should influence reasoning, not replace reasoning. Output JSON only."""

    try:
        response = client.chat.completions.create(
            model=active_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
    except Exception as e:
        error_msg = str(e)
        raise RuntimeError(
            f"Groq API error using model '{active_model}': {error_msg}.\n"
            f"Please verify GROQ_API_KEY and check that GROQ_MODEL in your .env points to an active model."
        ) from e

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError(f"Groq model '{active_model}' returned an empty response.")

    try:
        parsed = json.loads(content)
        return Diagnosis(**parsed)
    except Exception as e:
        raise ValueError(
            f"Failed to parse Groq response into Diagnosis model: {e}\nRaw output: {content}"
        ) from e
