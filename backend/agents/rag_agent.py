from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI

from config import OPENAI_API_KEY

embeddings = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY
)

db = FAISS.load_local(
    "vector_store/business_glossary",
    embeddings,
    allow_dangerous_deserialization=True
)

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=OPENAI_API_KEY
)

def answer_business_question(question):

    docs = db.similarity_search(
        question,
        k=3
    )

    context = "\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
    Answer using ONLY the provided context.

    Context:
    {context}

    Question:
    {question}
    """

    response = llm.invoke(prompt)

    return response.content
