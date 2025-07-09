import os
import pandas as pd
import pdfplumber
from langchain_core.documents import Document

def load_txt(path):
    #Load text from a .txt file into a Document object
    base = os.path.basename(path)
    filename_without_ext = os.path.splitext(base)[0]
    metadata = {
        "source": filename_without_ext,
        "filename": base,
        "file_path": path
    }
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return [Document(page_content=text, metadata=metadata)]

def load_pdf(path):
    #Extract text from each page of a PDF into separate Document objects.
    base = os.path.basename(path)
    filename_without_ext = os.path.splitext(base)[0]
    common_metadata = {
        "source": filename_without_ext,
        "filename": base,
        "file_path": path
    }
    documents = []
    with pdfplumber.open(path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text is None:
                text = ""
            metadata = {**common_metadata, "page": page_num}
            documents.append(Document(page_content=text, metadata=metadata))
    return documents

def load_csv(path):
    #Read a CSV file and convert its contents into a Document object.
    base = os.path.basename(path)
    filename_without_ext = os.path.splitext(base)[0]
    metadata = {
        "source": filename_without_ext,
        "filename": base,
        "file_path": path
    }
    df = pd.read_csv(path)
    content = df.to_csv(index=False)
    return [Document(page_content=content, metadata=metadata)]