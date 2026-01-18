# opik-hackathon-agent

The agentic layer of our Commit To Change 2026 hackathon project.

## Overview

This project implements a LangGraph-based agent with Opik tracing integration. The agent classifies user questions and routes them to appropriate handlers (greeting or search).

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
## Adding/Removing a package

```bash
uv add <package_name>
uv remove <package_name>
```

## Add a dev dependency:
```bash
uv add --dev <package_name>
```

## Running the agent:
```bash
uv run app.py
```


## Architecture

The workflow consists of:
- **Entry Point**: `classify_input` - Classifies the incoming question
- **Conditional Routing**: Routes to either `handle_greeting` or `handle_search` based on classification
- **Opik Tracer**: Tracks the entire execution graph for observability

## Dependencies

- `langchain` - Core LangChain functionality
- `langgraph` - Graph-based workflow orchestration
- `opik` - Observability and tracing platform
