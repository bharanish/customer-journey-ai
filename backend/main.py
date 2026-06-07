from fastapi import FastAPI
from pydantic import BaseModel
from agents.sql_agent import generate_sql, clean_sql
from agents.query_executor import execute_query
from agents.insight_agent import generate_insight
from agents.recommendation_agent import generate_recommendation
from workflows.customer_journey_graph import graph

app = FastAPI()

class ChatRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {
        "message": "Customer Journey AI Analyst"
    }

@app.post("/chat")
def chat(request: ChatRequest):

    result = graph.invoke({
        "question": request.question,
        "steps": []
    })
    
    return {
    "question": result["question"],
    "sql": result["sql"],
    "results": result["results_json"],
    "insight": result["insight"],
    "recommendations": result["recommendations"],
    "steps": result["steps"]
}
