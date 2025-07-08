import os
from loaders import load_txt, load_pdf, load_csv  

def test_loaders():
    # Define paths relative to the script location
    base_path = "data"
    txt_path = os.path.join(base_path, "sample.txt")
    pdf_path = "walmart-genai-support/text_extractor/data/sample.pdf"
    csv_path = os.path.join(base_path, "sample.csv")

    # Test TXT loader
    print("\n=== Testing TXT Loader ===")
    try:
        txt_docs = load_txt(txt_path)
        for doc in txt_docs:
            print("Content:", doc.page_content)
            print("Metadata:", doc.metadata)
    except Exception as e:
        print(f"Error loading TXT: {e}")

    # Test PDF loader
    print("\n=== Testing PDF Loader ===")
    try:
        pdf_docs = load_pdf(pdf_path)
        for doc in pdf_docs:
            print(f"Page {doc.metadata['page']}:", doc.page_content.strip())
            print("Metadata:", doc.metadata)
    except Exception as e:
        print(f"Error loading PDF: {e}")

    # Test CSV loader
    print("\n=== Testing CSV Loader ===")
    try:
        csv_docs = load_csv(csv_path)
        for doc in csv_docs:
            print("Content:", doc.page_content)
            print("Metadata:", doc.metadata)
    except Exception as e:
        print(f"Error loading CSV: {e}")

test_loaders()