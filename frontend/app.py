import streamlit as st
import requests
import plotly.express as px
import pandas as pd

st.title("Customer Journey AI Analyst")

# Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
question = st.chat_input("Ask a business question...")

if question:

    # Show user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # API call
    response = requests.post(
        "http://localhost:8000/chat",
        json={"question": question}
    )

    data = response.json()

    # Build assistant response
    assistant_text = f"""
### Insight

{data['insight']}

### Recommendations

{data['recommendations']}
"""

    # Display assistant response
    with st.chat_message("assistant"):

        st.markdown(assistant_text)

        st.subheader("Generated SQL")
        st.code(data["sql"])

        results = data.get("results", [])

        if results:

            df = pd.DataFrame(results)

            st.subheader("Results")
            st.dataframe(df)

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

    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_text
        }
    )
