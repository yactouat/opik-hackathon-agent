# opik-hackathon-agent

The agentic layer of our Commit To Change 2026 hackathon project.

## Overview

This project scaffolds a LangGraph-based agent with Opik tracing integration. The agent classifies user questions and routes them to appropriate handlers (greeting or search).

## Features

- **LangGraph Workflow**: Uses StateGraph to create a conditional routing workflow
- **Opik Integration**: Traces agent execution with Opik for observability
- **Question Classification**: Automatically classifies input questions
- **Modular Handlers**: Separate nodes for greeting and search operations

# Project Setup & Management with uv

## 1. Installation

macOS / Linux
```bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
```
Windows
```bash
powershell -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
```
## Setting up

```bash
uv sync
```

## Database Setup

1. **Start the Database**
   This project uses PostgreSQL 17 (LTS). Start the database service:
   ```bash
   docker-compose up -d
   ```

2. **Configure Environment Variables**
   Copy the example environment file and configure it:
   ```bash
   cp env.example .env
   ```
   The `.env` file should include your database credentials:
   ```
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=app
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```

## Adding/Removing a package

```bash
uv add <package_name>
uv remove <package_name>
```

## Add a dev dependency:
```bash
uv add --dev <package_name>
```

## Running the API:
```bash
uv run uvicorn app:app --reload
```

## Exposing the API with ngrok

To expose your local API to the internet (necessary to run [the mobile app](https://github.com/WissamElJ/opik-hackathon-mobile)), use `ngrok`.

1. **Install ngrok**: Follow the instructions at [ngrok.com/download](https://ngrok.com/download).

2. **Start the API**: Ensure your API is running locally:
   ```bash
   uv run uvicorn app:app --reload
   ```

3. **Expose the port**: In a separate terminal, run:
   ```bash
   ngrok http 8000
   ```

4. **Use the URL**: ngrok will generate a public URL (e.g., `https://<random-id>.ngrok-free.app`) that forwards traffic to your localhost:8000. You can use this URL to access your API endpoints externally.


## API Endpoints

The API provides the following endpoints:

### GET /

**Health check endpoint**

Returns the API status and database connection state.

**Response:**
```json
{
  "msg": "Paramis API is up and running",
  "data": {
    "status": {
      "database": true
    }
  }
}
```

### POST /users

**Create or update a user**

Creates a new user if they don't exist (based on email), or updates an existing user's information. Authorization is validated via the `sub` field.

**Request Payload:**
```json
{
  "city": "string",
  "email": "string",
  "full_name": "string",
  "sub": "string (UUID - subject identifier for authorization)"
}
```

**Behavior:**
- If user with email doesn't exist: creates new user with `sub` as `unique_id`
- If user exists: updates `full_name` and `city` only if they've changed
- Authorization: `sub` must match the existing user's `unique_id` for updates
- Email serves as the unique identifier for lookup

**Response:**
```json
{
  "msg": "User payload processed successfully | User updated | User already up to date"
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized (sub doesn't match existing user's unique_id)
- `503`: Database not available

### POST /interactions

**Record an interaction between users**

Processes a free-form text description of an interaction and extracts structured information using AI (the 5 Ws: Who, Where, When, Why, How), then stores it in the database.

**Request Payload:**
```json
{
  "input": "string (free-form text describing the interaction)",
  "user_id": "string (unique_id of the user recording the interaction)",
  "target_user_id": "string (unique_id of the user with whom the interaction occurred)",
  "sub": "string (UUID for authorization - must match user_id)"
}
```

**Behavior:**
- Validates that `sub` matches `user_id` (requester must be the recorder)
- Looks up both users by their `unique_id` values
- Processes the `input` text using LangGraph + Gemini AI to extract:
  - **who**: Name of the person
  - **where**: Location of the interaction
  - **when**: Time/date of the interaction
  - **why**: Reason/purpose of the interaction
  - **how**: Context/manner of the interaction
- Stores the extracted information in the `interactions` table
- Execution is traced with Opik for observability

**Response:**
```json
{
  "msg": "Interaction recorded successfully"
}
```

**Status Codes:**
- `200`: Success
- `400`: Interaction content could not be processed
- `401`: Unauthorized (sub doesn't match user_id)
- `404`: User or target user not found
- `500`: Internal server error during processing
- `503`: Database not available

**Example:**
```bash
curl -X POST http://localhost:8000/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "input": "I met John at the coffee shop yesterday. We talked about AI and machine learning for hours.",
    "user_id": "user-uuid-123",
    "target_user_id": "john-uuid-456",
    "sub": "user-uuid-123"
  }'
```

This will extract and store:
- who: "John"
- where: "the coffee shop"
- when: "yesterday"
- why: "talked about AI and machine learning"
- how: "met at the coffee shop, conversation"

## Testing the `/interactions` Endpoint

You can test the `/interactions` endpoint without a mobile app using the provided test scripts in the `tests` folder.

### Step 1: Seed Test Users

First, create dummy test users with hardcoded `unique_id` values:

```bash
uv run python tests/seed_test_users.py
```

This will create two test users:
- **Test User 1**: `unique_id: test-user-1-uuid`, email: `test.user1@example.com`
- **Test User 2**: `unique_id: test-user-2-uuid`, email: `test.user2@example.com`

The script is idempotent - you can run it multiple times safely. If the users already exist, it will skip creation.

### Step 2: Run the Interaction Test

With the API running and test users seeded, test the endpoint:

```bash
uv run python tests/test_interactions.py
```

This script will:
1. Check that the API and database are connected
2. Send a sample interaction from Test User 1 about Test User 2
3. Display the response and status
4. Process the interaction using the LangGraph + Gemini AI pipeline
5. Store the extracted "5 Ws" in the database

### Manual Testing with curl

You can also manually test with the hardcoded user IDs:

```bash
curl -X POST http://localhost:8000/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "input": "I met Test User Two at the park this morning. We discussed the weather and planned a weekend hike.",
    "user_id": "test-user-1-uuid",
    "target_user_id": "test-user-2-uuid",
    "sub": "test-user-1-uuid"
  }'
```

### Verifying Stored Interactions

To verify interactions were stored in the database:

```bash
docker exec -it opik-hackathon-agent-postgres-1 psql -U postgres -d app -c "SELECT * FROM interactions ORDER BY created_at DESC LIMIT 5;"
```

## Architecture

The workflow consists of:
- **Entry Point**: `classify_input` - Classifies the incoming question
- **Conditional Routing**: Routes to either `handle_greeting` or `handle_search` based on classification
- **Opik Tracer**: Tracks the entire execution graph for observability

## Running the Interaction Extraction Script

The `graphs/extract_interaction_with_a_person_card.py` script uses Google's Gemini AI to extract structured information about a person interaction from free-form text.

### What the Script Does

Given a text describing an interaction with someone, the script extracts the "5 Whys" (Who, Where, When, Why, How):
- **who**: The name of the person with whom the interaction took place
- **where**: Where the interaction took place
- **when**: When the interaction took place
- **why**: Why the interaction took place (the reason/purpose)
- **how**: How the interaction took place (the context/manner)

### Setup

1. **Get a Google AI Studio API Key**
   - Go to [Google AI Studio](https://aistudio.google.com/)
   - Sign in with your Google account
   - Click on "Get API Key" in the left sidebar
   - Create a new API key or use an existing one
   - Copy the key

2. **Configure Environment Variables**
   - Copy the example environment file:
     ```bash
     cp env.example .env
     ```
   - Open `.env` and add your Google API key:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

3. **Run the Script**
   ```bash
   uv run python graphs/extract_interaction_with_a_person_card.py
   ```

### Example

The script includes a sample input:
> "I met John at the coffee shop yesterday. We talked about AI and machine learning for hours. It was a really stimulating conversation!"

This would extract:
```python
{
    'input': 'I met John at the coffee shop yesterday. We talked about AI and machine learning for hours. It was a really stimulating conversation!', 'interaction_card': InteractionWithAPersonCard(
        who='John',
        where='the coffee shop',
        when='yesterday',
        why='talked about AI and machine learning',
        how='met at the coffee shop, conversation'
    )
}
```

The execution is traced with Opik, so you can view the full graph execution in your Opik dashboard.

## Dependencies

- `asyncpg` - Async PostgreSQL driver (no ORM)
- `fastapi` - Web framework for building APIs
- `langchain` - Core LangChain functionality
- `langchain-google-genai` - Google Gemini integration for LangChain
- `langgraph` - Graph-based workflow orchestration
- `opik` - Observability and tracing platform
- `uvicorn` - ASGI server for running FastAPI
