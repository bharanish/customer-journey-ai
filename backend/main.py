from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from agents.sql_agent import generate_sql, clean_sql
from agents.query_executor import execute_query
from agents.insight_agent import generate_insight
from agents.recommendation_agent import generate_recommendation
from workflows.customer_journey_graph import graph
from agents.router_agent import classify_question
from agents.chat_agent import general_chat

app = FastAPI()

class ChatRequest(BaseModel):
    question: str
    history: List[str] = []

@app.get("/")
def root():
    return {
        "message": "Customer Journey AI Analyst"
    }

@app.post("/chat")
def chat(request: ChatRequest):

    question_type = classify_question(
        request.question
    )

    if question_type == "GENERAL_QUESTION":

        answer = general_chat(
            request.question
        )

        return {
            "type": "general",
            "answer": answer
        }

    result = graph.invoke({
        "question": request.question,
        "history": request.history,
        "steps": []
    })

    result["type"] = "analytics"

    return result
