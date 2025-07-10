#Load Text, CSV, PDF

import os
import pandas as pd
import pdfplumber
from langchain_core.documents import Document

def load_txt(path):
    # Load text from a .txt file into a Document object
    base = os.path.basename(path)
    filename_without_ext = os.path.splitext(base)[0]
    metadata = {
        "source": filename_without_ext,
        "filename": base,
        "file_path": path
    }
    try:
        with open(path, 'r', encoding='utf-8') as file:
            text = file.read()
    except Exception as e:
        print(f"Error loading TXT file {path}: {e}")
        text = ""
    return [Document(page_content=text, metadata=metadata)]

def load_pdf(path):
    # Extract text from each page of a PDF into separate Document objects.
    base = os.path.basename(path)
    filename_without_ext = os.path.splitext(base)[0]
    common_metadata = {
        "source": filename_without_ext,
        "filename": base,
        "file_path": path
    }
    documents = []
    try:
        with pdfplumber.open(path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                metadata = {**common_metadata, "page": page_num}
                documents.append(Document(page_content=text, metadata=metadata))
    except Exception as e:
        print(f"Error loading PDF file {path}: {e}")
    return documents

def load_csv(path):
    # Read a CSV file and convert its contents into multiple Document objects, each under the Pinecone size limit.
    base = os.path.basename(path)
    filename_without_ext = os.path.splitext(base)[0]
    metadata = {
        "source": filename_without_ext,
        "filename": base,
        "file_path": path
    }
    documents = []
    try:
        df = pd.read_csv(path)
        csv_str = df.to_csv(index=False)
        # Pinecone limit is 4,194,304 bytes (4MB). Use 2MB as a safer chunk size.
        max_bytes = 2 * 1024 * 1024
        start = 0
        while start < len(csv_str):
            chunk = csv_str[start:start+max_bytes]
            documents.append(Document(page_content=chunk, metadata=metadata))
            start += max_bytes
    except Exception as e:
        print(f"Error loading CSV file {path}: {e}")
        documents = [Document(page_content="", metadata=metadata)]
    return documents

# In embedder.py, update embed_and_upload to upload in batches
# Example (add this logic in embedder.py):
# def embed_and_upload(docs: List[Document], batch_size=100):
#     for i in range(0, len(docs), batch_size):
#         batch = docs[i:i+batch_size]
#         PineconeLangChain.from_documents(
#             documents=batch,
#             embedding=embedding_model,
#             index_name=PINECONE_INDEX
#         )
#         print(f"Uploaded batch {i//batch_size+1} of {((len(docs)-1)//batch_size)+1}")