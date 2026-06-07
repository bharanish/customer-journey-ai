import streamlit as st
import requests
import plotly.express as px
import pandas as pd

# ---------------------------------
# Page Title
# ---------------------------------

st.title("Customer Journey AI Analyst")

# ---------------------------------
# Session State
# ---------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ---------------------------------
# Sidebar
# ---------------------------------

with st.sidebar:

    st.header("Question History")

    if st.session_state.history:

        for q in reversed(st.session_state.history):
            st.write(f"• {q}")

    else:
        st.write("No questions asked yet")

# ---------------------------------
# User Input
# ---------------------------------

question = st.chat_input("Ask a business question...")

# ---------------------------------
# API Call
# ---------------------------------

if question:

    response = requests.post(
        "http://localhost:8000/chat",
        json={
            "question": question,
            "history": st.session_state.history
        }
    )

    data = response.json()

    # Save history
    st.session_state.history.append(question)

    # Save latest result
    st.session_state.last_result = data

# ---------------------------------
# Display Latest Result
# ---------------------------------

if st.session_state.last_result:

    data = st.session_state.last_result
    
    with st.expander("Conversation Context"):
        for idx, q in enumerate(st.session_state.history,start=1):
            st.write(f"{idx}. {q}")

    st.subheader("Generated SQL")
    st.code(data["sql"])

    st.subheader("Insights")
    st.write(data["insight"])

    st.subheader("Recommendations")
    st.write(data["recommendations"])

    st.subheader("Agent Workflow")
    st.write(" → ".join(data["steps"]))

    results = data.get("results", [])

    if results:

        df = pd.DataFrame(results)

        st.subheader("Results")
        st.dataframe(df, use_container_width=True)

        if len(df.columns) >= 2:

            fig = px.bar(
                df,
                x=df.columns[0],
                y=df.columns[1],
                title=f"{df.columns[1]} by {df.columns[0]}"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
