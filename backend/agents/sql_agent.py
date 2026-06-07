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

    Table:
    customer_journey

    Available Columns:
    - customer_id
    - event_date
    - channel
    - campaign
    - device
    - event_type
    - revenue

    Rules:
    1. Use ONLY the columns listed above.
    2. Never invent columns.
    3. If the question requires a column that does not exist,
    respond with exactly this single token:

    INVALID_COLUMN

    Do not add explanations.
    Do not add comments.
    Do not add SQL.
    Do not add markdown.

    Question:
    {question}

    Return SQL only.
    """

    response = llm.invoke(prompt)

    return response.content


def clean_sql(sql_text):

    cleaned = (
        sql_text
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )

    if "INVALID_COLUMN" in cleaned:
        return "INVALID_COLUMN"

    return cleaned

# print(
#     generate_sql(
#         "Which channel generated highest revenue?"
#     )
# )
