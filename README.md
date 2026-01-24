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


## Architecture

The workflow consists of:
- **Entry Point**: `classify_input` - Classifies the incoming question
- **Conditional Routing**: Routes to either `handle_greeting` or `handle_search` based on classification
- **Opik Tracer**: Tracks the entire execution graph for observability

## Running the Interaction Extraction Script

The `graphs/extract_interaction_with_a_person_card.py` script uses Google's Gemini AI to extract structured information about a person interaction from free-form text.

### What the Script Does

Given a text describing an interaction with someone, the script extracts:
- **who**: The name of the person you interacted with
- **where**: Where the interaction took place
- **shared_interests**: Topics or interests you discussed
- **was_stimulating**: Whether the conversation was particularly engaging
- **why_took_place**: The reason for the interaction
- **additional_tags**: Other relevant descriptors

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
        additional_tags=['AI', 'machine learning', 'coffee shop'], 
        shared_interests=['AI', 'machine learning'], 
        was_stimulating=True, 
        where='the coffee shop', 
        when='yesterday', 
        who='John'
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
