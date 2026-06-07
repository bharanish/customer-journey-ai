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

    sql = clean_sql(sql)

    if sql.strip().endswith("INVALID_COLUMN"):

        state["sql"] = sql

        state["results"] = []

        state["results_json"] = []

        state["insight"] = (
            "Customer segment information is not available "
            "in the current dataset."
        )

        state["recommendations"] = """
        Try one of these questions:

        • Show revenue by channel
        • Show revenue by campaign
        • Show revenue by device
        • Which channel generated highest revenue?
        • What is total revenue?
        """

        state["steps"].append("SQL Agent")

        return state

    state["sql"] = sql
    state["steps"].append("SQL Agent")

    return state

def query_node(state):

    if state.get("sql") == "INVALID_COLUMN":
        return state

    try:

        df = execute_query(state["sql"])

        if len(df) > 20:
            sample_df = df.head(20)
        else:
            sample_df = df

        state["results"] = sample_df.to_string()
        state["results_json"] = df.to_dict(orient="records")

        state["steps"].append("Query Executor")

    except Exception as e:

        state["results"] = str(e)
        state["results_json"] = []

        state["insight"] = "Query execution failed."

        state["recommendations"] = (
            "Try rephrasing the question."
        )

    return state

def insight_node(state):

    if state.get("sql") == "INVALID_COLUMN":
        return state

    insight = generate_insight(
        state["question"],
        state["results"]
    )

    state["insight"] = insight
    state["steps"].append("Insight Agent")

    return state

def recommendation_node(state):

    if state.get("sql") == "INVALID_COLUMN":
        return state

    recommendations = generate_recommendation(
        state["insight"]
    )

    state["recommendations"] = recommendations
    state["steps"].append("Recommendation Agent")

    return state

def route_after_sql(state):

    if state["sql"] == "INVALID_COLUMN":
        return END

    return "query_executor"

builder = StateGraph(AgentState)

builder.add_node("sql_agent", sql_node)
builder.add_node("query_executor", query_node)
builder.add_node("insight_agent", insight_node)
builder.add_node("recommendation_agent", recommendation_node)

builder.set_entry_point("sql_agent")

builder.add_conditional_edges(
    "sql_agent",
    route_after_sql,
    {
        "query_executor": "query_executor",
        END: END
    }
)
builder.add_edge("query_executor", "insight_agent")
builder.add_edge("insight_agent", "recommendation_agent")
builder.add_edge("recommendation_agent", END)

graph = builder.compile()

if __name__ == "__main__":

    result = graph.invoke({
        "question": "Show revenue by customer segment",
        "sql": "",
        "results": "",
        "results_json": [],
        "insight": "",
        "recommendations": "",
        "steps": []
    })

    print(result)
