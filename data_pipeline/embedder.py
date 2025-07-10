import os
from dotenv import load_dotenv
from typing import List
from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from uuid import uuid4
from langchain.schema import Document

# Load env vars
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

# Initialize Pinecone (classic v2 style)
pc = Pinecone(api_key=PINECONE_API_KEY)

if not pc.has_index(PINECONE_INDEX):
    pc.create_index(
        name=PINECONE_INDEX,
        dimension=768,  # Changed from 1536 to 768 to match Gemini embedding output
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(PINECONE_INDEX)

def embed_and_upload(docs: List[Document], batch_size=600):
    """
    Embeds the documents and uploads them to Pinecone in batches.
    Each document is a chunk with metadata.
    """
    print(f"Embedding and uploading {len(docs)} chunks...")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = PineconeVectorStore(index=index, embedding=embeddings)
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i+batch_size]
            uuids = [str(uuid4()) for _ in range(len(batch))]
            vector_store.add_documents(documents=batch, ids=uuids)
            print(f"Uploaded batch {i//batch_size+1} of {((len(docs)-1)//batch_size)+1}")
        print(f"Uploaded {len(docs)} chunks to Pinecone index '{PINECONE_INDEX}' ✅")
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