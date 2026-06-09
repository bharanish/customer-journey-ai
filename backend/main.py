import os
from fastapi import FastAPI, Header, HTTPException
from httpcore import request
from pydantic import BaseModel
from typing import List, Dict, Any

from workflows.customer_journey_graph import graph

from agents.router_agent import classify_question
from agents.chat_agent import general_chat

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from middleware.logging import LoggingMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from agents.rag_router import (
    is_business_definition
)

from agents.rag_agent import (
    answer_business_question
)

app = FastAPI()

app.add_middleware(
    LoggingMiddleware
)

limiter = Limiter(
    key_func=get_remote_address
)

app.state.limiter = limiter
app.add_middleware(
    SlowAPIMiddleware
)

# Metrics endpoint
Instrumentator().instrument(app).expose(app)

API_KEY = os.getenv("API_KEY")

class ChatRequest(BaseModel):
    question: str
    history: List[Dict[str, Any]] = []


@app.get("/")
def root():
    return {
        "message": "Customer Journey AI Analyst"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.post("/chat")
@limiter.limit("20/minute")
def chat(
    request: Request,
    payload: ChatRequest,
    x_api_key: str = Header(None)
):

    if x_api_key != API_KEY:
        raise HTTPException(
        	status_code=401,
       		detail="Unauthorized"
    	)

    # --------------------------------
    # RAG Business Dictionary
    # --------------------------------

    if is_business_definition(payload.question) == "YES":

        answer = answer_business_question(
            payload.question
        )

        return {
            "type": "rag",
            "answer": answer,
            "sources": result["sources"]
        }

    # --------------------------------
    # Router Agent
    # --------------------------------

    question_type = classify_question(
        payload.question
    )

    print(
        f"QUESTION TYPE: {question_type}"
    )

    # --------------------------------
    # Analytics Workflow
    # --------------------------------

    if question_type == "DATA_ANALYSIS":

        result = graph.invoke({

            "question": payload.question,
            "history": payload.history,

            "question_status": "",

            "sql": "",
            "safe_sql": True,

            "results": "",
            "results_json": [],

            "visualization": {},

            "insight": "",
            "recommendations": "",

            "steps": []
        })

        result["type"] = "analytics"

        return result

    # --------------------------------
    # General Chat
    # --------------------------------

    answer = general_chat(
        payload.question
    )

    return {
        "type": "general",
        "answer": answer
    }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
