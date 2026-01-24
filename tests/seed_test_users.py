"""
Seed test users for interaction endpoint testing.

This script creates two dummy users with hardcoded unique_id values
that can be reused for testing the /interactions endpoint without
requiring a mobile app.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

# Hardcoded test user IDs for consistent testing
TEST_USER_1_ID = "test-user-1-uuid"
TEST_USER_2_ID = "test-user-2-uuid"

TEST_USERS = [
    {
        "unique_id": TEST_USER_1_ID,
        "email": "test.user1@example.com",
        "full_name": "Test User One",
        "city": "New York"
    },
    {
        "unique_id": TEST_USER_2_ID,
        "email": "test.user2@example.com",
        "full_name": "Test User Two",
        "city": "San Francisco"
    }
]


async def seed_test_users():
    """Seeds test users into the database."""

    pool = await asyncpg.create_pool(
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        database=os.getenv("POSTGRES_DB", "app"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )

    try:
        async with pool.acquire() as conn:
            for user in TEST_USERS:
                # Check if user already exists
                existing = await conn.fetchrow(
                    "SELECT id, unique_id, email FROM users WHERE unique_id = $1",
                    user["unique_id"]
                )

                if existing:
                    print(f"✓ User already exists: {user['email']} (unique_id: {user['unique_id']})")
                else:
                    # Insert new user
                    await conn.execute("""
                        INSERT INTO users (unique_id, email, full_name, city)
                        VALUES ($1, $2, $3, $4)
                    """, user["unique_id"], user["email"], user["full_name"], user["city"])
                    print(f"✓ Created user: {user['email']} (unique_id: {user['unique_id']})")

            print("\n" + "="*60)
            print("Test users seeded successfully!")
            print("="*60)
            print(f"\nTest User 1 ID: {TEST_USER_1_ID}")
            print(f"Test User 2 ID: {TEST_USER_2_ID}")
            print("\nYou can now use these IDs in test_interactions.py")

    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(seed_test_users())
