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
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

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
        vectorstore = PineconeLangChain.from_existing_index(
            index_name=PINECONE_INDEX,
            embedding=embedding_model
        )

        # 4. Return the vectorstore itself so the caller can fetch documents directly
        print("✅ Pinecone vectorstore loaded successfully using modern client.")
        return vectorstore

    except Exception as e:
        print(f"❌ Failed to build Pinecone vectorstore: {e}")
        # Add a helpful tip for the most common issue.
        print("   Hint: Ensure your PINECONE_API_KEY and PINECONE_INDEX environment variables are correct.")
        return None

# --- OPENROUTER LLMCHAIN SETUP ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
YOUR_SITE_URL = os.getenv("YOUR_SITE_URL")
YOUR_SITE_NAME = os.getenv("YOUR_SITE_NAME")

openrouter_prompt_template = """Context:\n{context}\n\nQuestion: {question}\nAnswer: Let's think step by step."""
openrouter_prompt = PromptTemplate(
    template=openrouter_prompt_template,
    input_variables=["context", "question"]
)

def get_openrouter_llm():
    return ChatOpenAI(
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
        model_name="openrouter/auto",  # Replace with your preferred model
    )

def answer_question_with_rag(question, retriever, max_context_docs=4):
    """
    Retrieves relevant context using the retriever and answers the question using OpenRouter LLMChain.
    """
    # Retrieve relevant documents
    docs = retriever.invoke(question)
    if not docs:
        return "No relevant context found."
    # Concatenate context (truncate if too long)
    context = "\n\n".join(doc.page_content for doc in docs[:max_context_docs])
    llm_chain = LLMChain(prompt=openrouter_prompt, llm=get_openrouter_llm())
    return llm_chain.run({"context": context, "question": question})

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
                    score = doc.metadata.get('_score')
                    if score is not None:
                        print(f"Score: {score:.4f}")
                    print(f"Content: {doc.page_content[:200]}...")
            else:
                print("No relevant documents found for the test query (or none met the threshold).")

        except Exception as e:
            print(f"An error occurred during the test query: {e}")
        
        # --- Test the full RAG chain ---
        print("\n--- Testing RAG LLMChain ---")
        rag_answer = answer_question_with_rag("What is the return policy for electronics?", retriever)
        print(f"\nRAG Answer: {rag_answer}")
    else:
        print("\nCould not perform test query because retriever setup failed.")