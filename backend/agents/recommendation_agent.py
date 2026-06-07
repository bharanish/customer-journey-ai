from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=OPENAI_API_KEY
)

def generate_recommendation(insight):

    prompt = f"""
    You are a marketing strategist.

    Insight:
    {insight}

    Return ONLY:

    1. Three concise recommendations
    2. One expected impact

    Maximum 100 words.
    """

    response = llm.invoke(prompt)

    return response.content
