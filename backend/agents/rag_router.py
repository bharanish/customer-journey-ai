from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY
)

def is_business_definition(question):

    prompt = f"""
    Determine if the user is asking for:

    - business terminology
    - metric definition
    - KPI explanation

    Return ONLY:

    YES
    or
    NO

    Question:
    {question}
    """

    response = llm.invoke(prompt)

    return response.content.strip()
