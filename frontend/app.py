import streamlit as st
import requests

st.title("Customer Journey AI Analyst")

question = st.text_input("Ask a question")

if st.button("Analyze"):

    response = requests.post(
        "http://localhost:8000/chat",
        json={"question": question}
    )

    data = response.json()

    st.subheader("Generated SQL")
    st.code(data["sql"])

    st.subheader("Insights")
    st.write(data["insight"])

    st.subheader("Recommendations")
    st.write(data["recommendations"])
