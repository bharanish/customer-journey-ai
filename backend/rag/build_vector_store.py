from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
import os
from pathlib import Path

import sys
sys.path.append('/Users/bharanishkumar/GenerativeAI/customer-journey-ai/backend')
from config import OPENAI_API_KEY

glossary_path = str(Path(__file__).resolve().parents[2] / 'data' / 'business_glossary.txt')
with open(
    glossary_path,
    "r"
) as f:

    text = f.read()

splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

docs = splitter.create_documents([text])

embeddings = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY
)

db = FAISS.from_documents(
    docs,
    embeddings
)

db.save_local(
    "vector_store/business_glossary"
)

print("Vector store created")
