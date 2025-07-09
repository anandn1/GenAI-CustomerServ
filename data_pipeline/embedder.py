# Gemini Embedding + Pinecone uploader


import os
from dotenv import load_dotenv
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Pinecone as PineconeLangChain
from langchain.schema import Document
import pinecone

# Load environment variables from .env
load_dotenv()

# Load API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

# Initialize embedding model
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

# Ensure the index exists
if PINECONE_INDEX not in pinecone.list_indexes():
    pinecone.create_index(PINECONE_INDEX, dimension=768, metric="cosine")

# Connect to the index
index = pinecone.Index(PINECONE_INDEX)

def embed_and_upload(docs: List[Document]):
    """
    Embeds the documents and uploads them to Pinecone.
    Each document is a chunk with metadata.
    """
    print(f"Embedding {len(docs)} chunks...")

    # Upload using LangChain's Pinecone wrapper
    vectorstore = PineconeLangChain.from_documents(
        documents=docs,
        embedding=embedding_model,
        index_name=PINECONE_INDEX
    )

    print(f"Uploaded {len(docs)} chunks to Pinecone index '{PINECONE_INDEX}' ✅")

if __name__ == "__main__":
    # Optional test
    from chunker import chunk_documents
    from langchain.schema import Document

    # Sample chunk test
    sample_doc = Document(
        page_content="Walmart accepts returns within 30 days of purchase.",
        metadata={"source": "manual_test"}
    )

    chunks = chunk_documents([sample_doc])
    embed_and_upload(chunks)
