import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from io import BytesIO

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(data):

    pdf_path = "report.pdf"

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    content = [

        Paragraph(
            "Customer Journey AI Report",
            styles["Title"]
        ),

        Spacer(1, 12),

        Paragraph(
            f"<b>Question:</b> {data['question']}",
            styles["BodyText"]
        ),

        Spacer(1, 12),

        Paragraph(
            f"<b>Insight:</b><br/>{data['insight']}",
            styles["BodyText"]
        ),

        Spacer(1, 12),

        Paragraph(
            f"<b>Recommendations:</b><br/>{data['recommendations']}",
            styles["BodyText"]
        )
    ]

    doc.build(content)

    return pdf_path

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
                
                col1, col2, col3 = st.columns(3)

                # CSV Download
                with col1:
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📄 CSV",
                        csv,
                        file_name="analysis_results.csv",
                        mime="text/csv"
                    )

                # Excel Download

                with col2:

                    excel_buffer = BytesIO()
                
                    with pd.ExcelWriter(
                        excel_buffer,
                        engine="openpyxl"
                    ) as writer:

                        df.to_excel(
                            writer,
                            index=False,
                            sheet_name="Results"
                        )

                    st.download_button(
                        "📊 Excel",
                        excel_buffer.getvalue(),
                        file_name="analysis_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                with col3:

                    pdf_file = generate_pdf(data)

                    with open(pdf_file, "rb") as f:

                        st.download_button(
                            "📑 PDF Report",
                            data=f,
                            file_name="business_report.pdf",
                            mime="application/pdf"
                        )

                # Chart

                if len(df.columns) >= 2:

                    try:
                        viz = data.get("visualization")

                        if viz and results:

                            chart_type = viz.get("chart_type")
                            x_col = viz.get("x")
                            y_col = viz.get("y")

                            try:

                                if chart_type == "line":

                                    fig = px.line(
                                        df,
                                        x=x_col,
                                        y=y_col
                                    )

                                elif chart_type == "pie":

                                    fig = px.pie(
                                        df,
                                        names=x_col,
                                        values=y_col
                                    )

                                elif chart_type == "scatter":

                                    fig = px.scatter(
                                        df,
                                        x=x_col,
                                        y=y_col
                                    )
                                
                                else:

                                    fig = px.bar(
                                        df,
                                        x=x_col,
                                        y=y_col
                                    )

                                st.plotly_chart(
                                    fig,
                                    use_container_width=True
                                )

                            except Exception as e:

                                st.warning(
                                    f"Could not generate chart: {e}"
                                )

                    except Exception:
                        pass
