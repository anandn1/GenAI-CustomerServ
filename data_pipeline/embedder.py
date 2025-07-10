import os
from dotenv import load_dotenv
from typing import List
import pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Pinecone as PineconeLangChain
from langchain.schema import Document

# Load env vars
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

# Initialize Pinecone (classic v2 style)
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

# Check if index exists
if PINECONE_INDEX not in pinecone.list_indexes():
    pinecone.create_index(name=PINECONE_INDEX, dimension=768, metric="cosine")

def embed_and_upload(docs: List[Document]):
    print(f"Embedding and uploading {len(docs)} chunks...")
    try:
        embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        vectorstore = PineconeLangChain.from_documents(
            documents=docs,
            embedding=embedding_model,
            index_name=PINECONE_INDEX
        )

        print("✅ Upload complete to Pinecone.")
    except Exception as e:
        import traceback
        print("❌ Upload failed:")
        print(traceback.format_exc())

# Optional test
if __name__ == "__main__":
    from chunker import chunk_documents
    from langchain.schema import Document

    doc = Document(page_content="Walmart return window is 30 days.", metadata={"source": "manual_test"})
    chunks = chunk_documents([doc])
    embed_and_upload(chunks)