from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List


def chunk_documents(docs: List[Document], chunk_size=300, chunk_overlap=50) -> List[Document]:
    """
    Takes a list of LangChain Document objects and returns a list of chunked Documents
    with clean, minimal metadata to prevent API size limit errors.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "],
        length_function=len
    )

    all_chunks = []
    for doc in docs:
        # This first split creates chunks but they inherit the parent's (potentially huge) metadata
        chunks_with_old_metadata = text_splitter.split_documents([doc])

        # Now, we iterate through and create new, clean Document objects
        for i, chunk in enumerate(chunks_with_old_metadata):
            # Create a brand new Document. This is the key step.
            # It ensures we don't carry over any unwanted, large metadata fields.
            new_chunk = Document(
                page_content=chunk.page_content,
                metadata={
                    "source": doc.metadata.get("source", "unknown"),
                    "chunk_id": i
                }
            )
            all_chunks.append(new_chunk)

    return all_chunks