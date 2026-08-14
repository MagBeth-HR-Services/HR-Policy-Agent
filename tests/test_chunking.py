from pathlib import Path

from ingestion.chunking import (
    CHUNK_SIZE,
    chunk_documents,
)
from ingestion.loaders import load_policy_corpus


PROJECT_ROOT = Path(__file__).resolve().parents[1]
POLICY_DIRECTORY = PROJECT_ROOT / "policies"


def get_chunks():
    documents = load_policy_corpus(POLICY_DIRECTORY)
    return chunk_documents(documents)


def test_chunks_are_created_for_all_policies():
    chunks = get_chunks()

    document_ids = {
        chunk.metadata["document_id"]
        for chunk in chunks
    }

    expected_ids = {
        f"POL-{number:03d}"
        for number in range(1, 12)
    }

    assert chunks
    assert document_ids == expected_ids


def test_chunks_have_valid_size_and_metadata():
    chunks = get_chunks()
    chunk_ids = []

    for chunk in chunks:
        assert chunk.page_content.strip()
        assert len(chunk.page_content) <= CHUNK_SIZE

        assert chunk.metadata["chunk_id"]
        assert chunk.metadata["chunk_index"] >= 1
        assert chunk.metadata["document_id"]
        assert chunk.metadata["title"]
        assert chunk.metadata["section"]
        assert chunk.metadata["source_file"]
        assert chunk.metadata["source_format"]
        assert chunk.metadata["page_number"] >= 0
        assert chunk.metadata["source_snippet"]
        assert len(chunk.metadata["source_snippet"]) <= 240

        chunk_ids.append(chunk.metadata["chunk_id"])

    assert len(chunk_ids) == len(set(chunk_ids))


def test_chunking_is_deterministic():
    first_run = get_chunks()
    second_run = get_chunks()

    first_results = [
        (
            chunk.metadata["chunk_id"],
            chunk.page_content,
        )
        for chunk in first_run
    ]

    second_results = [
        (
            chunk.metadata["chunk_id"],
            chunk.page_content,
        )
        for chunk in second_run
    ]

    assert first_results == second_results