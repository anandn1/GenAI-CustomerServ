import json
from typing import List
from langchain.schema import Document


def inspect_chunks(chunks: List[Document], top_n: int = 5):
    """
    Analyzes a list of document chunks and prints a report on their sizes.
    This helps diagnose 'message length too large' errors.
    """
    if not chunks:
        print("No chunks to inspect.")
        return

    chunk_sizes = []
    for i, chunk in enumerate(chunks):
        # Calculate size of page_content in bytes (using utf-8)
        content_bytes = len(chunk.page_content.encode('utf-8'))

        # Calculate size of metadata when serialized to JSON
        try:
            # Use ensure_ascii=False for accurate sizing of non-ASCII chars
            metadata_str = json.dumps(chunk.metadata, ensure_ascii=False)
            metadata_bytes = len(metadata_str.encode('utf-8'))
        except TypeError as e:
            # Handle non-serializable objects gracefully
            print(f"Warning: Could not serialize metadata for chunk {i}: {e}")
            metadata_bytes = 0

        total_bytes = content_bytes + metadata_bytes
        chunk_sizes.append({
            'index': i,
            'total_bytes': total_bytes,
            'content_bytes': content_bytes,
            'metadata_bytes': metadata_bytes,
            'source': chunk.metadata.get('source', 'unknown')
        })

    # Sort to find the largest chunks
    sorted_chunks = sorted(chunk_sizes, key=lambda x: x['total_bytes'], reverse=True)

    print("\n--- CHUNK INSPECTION REPORT ---")
    print(f"Total chunks generated: {len(chunks)}")

    print(f"\nTop {top_n} Largest Chunks Found:")
    for i in range(min(top_n, len(sorted_chunks))):
        largest = sorted_chunks[i]
        print(f"  - Rank {i + 1}:")
        print(f"    Index in List: {largest['index']}")
        print(f"    Source File:   {largest['source']}")
        print(f"    Total Size:    {largest['total_bytes']:,} bytes")
        print(f"    Content Size:  {largest['content_bytes']:,} bytes")
        print(f"    Metadata Size: {largest['metadata_bytes']:,} bytes")

    # Check if the largest chunk is the problem
    if sorted_chunks:
        largest_chunk_info = sorted_chunks[0]
        # Pinecone's limit is ~4MB. If a single chunk is over 2MB, it's a huge problem.
        if largest_chunk_info['total_bytes'] > 2_000_000:
            print("\n\n‼️ CRITICAL WARNING ‼️")
            print("The largest chunk is over 2MB BY ITSELF.")
            print("This is the source of the API error. No batch size will fix this.")
            print("The problem is either the 'chunker.py' is not replacing the metadata correctly,")
            print("or a single row/field in your source CSV is enormous.")