import os
from fastapi import FastAPI, Header, HTTPException
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
API_KEY = os.getenv("API_KEY")

class ChatRequest(BaseModel):
    question: str
    history: List[Dict[str, Any]] = []


@app.get("/")
def root():
    return {
        "message": "Customer Journey AI Analyst"
    }


@app.post("/chat")
def chat(request: ChatRequest, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
    	raise HTTPException(
        	status_code=401,
       		detail="Unauthorized"
    	)

    # --------------------------------
    # RAG Business Dictionary
    # --------------------------------

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

    # --------------------------------
    # Router Agent
    # --------------------------------

    question_type = classify_question(
        request.question
    )

    print(
        f"QUESTION TYPE: {question_type}"
    )

    # --------------------------------
    # Analytics Workflow
    # --------------------------------

    if question_type == "DATA_ANALYSIS":

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

    # --------------------------------
    # General Chat
    # --------------------------------

    answer = general_chat(
        request.question
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
