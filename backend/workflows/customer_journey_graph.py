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
from agents.visualization_agent import generate_visualization
from agents.sql_guard_agent import validate_sql
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    question: str
    history: list

    sql: str
    safe_sql: bool

    results: str
    results_json: list

    visualization: dict
    insight: str
    recommendations: str
    
    steps: list

def sql_node(state):

    sql = generate_sql(state["question"], state.get("history", []))

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

def sql_guard_node(state):

    is_safe = validate_sql(
        state["sql"]
    )

    state["safe_sql"] = is_safe

    state["steps"].append(
        "SQL Guard Agent"
    )

    if not is_safe:

        state["results"] = []

        state["results_json"] = []

        state["insight"] = (
            "Unsafe SQL query detected."
        )

        state["recommendations"] = (
            "Only read-only SELECT queries "
            "are allowed."
        )

    return state

def route_after_guard(state):

    if "INVALID_COLUMN" in state["sql"]:
        return END

    if not state["safe_sql"]:
        return END

    return "query_executor"

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

def visualization_node(state):

    if not state["results_json"]:
        return state

    columns = list(
        state["results_json"][0].keys()
    )

    viz = generate_visualization(
        state["question"],
        columns
    )

    state["visualization"] = viz

    state["steps"].append(
        "Visualization Agent"
    )

    return state

# def route_after_sql(state):

#     if state["sql"] == "INVALID_COLUMN":
#         return END

#     return "query_executor"

builder = StateGraph(AgentState)

builder.add_node("sql_agent", sql_node)
builder.add_node("sql_guard_agent", sql_guard_node)
builder.add_node("query_executor", query_node)
builder.add_node("insight_agent", insight_node)
builder.add_node("recommendation_agent", recommendation_node)
builder.add_node("visualization_agent", visualization_node)

builder.set_entry_point("sql_agent")

builder.add_edge(
    "sql_agent",
    "sql_guard_agent"
)

builder.add_conditional_edges(
    "sql_guard_agent",
    route_after_guard,
    {
        "query_executor": "query_executor",
        END: END
    }
)
builder.add_edge("query_executor","visualization_agent")
builder.add_edge("visualization_agent", "insight_agent")
builder.add_edge("insight_agent", "recommendation_agent")
builder.add_edge("recommendation_agent", END)

graph = builder.compile()

if __name__ == "__main__":

    result = graph.invoke({
        "question": "Show revenue by channel",
        "history": [],
        "sql": "",
        "safe_sql": True,
        "results": "",
        "results_json": [],
        "visualization": {},
        "insight": "",
        "recommendations": "",
        "steps": []
    })

    print(result)
