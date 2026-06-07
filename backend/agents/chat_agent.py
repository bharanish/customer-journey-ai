from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=OPENAI_API_KEY
)

def general_chat(question):

    prompt = f"""
    You are a helpful AI assistant.

    User Question:
    {question}

    Provide a concise and helpful response.
    """

    response = llm.invoke(prompt)

    return response.content
