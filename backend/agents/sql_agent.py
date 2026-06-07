import sys
from pathlib import Path
from langchain_openai import ChatOpenAI

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import OPENAI_API_KEY

llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=OPENAI_API_KEY
)

def generate_sql(question):

    prompt = f"""
    You are a PostgreSQL expert.

    Generate SQL that returns the data needed
    to answer the question completely.

    Always include calculated metrics.

    Table:
    customer_journey

    Columns:
    customer_id
    event_date
    channel
    campaign
    device
    event_type
    revenue

    Question:
    {question}

    Return SQL only.
    """

    response = llm.invoke(prompt)

    return response.content


def clean_sql(sql_text):
    return (
        sql_text
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )

# print(
#     generate_sql(
#         "Which channel generated highest revenue?"
#     )
# )
