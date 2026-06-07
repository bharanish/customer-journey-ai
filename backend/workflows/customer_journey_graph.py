from typing import TypedDict
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from agents.sql_agent import generate_sql, clean_sql
from agents.query_executor import execute_query
from agents.insight_agent import generate_insight
from agents.recommendation_agent import generate_recommendation
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    question: str
    sql: str
    results: str
    results_json: list
    insight: str
    recommendations: str
    steps: list

def sql_node(state):

    sql = generate_sql(state["question"])

    state["sql"] = clean_sql(sql)
    state["steps"].append("SQL Agent")

    return state

def query_node(state):

    df = execute_query(state["sql"])

    state["results"] = df.to_string()

    state["results_json"] = df.to_dict(orient="records")
    state["steps"].append("Query Executor")

    return state

def insight_node(state):

    insight = generate_insight(
        state["question"],
        state["results"]
    )

    state["insight"] = insight
    state["steps"].append("Insight Agent")

    return state

def recommendation_node(state):

    recommendations = generate_recommendation(
        state["insight"]
    )

    state["recommendations"] = recommendations
    state["steps"].append("Recommendation Agent")

    return state

builder = StateGraph(AgentState)

builder.add_node("sql_agent", sql_node)
builder.add_node("query_executor", query_node)
builder.add_node("insight_agent", insight_node)
builder.add_node("recommendation_agent", recommendation_node)

builder.set_entry_point("sql_agent")

builder.add_edge("sql_agent", "query_executor")
builder.add_edge("query_executor", "insight_agent")
builder.add_edge("insight_agent", "recommendation_agent")
builder.add_edge("recommendation_agent", END)

graph = builder.compile()

if __name__ == "__main__":

    result = graph.invoke({
        "question": "Which channel generated highest revenue?"
    })

    print(result)
