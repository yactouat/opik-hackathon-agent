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

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
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
