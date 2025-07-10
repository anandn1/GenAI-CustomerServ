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
    # Read a CSV file and convert its contents into a Document object.
    base = os.path.basename(path)
    filename_without_ext = os.path.splitext(base)[0]
    metadata = {
        "source": filename_without_ext,
        "filename": base,
        "file_path": path
    }
    try:
        df = pd.read_csv(path)
        content = df.to_csv(index=False)
    except Exception as e:
        print(f"Error loading CSV file {path}: {e}")
        content = ""
    return [Document(page_content=content, metadata=metadata)]