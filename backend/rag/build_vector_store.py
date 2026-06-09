from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

import sys
sys.path.append(
    "/Users/bharanishkumar/GenerativeAI/customer-journey-ai/backend"
)

from config import OPENAI_API_KEY


# -----------------------------
# Load all knowledge files
# -----------------------------

data_dir = Path(__file__).resolve().parents[2] / "data"

documents = []

for file in data_dir.glob("*.txt"):

    with open(file, "r", encoding="utf-8") as f:

        text = f.read()

        documents.append(
            {
                "content": text,
                "source": file.name
            }
        )


# -----------------------------
# Chunking
# -----------------------------

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

docs = []

for doc in documents:

    chunks = splitter.create_documents(
        [doc["content"]],
        metadatas=[
            {
                "source": doc["source"]
            }
        ]
    )

    docs.extend(chunks)


print(f"Total chunks: {len(docs)}")


# -----------------------------
# Embeddings
# -----------------------------

embeddings = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY
)

# -----------------------------
# Build Vector Store
# -----------------------------

db = FAISS.from_documents(
    docs,
    embeddings
)

db.save_local(
    "vector_store/customer_knowledge_base"
)

print("Knowledge base created successfully")
