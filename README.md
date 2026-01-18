# opik-hackathon-agent

The agentic layer of our Commit To Change 2026 hackathon project.

## Overview

This project implements a LangGraph-based agent with Opik tracing integration. The agent classifies user questions and routes them to appropriate handlers (greeting or search).

## Features

- **LangGraph Workflow**: Uses StateGraph to create a conditional routing workflow
- **Opik Integration**: Traces agent execution with Opik for observability
- **Question Classification**: Automatically classifies input questions
- **Modular Handlers**: Separate nodes for greeting and search operations

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for fast Python package management.

1. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a virtual environment and install dependencies:
```bash
uv sync
```

This will create a `.venv` directory and install all dependencies from `pyproject.toml` using the lockfile (`uv.lock`).

3. Activate the virtual environment:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## Usage

Run the agent:
```bash
python app.py
```

The agent will process the example question "Hello, how are you?" and return a response.

## Architecture

The workflow consists of:
- **Entry Point**: `classify_input` - Classifies the incoming question
- **Conditional Routing**: Routes to either `handle_greeting` or `handle_search` based on classification
- **Opik Tracer**: Tracks the entire execution graph for observability

## Dependencies

- `langchain` - Core LangChain functionality
- `langgraph` - Graph-based workflow orchestration
- `opik` - Observability and tracing platform
