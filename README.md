# Customer Journey AI Analyst

## Overview

Customer Journey AI Analyst is an agentic analytics application that turns natural language business questions into SQL, executes queries on a PostgreSQL customer journey dataset, and produces actionable insights and recommendations.

The system also supports Retrieval-Augmented Generation (RAG) for business glossary and KPI definition questions using a vector search over text documents.

## What this project demonstrates

- Natural language understanding for analytics questions
- Safe SQL generation using an LLM prompt with schema awareness
- Runtime SQL validation and execution against PostgreSQL
- Insight extraction and business recommendation generation
- RAG retrieval over a knowledge base for domain definitions
- Full request flow from Streamlit frontend to FastAPI backend

## Architecture

```text
User Question
      ↓
Streamlit Frontend
      ↓
FastAPI Backend (/chat)
      ↓
is_business_definition? ── yes ──> RAG branch
      │                              │
      │                              ↓
      │                        FAISS vector store
      │                              ↓
      │                       LLM answer using context
      │                              ↓
      └─ no ──> question classifier
                    ↓
             DATA_ANALYSIS? ── yes ──> Analytics workflow
                    │                    │
                    │                    ↓
                    │                SQL generation
                    │                    ↓
                    │              SQL safety guard
                    │                    ↓
                    │              PostgreSQL execution
                    │                    ↓
                    │              Visualization + Insight + Recommendation
                    │                    ↓
                    └─ no ──> General chat LLM response
```

## Component breakdown

### Frontend

- `frontend/app.py`
- Streamlit interface that sends `POST /chat` requests to the backend
- Displays three response types: `rag`, `analytics`, and `general`

### Backend API

- `backend/main.py`
- FastAPI app exposing `/chat`
- API key protection using `x-api-key`
- Branches requests into RAG, analytics, or general chat

### RAG path

- `backend/agents/rag_router.py`
  - `is_business_definition(question)` decides whether the question is about terminology, metrics, or definitions
- `backend/agents/rag_agent.py`
  - loads `vector_store/customer_knowledge_base`
  - performs similarity search with OpenAI embeddings
  - builds a prompt using the retrieved passages
  - returns the answer and source documents
- `backend/rag/build_vector_store.py`
  - offline builder for the vector index from `data/*.txt`
  - chunks text, generates embeddings, and saves FAISS index

### Analytics workflow

- `backend/agents/router_agent.py`
  - quick keyword classifier to detect analytics queries
- `backend/workflows/customer_journey_graph.py`
  - LangGraph `StateGraph` defining the execution flow
  - nodes for question validation, SQL gen, guard, execution, visualization, insight, recommendation
- `backend/agents/sql_agent.py`
  - generates SQL from natural language using a prompt-based LLM
  - contains schema, sample examples, and strict SQL rules
- `backend/agents/sql_guard_agent.py`
  - validates SQL safety before execution
- `backend/agents/query_executor.py`
  - runs SQL against PostgreSQL and returns results
- `backend/agents/visualization_agent.py`
  - chooses visualization metadata for frontend display
- `backend/agents/insight_agent.py`
  - converts query results into business insight text
- `backend/agents/recommendation_agent.py`
  - generates business recommendations from the insight

### General chat

- `backend/agents/chat_agent.py`
- fallback LLM response for questions outside analytics and RAG

### Database and data loading

- `backend/database.py`
  - loads `DATABASE_URL` from `backend/.env`
  - creates SQLAlchemy engine
- `backend/load_data.py`
  - loads `data/customer_journey.csv` into PostgreSQL as `customer_journey`

## Execution flow step-by-step

### 1. Setup environment

1. Activate the project virtual environment:
   ```bash
   source env/bin/activate
   ```
2. Ensure `backend/.env` includes:
   ```env
   OPENAI_API_KEY="<your_openai_key>"
   API_KEY="<your_api_key>"
   DATABASE_URL="postgresql://admin:password@localhost:5432/customer_ai"
   ```

### 2. Start dependencies

There are two options:

#### Option A: Run with Docker Compose

1. Create a root `.env` file next to `docker-compose.yml` with:
   ```env
   OPENAI_API_KEY="<your_openai_key>"
   API_KEY="<your_api_key>"
   ```
2. Start the stack:
   ```bash
   docker compose up -d
   ```
3. Confirm services:
   ```bash
   docker compose ps
   ```

#### Option B: Run services manually

1. Start PostgreSQL separately and confirm `DATABASE_URL` points to it.
2. Run the FastAPI backend from `backend/`.

### 3. Load application data

Load the customer journey CSV into PostgreSQL:

```bash
cd backend
../env/bin/python3 load_data.py
```

If using Docker Compose, run:

```bash
docker compose exec api python /app/backend/load_data.py
```

### 4. Build the RAG index (optional)

Use the text files under `data/` to build the knowledge base:

```bash
cd backend/rag
python build_vector_store.py
```

That creates the FAISS index under `vector_store/customer_knowledge_base`.

### 5. Start the backend and frontend

#### Backend

```bash
cd backend
../env/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
streamlit run app.py
```

### 6. Send a request

Example:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: <your_api_key>" \
  -d '{"question":"Show revenue by channel","history":[]}'
```

## Detailed request flow

### RAG question flow

1. `/chat` receives request.
2. `is_business_definition(question)` returns `YES`.
3. `answer_business_question(question)` loads FAISS index.
4. top-k similar chunks are retrieved.
5. the LLM is prompted with retrieved context.
6. result is returned as `type: "rag"`.

This path is used for glossary/definition questions, not analytics queries.

### Analytics question flow

1. `/chat` receives request.
2. `is_business_definition(question)` returns `NO`.
3. `classify_question(question)` returns `DATA_ANALYSIS`.
4. `customer_journey_graph` workflow starts.
5. `question_validation_agent` validates intent and availability.
6. `sql_agent` generates SQL using the schema-aware prompt.
7. `sql_guard_agent` checks SQL safety.
8. `query_executor` runs SQL against PostgreSQL.
9. `visualization_agent` prepares chart metadata.
10. `insight_agent` synthesizes insights from results.
11. `recommendation_agent` produces recommendations.
12. final response is returned as `type: "analytics"`.

### General chat flow

If the question does not match RAG or analytics, `general_chat()` returns a conversational LLM response with `type: "general"`.

## Technical details

### SQL generation prompt design

The SQL prompt is intentionally strict:

- it includes a single table schema
- it lists allowed columns only
- it forbids DDL and DML
- it requires exactly one SELECT statement
- it returns `INVALID_COLUMN` for unsupported requests

This reduces hallucination and keeps SQL generation safe.

### RAG construction

- Text files in `data/` are loaded and chunked.
- Chunks are embedded with OpenAI embeddings.
- FAISS stores vector embeddings and metadata.
- At query time, semantic search retrieves relevant documents.
- The LLM answers using the retrieved context only.

### What the `backend` folder contains

- `main.py` — FastAPI router and request dispatcher
- `config.py` — loads OpenAI API key from `.env`
- `database.py` — builds SQLAlchemy engine from `DATABASE_URL`
- `load_data.py` — loads CSV into PostgreSQL
- `agents/` — LLM agents for SQL, chat, insight, recommendation, RAG, validation, visualization
- `rag/` — vector store builder
- `workflows/` — LangGraph workflow definition

## Interview talking points

- This project is designed as a hybrid analytics agent: it uses both retrieval and structured SQL execution.
- The architecture separates concerns cleanly between frontend, router, workflow, and agent components.
- The SQL generation prompt is a key safety control to prevent unsafe operations.
- The RAG branch is a good example of using semantic search for domain knowledge lookup.
- Data loading and container orchestration are included so the system can run end-to-end.

## Troubleshooting

### `401 Unauthorized`

- Make sure `x-api-key` header exactly matches `API_KEY` in `backend/.env` or root `.env`.

### `DATABASE_URL` errors

- Ensure `backend/.env` contains a valid Postgres connection string.
- If using Docker Compose, use `postgresql://admin:password@postgres:5432/customer_ai` inside the `api` service.

### `relation "customer_journey" does not exist`

- Load the data: `python backend/load_data.py` or `docker compose exec api python /app/backend/load_data.py`

### Docker port conflicts

- If port `5432`, `9090`, or `3000` is already in use, stop the conflicting service or change the host port mapping.

## Summary

This repo demonstrates a full-stack AI analytics app with:
- natural language to SQL pipeline
- database-backed analytics
- retrieval augmented generation for glossary answers
- practical orchestration using Docker and FastAPI
- clear separation between data loading, model prompts, and runtime workflow
