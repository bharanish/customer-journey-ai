from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI

from config import OPENAI_API_KEY


embeddings = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY
)

db = FAISS.load_local(
    "vector_store/customer_knowledge_base",
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

    sources = list(
        set(
            doc.metadata.get("source", "Unknown")
            for doc in docs
        )
    )

    prompt = f"""
    You are a business analytics assistant.

    Answer the question using only the provided context.

    If the answer is not present in the context,
    say:

    "I could not find that information in the knowledge base."

    Context:
    {context}

    Question:
    {question}
    """

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "sources": sources
    }
