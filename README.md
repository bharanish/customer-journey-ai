# Customer Journey AI Analyst

## Overview

Customer Journey AI Analyst is an Agentic AI platform that enables business users to ask natural language questions about customer journey data and receive actionable business insights and recommendations.

## Features

* Natural language to SQL generation
* PostgreSQL query execution
* AI-generated business insights
* AI-generated recommendations
* LangGraph agent orchestration
* FastAPI backend
* Streamlit frontend

## Architecture

User Question

→ Streamlit Frontend

→ FastAPI Backend

→ LangGraph Workflow

→ SQL Agent

→ Query Executor

→ Insight Agent

→ Recommendation Agent

→ PostgreSQL

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* OpenAI
* LangGraph
* Streamlit
* SQLAlchemy

## Example Questions

* Which channel generated highest revenue?
* Which campaign performs best?
* Show revenue by device.
* Which channel has the highest conversions?
* Give recommendations to improve revenue.

## Run Backend

```bash
uvicorn main:app --reload
```

## Run Frontend

```bash
streamlit run app.py
```
