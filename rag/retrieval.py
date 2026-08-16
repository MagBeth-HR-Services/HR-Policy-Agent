import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

from ingestion.vector_store import get_vector_store


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_chroma_path() -> Path:
    """Read and resolve the configured Chroma path."""
    load_dotenv(PROJECT_ROOT / ".env")

    configured_path = Path(
        os.getenv("CHROMA_PATH", "./data/chroma")
    )

    if configured_path.is_absolute():
        return configured_path

    return (PROJECT_ROOT / configured_path).resolve()


@lru_cache(maxsize=1)
def cached_vector_store(chroma_path: str):
    """Open and reuse the existing vector store."""
    return get_vector_store(chroma_path)


def search_policy_documents(
    query: str,
    k: int = 5,
    document_id: str | None = None,
    diversify: bool = False,
) -> list[dict]:
    """Retrieve structured policy evidence from Chroma."""
    query = query.strip()

    if not query:
        raise ValueError("The search query cannot be empty.")

    if not 1 <= k <= 10:
        raise ValueError("k must be between 1 and 10.")

    vector_store = cached_vector_store(
        str(resolve_chroma_path())
    )

    filter_value = None

    if document_id:
        filter_value = {"document_id": document_id}

    candidate_count = min(k * 4, 40) if diversify else k

    candidates = vector_store.similarity_search_with_relevance_scores(
        query=query,
        k=candidate_count,
        filter=filter_value,
    )

    selected = []
    document_counts = {}

    for document, score in candidates:
        candidate_document_id = document.metadata["document_id"]

        if diversify:
            current_count = document_counts.get(
                candidate_document_id,
                0,
            )

            if current_count >= 2:
                continue

            document_counts[candidate_document_id] = (
                current_count + 1
            )

        selected.append((document, score))

        if len(selected) == k:
            break

    evidence = []

    for rank, (document, score) in enumerate(
        selected,
        start=1,
    ):
        metadata = document.metadata

        evidence.append(
            {
                "rank": rank,
                "score": round(float(score), 4),
                "document_id": metadata["document_id"],
                "title": metadata["title"],
                "section": metadata["section"],
                "page_number": metadata["page_number"],
                "chunk_id": metadata["chunk_id"],
                "source_file": metadata["source_file"],
                "snippet": metadata["source_snippet"],
                "content": document.page_content,
            }
        )

    return evidence