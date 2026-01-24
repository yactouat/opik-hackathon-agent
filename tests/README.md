# Tests

This folder contains test utilities for the Paramis API, allowing you to test endpoints without requiring a mobile app.

## Files

- **seed_test_users.py**: Seeds test users with hardcoded `unique_id` values into the database
- **test_interactions.py**: Tests the `/interactions` endpoint using the seeded test users

## Usage

### 1. Seed Test Users

Run the seeder to create test users:

```bash
uv run python tests/seed_test_users.py
```

This creates two users:
- `test-user-1-uuid` (test.user1@example.com)
- `test-user-2-uuid` (test.user2@example.com)

### 2. Test the Interactions Endpoint

Run the test script:

```bash
uv run python tests/test_interactions.py
```

This will send a sample interaction and display the results.

## Prerequisites

Before running tests, ensure:
1. Database is running: `docker-compose up -d`
2. API is running: `uv run uvicorn app:app --reload`
3. Environment variables are configured in `.env`

## Hardcoded Test IDs

The following IDs are hardcoded in both scripts for consistency:

```python
TEST_USER_1_ID = "test-user-1-uuid"
TEST_USER_2_ID = "test-user-2-uuid"
```

You can use these IDs in your own test scripts or manual API calls.
