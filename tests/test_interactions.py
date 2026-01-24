"""
Test script for the /interactions endpoint.

This script tests the /interactions endpoint using the seeded test users
without requiring a mobile app. It sends a sample interaction and displays
the response.
"""

import asyncio
import httpx
import sys

# Hardcoded test user IDs (must match seed_test_users.py)
TEST_USER_1_ID = "test-user-1-uuid"
TEST_USER_2_ID = "test-user-2-uuid"

# API base URL (change if running on different host/port)
API_BASE_URL = "http://localhost:8000"


async def test_interaction():
    """Test creating an interaction between two users."""

    # Sample interaction payload
    payload = {
        "input": "I met Test User Two at the coffee shop yesterday. We discussed the new Python project and decided to collaborate on it. It was a productive meeting that lasted about an hour.",
        "user_id": TEST_USER_1_ID,
        "target_user_id": TEST_USER_2_ID,
        "sub": TEST_USER_1_ID  # Must match user_id for authorization
    }

    print("Testing /interactions endpoint")
    print("="*60)
    print(f"\nPayload:")
    print(f"  user_id: {payload['user_id']}")
    print(f"  target_user_id: {payload['target_user_id']}")
    print(f"  input: {payload['input']}")
    print("\nSending request...")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/interactions",
                json=payload
            )

            print("\n" + "="*60)
            print(f"Response Status: {response.status_code}")
            print("="*60)

            if response.status_code == 200:
                result = response.json()
                print(f"\n✓ Success!")
                print(f"Message: {result.get('msg')}")
                print(f"\nThe interaction was processed and stored in the database.")
                print(f"You can verify it by checking the interactions table.")
            else:
                print(f"\n✗ Error!")
                print(f"Response: {response.text}")

        except httpx.ConnectError:
            print("\n✗ Connection Error!")
            print(f"Could not connect to {API_BASE_URL}")
            print("Make sure the API is running with: uv run uvicorn app:app --reload")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Unexpected Error!")
            print(f"Error: {str(e)}")
            sys.exit(1)


async def test_health_check():
    """Test that the API is running."""
    print("Checking API health...")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{API_BASE_URL}/")
            if response.status_code == 200:
                result = response.json()
                db_status = result.get("data", {}).get("status", {}).get("database", False)
                print(f"✓ API is running (database: {'connected' if db_status else 'disconnected'})")
                return db_status
            else:
                print(f"✗ API returned status {response.status_code}")
                return False
        except httpx.ConnectError:
            print(f"✗ Could not connect to {API_BASE_URL}")
            return False


async def main():
    """Main test runner."""
    print("\n" + "="*60)
    print("Interaction Endpoint Test")
    print("="*60 + "\n")

    # Check API health first
    db_connected = await test_health_check()
    if not db_connected:
        print("\nPlease ensure:")
        print("1. The database is running: docker-compose up -d")
        print("2. The API is running: uv run uvicorn app:app --reload")
        print("3. Test users are seeded: uv run python tests/seed_test_users.py")
        sys.exit(1)

    print()

    # Run the interaction test
    await test_interaction()

    print("\n" + "="*60)
    print("Test completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
