import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from hindsight_client import Hindsight

def main():
    # 1. Load environment variables from .env file
    # Searches both the root directory and current directory
    root_env = Path(__file__).resolve().parent.parent / ".env"
    if root_env.exists():
        load_dotenv(dotenv_path=root_env)
    else:
        load_dotenv()

    api_url = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io")
    api_key = os.getenv("HINDSIGHT_API_KEY")
    bank_id = os.getenv("HINDSIGHT_BANK_ID", "recallops")

    print("=" * 60)
    print("RecallOps - Hindsight Memory Test")
    print("=" * 60)

    # Validate required credentials
    if not api_key:
        print("\n[ERROR] HINDSIGHT_API_KEY is missing!")
        print("Please follow these steps:")
        print("1. Create a '.env' file in the project root by copying '.env.example'")
        print("2. Add your Hindsight API key: HINDSIGHT_API_KEY=your_key_here")
        print("3. Run this script again.")
        sys.exit(1)

    # 2. Connect to Hindsight Cloud
    print(f"\n1. Connecting to Hindsight Cloud at: {api_url}")
    client = Hindsight(base_url=api_url, api_key=api_key)

    # 3. Create or use the bank
    print(f"\n2. Setting up memory bank: '{bank_id}'...")
    try:
        client.create_bank(
            bank_id=bank_id,
            name="RecallOps Incident Memory",
            mission="Store and recall production incidents, postmortems, root causes, and runbook remediations."
        )
        print(f"   Created new bank '{bank_id}'.")
    except Exception as e:
        # If the bank already exists or was previously created, proceed
        print(f"   Bank '{bank_id}' is ready to use.")

    # 4. Retain one realistic production incident
    incident_data = (
        "Incident INC-4092: Checkout Service 504 Gateway Timeout Outage.\n"
        "Summary: On 2026-04-12 at 14:20 UTC, the Checkout Service experienced a surge in 504 Gateway Timeouts.\n"
        "Root Cause: A connection pool leak in the Redis session cache caused all worker connections to exhaust "
        "during high traffic spikes, blocking incoming HTTP requests.\n"
        "Resolution: Engineers restarted the checkout-service pods, purged stale Redis connections, and applied "
        "a hotfix setting max_connections=500 with a 3-second connection timeout and keep-alive health checks.\n"
        "Mitigation: Added Redis connection pool saturation alerts at 80% threshold and enabled horizontal pod autoscaling."
    )

    print(f"\n3. Retaining production incident in bank '{bank_id}'...")
    retain_response = client.retain(bank_id=bank_id, content=incident_data)
    print("   Incident retained successfully!")

    # 5. Recall the incident using a natural-language query
    query = "Why did the checkout service throw 504 gateway timeout errors and how was it fixed?"
    print(f"\n4. Recalling incident memory with query:\n   \"{query}\"")
    recall_response = client.recall(bank_id=bank_id, query=query)

    # 6. Print the retrieved memory
    print("\n" + "=" * 60)
    print("RETRIEVED MEMORY FROM HINDSIGHT:")
    print("=" * 60)

    if recall_response.results:
        for i, item in enumerate(recall_response.results, 1):
            print(f"\n[Result {i}]")
            print(item.text)
    else:
        print("\nNo memories returned for this query yet.")
        print("Raw response:", recall_response)

    print("\n" + "=" * 60)
    print("Test finished successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
