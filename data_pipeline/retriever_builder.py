"""
A dedicated module for building and configuring the Pinecone vector store retriever.
This centralizes retriever logic, making it easy to manage and test.
Uses modern Pinecone-client v3.x syntax.
"""

import os
from dotenv import load_dotenv
from langchain.vectorstores import Pinecone as PineconeLangChain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone as PineconeClient # Import the main client

# --- INITIALIZATION ---
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# NOTE: The 'PINECONE_ENV' (environment) is no longer needed for initialization in v3.x
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- BUILDER FUNCTION ---

def get_configured_retriever(k_value: int = 5, score_threshold: float = 0.50):
    """
    Builds and returns a configured Pinecone retriever for the RAG chain.
    This function is the single source of truth for retriever configuration.

    Args:
        k_value (int): The number of documents to retrieve.
        score_threshold (float): The minimum similarity score for a document to be considered relevant.

    Returns:
        A configured LangChain retriever object, or None if setup fails.
    """
    # 1. Validate environment variables
    required_vars = {
        "PINECONE_API_KEY": PINECONE_API_KEY,
        "PINECONE_INDEX": PINECONE_INDEX,
        "GOOGLE_API_KEY": GOOGLE_API_KEY
    }
    for var_name, var_value in required_vars.items():
        if not var_value:
            print(f"Error: Environment variable '{var_name}' is not set.")
            return None

    try:
        # 2. Initialize the embedding model
        embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        # 3. Connect to the existing Pinecone index using the LangChain wrapper.
        # LangChain's Pinecone wrapper handles the new client initialization internally.
        # You just need to pass the index name directly.
        vectorstore = PineconeLangChain.from_existing_index(
            index_name=PINECONE_INDEX,
            embedding=embedding_model
        )

        # 4. Configure and return the retriever
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": k_value,
                "score_threshold": score_threshold
            }
        )
        print("✅ Pinecone retriever configured successfully using modern client.")
        return retriever

    except Exception as e:
        print(f"❌ Failed to build Pinecone retriever: {e}")
        # Add a helpful tip for the most common issue.
        print("   Hint: Ensure your PINECONE_API_KEY and PINECONE_INDEX environment variables are correct.")
        return None

# --- TESTING BLOCK ---
if __name__ == "__main__":
    print("--- Testing Retriever Configuration ---")

    retriever = get_configured_retriever()

    if retriever:
        print("\n--- Running a test query ---")
        test_query = "What is the return policy for electronics?"

        try:
            retrieved_docs = retriever.invoke(test_query)

            print(f"Query: '{test_query}'")
            print(f"Retrieved {len(retrieved_docs)} documents.")

            if retrieved_docs:
                for i, doc in enumerate(retrieved_docs):
                    print(f"\n--- Document {i+1} ---")
                    # The score is automatically included by LangChain when using this search type
                    score = doc.metadata.get('_score')
                    # The v3 client might not add '_score' to metadata in the same way. Check the object.
                    # A more robust way might be to get it from the tuple if the retriever returns one.
                    # For now, this is a safe way to check.
                    if score is not None:
                        print(f"Score: {score:.4f}")
                    print(f"Content: {doc.page_content[:200]}...")
            else:
                print("No relevant documents found for the test query (or none met the threshold).")

        except Exception as e:
            print(f"An error occurred during the test query: {e}")
    else:
        print("\nCould not perform test query because retriever setup failed.")