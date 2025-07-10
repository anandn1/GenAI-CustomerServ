# embedder.py (Final Dynamic Batching Version)

import os
from dotenv import load_dotenv
from typing import List
import time

from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import PineconeApiException
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.schema import Document

# --- Boilerplate Setup (No changes) ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
pc = Pinecone(api_key=PINECONE_API_KEY)

if PINECONE_INDEX not in pc.list_indexes().names():
    print(f"Index '{PINECONE_INDEX}' not found. Creating a new one...")
    pc.create_index(
        name=PINECONE_INDEX,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )
    print(f"Index '{PINECONE_INDEX}' created successfully.")
else:
    print(f"Index '{PINECONE_INDEX}' already exists.")


# --- NEW, DYNAMIC BATCHING UPLOADER ---
def embed_and_upload(docs: List[Document], initial_batch_size: int = 64):
    """
    Embeds and uploads documents, dynamically reducing batch size on API errors.
    """
    if not docs:
        print("No documents to upload.")
        return

    print(f"Starting dynamic batching for {len(docs)} chunks, initial batch size: {initial_batch_size}...")

    try:
        embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vectorstore = PineconeVectorStore(
            index_name=PINECONE_INDEX,
            embedding=embedding_model
        )

        # Process the documents in a loop
        i = 0
        while i < len(docs):
            current_batch_size = initial_batch_size

            # This inner loop will retry with smaller batches if necessary
            while True:
                i_end = i + current_batch_size
                batch = docs[i:i_end]

                if not batch:
                    break  # Exit if there are no more documents in the batch

                try:
                    # Attempt to add the current batch
                    vectorstore.add_documents(batch)

                    # If successful, log progress and break the retry loop
                    print(f"  ✅ Uploaded batch of {len(batch)} (total progress: {i_end}/{len(docs)})")
                    i = i_end  # Move the main index forward
                    break  # Exit the retry loop and proceed to the next batch

                except PineconeApiException as e:
                    # Check if it's the specific "message length too large" error
                    if e.status == 400 and "message length too large" in str(e.body):

                        # If the batch size is already 1, we can't reduce it further.
                        # This means a single document is the problem.
                        if current_batch_size == 1:
                            problematic_doc = batch[0]
                            print(f"‼️ CRITICAL: Skipping a single document that is too large to upload.")
                            print(
                                f"   Source: {problematic_doc.metadata.get('source')}, Chunk ID: {problematic_doc.metadata.get('chunk_id')}")
                            i = i_end  # Skip this doc and move on
                            break  # Exit retry loop

                        # Reduce the batch size and retry
                        new_batch_size = max(1, current_batch_size // 2)
                        print(
                            f"  ⚠️ API size limit hit. Reducing batch size from {current_batch_size} to {new_batch_size} and retrying...")
                        current_batch_size = new_batch_size
                        # The outer loop index `i` does not change, so we retry the same chunk of data
                    else:
                        # If it's a different API error, re-raise it
                        raise e

                except Exception as e:
                    # Handle other potential exceptions during the add_documents call
                    print(f"An unexpected error occurred: {e}")
                    raise e

        print("\n✅✅ Dynamic upload complete.")

    except Exception as e:
        import traceback
        print("❌ A fatal error occurred during the upload process:")
        print(traceback.format_exc())