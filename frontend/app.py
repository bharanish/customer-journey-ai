import streamlit as st
import requests
import plotly.express as px
import pandas as pd

# ---------------------------------
# Page Title
# ---------------------------------

st.set_page_config(
    page_title="Customer Journey AI Analyst",
    layout="wide"
)

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
if st.sidebar.button("Clear History"):
    st.session_state.clear()
    st.rerun()

with st.sidebar:

    st.header("Question History")

    if st.session_state.history:

        for item in reversed(st.session_state.history):

            if isinstance(item, dict):
                st.write(f"• {item['question']}")

            else:
                st.write(f"• {item}")

    else:
        st.write("No questions asked yet")

# ---------------------------------
# User Input
# ---------------------------------

question = st.chat_input(
    "Ask a business question..."
)

# ---------------------------------
# API Call
# ---------------------------------

if question:

    with st.spinner("Analyzing..."):

        try:

            response = requests.post(
                "http://localhost:8000/chat",
                json={
                    "question": question,
                    "history": st.session_state.history[-5:]
                }
            )

            if response.status_code != 200:
                st.error(response.text)
                st.stop()

            data = response.json()

            # Save history
            st.session_state.history.append({
                "question": question,
                "result": data.get("results_json", [])[:5]
            })

            # Save latest response
            st.session_state.last_result = data

        except Exception as e:

            st.error(
                f"Application Error: {str(e)}"
            )

            st.stop()

# ---------------------------------
# Display Latest Result
# ---------------------------------

if st.session_state.last_result:

    data = st.session_state.last_result

    if data.get("sql") == "INVALID_COLUMN":

        st.warning(
            "The requested field is not available in the dataset."
        )

        st.markdown("""
    ### Available Fields

    - customer_id
    - event_date
    - channel
    - campaign
    - device
    - event_type
    - revenue

    ### Try asking:

    - Show revenue by channel
    - Show revenue by campaign
    - Show revenue by device
    - Which channel generated highest revenue?
    - What is total revenue?
    """)

    else:

        # -----------------------------
        # Conversation Context
        # -----------------------------

        with st.expander("Conversation Context"):

            for idx, q in enumerate(
                st.session_state.history,
                start=1
            ):
                st.write(f"{idx}. {q}")

        # -----------------------------
        # General Chat Response
        # -----------------------------

        if data.get("type") == "general":

            st.subheader("AI Assistant")

            st.write(
                data.get(
                    "answer",
                    "No response generated."
                )
            )

        # -----------------------------
        # Analytics Response
        # -----------------------------

        else:

            # Generated SQL

            if "sql" in data:

                st.subheader("Generated SQL")

                st.code(
                    data["sql"],
                    language="sql"
                )

            # Insight

            if "insight" in data:

                st.subheader("Insights")

                st.write(
                    data["insight"]
                )

            # Recommendations

            if "recommendations" in data:

                st.subheader("Recommendations")

                st.write(
                    data["recommendations"]
                )

            # Workflow

            if "steps" in data:

                st.subheader("Agent Workflow")

                st.write(
                    " → ".join(
                        data["steps"]
                    )
                )

            # Results Table

            results = data.get(
                "results_json",
                []
            )

            if results:

                df = pd.DataFrame(results)

                st.subheader("Results")

                st.dataframe(
                    df,
                    use_container_width=True
                )

                # Chart

                if len(df.columns) >= 2:

                    try:

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

                    except Exception:
                        pass