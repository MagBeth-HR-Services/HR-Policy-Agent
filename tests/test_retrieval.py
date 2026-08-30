from langchain_core.documents import Document

from rag.retrieval import cached_vector_store, search_policy_documents


class FakeVectorStore:
    """Return canned policy chunks without loading MiniLM."""

    def __init__(self, documents):
        self.documents = documents

    def similarity_search_with_relevance_scores(
        self,
        query,
        k,
        filter=None,
    ):
        selected = []

        for document, score in self.documents:
            if (
                filter
                and document.metadata["document_id"]
                != filter["document_id"]
            ):
                continue

            selected.append((document, score))

            if len(selected) == k:
                break

        return selected


def make_document(document_id, section, chunk_id):
    return Document(
        page_content=f"{document_id} {section} body",
        metadata={
            "document_id": document_id,
            "title": f"{document_id} title",
            "section": section,
            "page_number": 1 if document_id == "POL-005" else 0,
            "chunk_id": chunk_id,
            "source_file": f"{document_id}.md",
            "source_snippet": f"{section} snippet",
        },
    )


def test_search_returns_top_k_and_citation_fields(monkeypatch):
    cached_vector_store.cache_clear()

    store = FakeVectorStore(
        [
            (make_document("POL-004", "4. Requirements", "POL-004-C0001"), 0.9),
            (make_document("POL-003", "3. Core", "POL-003-C0001"), 0.8),
            (make_document("POL-005", "2. Rules", "POL-005-C0001"), 0.7),
        ]
    )

    monkeypatch.setattr(
        "rag.retrieval.cached_vector_store",
        lambda chroma_path: store,
    )

    results = search_policy_documents(
        "international temporary work",
        k=2,
    )

    assert len(results) == 2
    assert results[0]["document_id"] == "POL-004"
    assert results[0]["snippet"] == "4. Requirements snippet"
    assert results[0]["rank"] == 1
    assert "score" in results[0]


def test_search_can_filter_by_document_id(monkeypatch):
    cached_vector_store.cache_clear()

    store = FakeVectorStore(
        [
            (make_document("POL-004", "4. Requirements", "POL-004-C0001"), 0.9),
            (make_document("POL-003", "3. Core", "POL-003-C0001"), 0.8),
        ]
    )

    monkeypatch.setattr(
        "rag.retrieval.cached_vector_store",
        lambda chroma_path: store,
    )

    results = search_policy_documents(
        "temporary work",
        k=5,
        document_id="POL-003",
    )

    assert len(results) == 1
    assert results[0]["document_id"] == "POL-003"


def test_search_diversifies_across_documents(monkeypatch):
    cached_vector_store.cache_clear()

    store = FakeVectorStore(
        [
            (make_document("POL-004", "Section A", "POL-004-C0001"), 0.99),
            (make_document("POL-004", "Section B", "POL-004-C0002"), 0.98),
            (make_document("POL-004", "Section C", "POL-004-C0003"), 0.97),
            (make_document("POL-003", "Remote", "POL-003-C0001"), 0.80),
        ]
    )

    monkeypatch.setattr(
        "rag.retrieval.cached_vector_store",
        lambda chroma_path: store,
    )

    results = search_policy_documents(
        "work location",
        k=3,
        diversify=True,
    )

    document_ids = [
        result["document_id"]
        for result in results
    ]

    assert document_ids.count("POL-004") == 2
    assert "POL-003" in document_ids
