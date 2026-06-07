from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=OPENAI_API_KEY
)

def generate_insight(question, results):

    prompt = f"""
    You are a senior business analyst.

    User Question:
    {question}

    Query Results:
    {results}

    Generate:
    1. Key insight
    2. Business interpretation

    Keep response concise.
    """

    response = llm.invoke(prompt)

    return response.content
