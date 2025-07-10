import logging
import os
import glob
from datetime import datetime

# --- Logger Setup ---
# (This can stay exactly as you had it)
logger = logging.getLogger("ingest_logger")
logger.setLevel(logging.INFO)
# Make sure the log file path is correct
log_path = os.path.join(os.path.dirname(__file__), "log.txt")
file_handler = logging.FileHandler(log_path, mode='w', encoding="utf-8")  # 'w' to overwrite log each run
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


def ingest_data(file_path: str):
    """
    Orchestrates the loading, chunking, and dynamic uploading of a single file.
    """
    # These imports are local to the function as per your original design
    from loaders import load_txt, load_pdf, load_csv
    from chunker import chunk_documents
    from embedder import embed_and_upload

    # --- File Loading ---
    file_name = os.path.basename(file_path)
    logger.info(f"--- Starting ingestion for: {file_name} ---")
    ext = os.path.splitext(file_path)[1].lower()

    docs = []
    if ext == ".txt":
        docs = load_txt(file_path)
    elif ext == ".pdf":
        docs = load_pdf(file_path)
    elif ext == ".csv":
        # Pass the filename to be used as the source in metadata
        docs = load_csv(file_path)
    else:
        logger.warning(f"Unsupported file type '{ext}' for {file_name}. Skipping.")
        return

    if not docs:
        logger.warning(f"No documents were loaded from {file_name}. Skipping.")
        return

    # --- Chunking & Embedding ---
    logger.info(f"Loaded {len(docs)} document(s) from {file_name}")
    chunks = chunk_documents(docs)
    logger.info(f"Chunked into {len(chunks)} chunk(s).")

    # Call the new dynamic embedder
    embed_and_upload(chunks)

    logger.info(f"--- Ingestion complete for: {file_name} ---\n")


if __name__ == "__main__":
    # --- Main Execution Block ---
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    print(f"Starting data ingestion from directory: {data_dir}")

    # Get a list of all files to process
    all_files = glob.glob(os.path.join(data_dir, "*"))

    if not all_files:
        print("No files found in the data directory. Exiting.")
    else:
        for file_path in all_files:
            try:
                ingest_data(file_path)
            except Exception as e:
                import traceback

                logger.error(f"A fatal error occurred processing {os.path.basename(file_path)}")
                logger.error(traceback.format_exc())
        print("All files processed.")