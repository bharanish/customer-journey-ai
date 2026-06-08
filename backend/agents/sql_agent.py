import sys
from pathlib import Path

from langchain_openai import ChatOpenAI

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from config import OPENAI_API_KEY

# ---------------------------------
# LLM
# ---------------------------------

llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=OPENAI_API_KEY,
    temperature=0
)

# ---------------------------------
# SQL Generation
# ---------------------------------

def generate_sql(question, history):

    history_context = ""

    for item in history:

        history_context += f"""
User Question:
{item.get("question")}

Result:
{item.get("result")}
"""

    prompt = f"""
You are an expert Customer Journey Analytics SQL assistant.

Your job is to answer business questions
using PostgreSQL SQL.

=========================================
DATABASE SCHEMA
=========================================

Table Name:
customer_journey

Columns:

customer_id
- Unique customer identifier

event_date
- Date of customer interaction

channel
- Marketing acquisition channel
- Examples:
  Facebook
  Google Ads
  Email
  Organic
  Direct

campaign
- Marketing campaign name

device
- Device used by customer
- Examples:
  Mobile
  Desktop
  Tablet

event_type
- Customer action
- Examples:
  Click
  Signup
  Purchase

revenue
- Revenue generated

=========================================
BUSINESS CONTEXT
=========================================

This dataset is used for:

- Revenue analysis
- Channel performance
- Campaign performance
- Device performance
- Customer journey analytics

=========================================
CONVERSATION HISTORY
=========================================

{history_context}

=========================================
SQL RULES
=========================================

1. Use ONLY the columns listed above.
2. Never invent columns.
3. Generate PostgreSQL SQL only.
4. Return exactly ONE SQL statement.
5. Only generate SELECT queries.
6. Never generate INSERT.
7. Never generate UPDATE.
8. Never generate DELETE.
9. Never generate DROP.
10. Never generate ALTER.
11. Never generate CREATE.
12. Never generate TRUNCATE.

If the user asks for information that
cannot be answered using the available
columns, return exactly:

INVALID_COLUMN

=========================================
EXAMPLES
=========================================

Question:
Show revenue by channel

SQL:
SELECT
    channel,
    SUM(revenue) AS total_revenue
FROM customer_journey
GROUP BY channel;

Question:
What is total revenue?

SQL:
SELECT
    SUM(revenue) AS total_revenue
FROM customer_journey;

Question:
Show revenue by device

SQL:
SELECT
    device,
    SUM(revenue) AS total_revenue
FROM customer_journey
GROUP BY device;

Question:
Which channel generated highest revenue?

SQL:
SELECT
    channel,
    SUM(revenue) AS total_revenue
FROM customer_journey
GROUP BY channel
ORDER BY total_revenue DESC
LIMIT 1;

Question:
Show revenue by customer segment

Answer:
INVALID_COLUMN

=========================================
CURRENT QUESTION
=========================================

{question}

Return SQL only.

Do not explain.

Do not add markdown.

Do not add comments.
"""

    response = llm.invoke(prompt)

    return response.content


# ---------------------------------
# SQL Cleanup
# ---------------------------------

def clean_sql(sql_text):

    cleaned = (
        sql_text
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )

    if "INVALID_COLUMN" in cleaned:
        return "INVALID_COLUMN"

    if "UNSAFE_OPERATION" in cleaned:
        return "UNSAFE_OPERATION"

    return cleaned


# ---------------------------------
# Testing
# ---------------------------------

if __name__ == "__main__":

    sql = generate_sql(
        "Show revenue by channel",
        []
    )

    print(sql)

    print(
        clean_sql(sql)
    )
