# LangChain chunking logic


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List

def chunk_documents(docs: List[Document], chunk_size=300, chunk_overlap=50) -> List[Document]:
    """
    Takes a list of LangChain Document objects and returns a list of chunked Documents.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )

    all_chunks = []
    for doc in docs:
        chunks = splitter.split_documents([doc])
        # Add source metadata to each chunk
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["source"] = doc.metadata.get("source", "unknown")
        all_chunks.extend(chunks)

    return all_chunks

