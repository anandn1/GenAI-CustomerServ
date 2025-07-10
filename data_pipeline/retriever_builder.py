# Pinecone index setup

import os
from dotenv import load_dotenv
from langchain.vectorstores import Pinecone as PineconeLangChain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import pinecone

# Load environment variables from .env
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Validate environment variables
for var in [PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX, GOOGLE_API_KEY]:
    if not var:
        raise ValueError("One or more required environment variables are missing.")

# Initialize Pinecone
try:
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
except Exception as e:
    raise RuntimeError(f"Failed to initialize Pinecone: {e}")

# Initialize embedding model
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Connect to Pinecone index
try:
    index = pinecone.Index(PINECONE_INDEX)
except Exception as e:
    raise RuntimeError(f"Failed to connect to Pinecone index: {e}")

def build_retriever():
    """
    Returns a retriever object for querying Pinecone using LangChain.
    """
    try:
        vectorstore = PineconeLangChain(
            index=index,
            embedding=embedding_model,
            text_key="text"
        )
        retriever = vectorstore.as_retriever()
        return retriever
    except Exception as e:
        print(f"Error building retriever: {e}")
        return None

if __name__ == "__main__":
    retriever = build_retriever()
    print("Retriever is set up and ready to use.")
