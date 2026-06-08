from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

from workflows.customer_journey_graph import graph

from agents.router_agent import classify_question
from agents.chat_agent import general_chat

from agents.rag_router import (
    is_business_definition
)

from agents.rag_agent import (
    answer_business_question
)

app = FastAPI()


class ChatRequest(BaseModel):
    question: str
    history: List[Dict[str, Any]] = []


@app.get("/")
def root():
    return {
        "message": "Customer Journey AI Analyst"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    # -----------------------------
    # RAG Business Dictionary
    # -----------------------------

    if is_business_definition(
        request.question
    ) == "YES":

        answer = answer_business_question(
            request.question
        )

        return {
            "type": "rag",
            "answer": answer
        }

    # -----------------------------
    # Force SQL-related questions
    # through LangGraph
    # -----------------------------

    q = request.question.lower()

    sql_keywords = [
        "select",
        "drop",
        "delete",
        "truncate",
        "update",
        "insert",
        "alter",
        "table",
        "column",
        "revenue",
        "campaign",
        "channel",
        "device",
        "customer"
    ]

    if any(word in q for word in sql_keywords):

        result = graph.invoke({
            "question": request.question,
            "history": request.history,
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

    # -----------------------------
    # General Chat
    # -----------------------------

    answer = general_chat(
        request.question
    )

    return {
        "type": "general",
        "answer": answer
    }
