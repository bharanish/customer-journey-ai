from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=OPENAI_API_KEY,
    temperature=0
)

def validate_question(question):

    prompt = f"""
You are a business analytics validator.

Dataset columns:

customer_id
event_date
channel
campaign
device
event_type
revenue

Determine whether the question is:

VALID
AMBIGUOUS
UNSUPPORTED

Examples:

Question:
Show revenue by channel

Answer:
VALID

Question:
Show performance

Answer:
AMBIGUOUS

Question:
Show employee salary

Answer:
UNSUPPORTED

Question:
How many employees work here?

Answer:
UNSUPPORTED

Question:
Show campaign performance

Answer:
VALID

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content.strip().upper()
