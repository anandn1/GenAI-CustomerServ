import logging
import os
from datetime import datetime

# Set up logger to write to log.txt
logger = logging.getLogger("ingest_logger")
logger.setLevel(logging.INFO)
log_path = os.path.join(os.path.dirname(__file__), "log.txt")
file_handler = logging.FileHandler(log_path, encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def ingest_data(file_path: str):
    """
    Loads, chunks, embeds, and uploads data from a file to Pinecone.
    Supports TXT, PDF, and CSV files.
    """
    from loaders import load_txt, load_pdf, load_csv
    from chunker import chunk_documents
    from embedder import embed_and_upload
    import os

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        docs = load_txt(file_path)
    elif ext == ".pdf":
        docs = load_pdf(file_path)
    elif ext == ".csv":
        docs = load_csv(file_path)
    else:
        logger.error(f"Unsupported file type: {ext} for {file_path}")
        raise ValueError(f"Unsupported file type: {ext}")

    logger.info(f"Loaded {len(docs)} document(s) from {file_path}")
    chunks = chunk_documents(docs)
    logger.info(f"Chunked into {len(chunks)} chunk(s) from {file_path}")
    embed_and_upload(chunks)
    logger.info(f"Ingestion complete for {file_path}")

if __name__ == "__main__":
    import glob
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    for file_path in glob.glob(os.path.join(data_dir, "*")):
        try:
            ingest_data(file_path)
        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {e}")