from pathlib import Path

from ingestion.loaders import load_policy_corpus


PROJECT_ROOT = Path(__file__).resolve().parents[1]
POLICY_DIRECTORY = PROJECT_ROOT / "policies"


def test_loads_all_policy_ids_and_formats():
    documents = load_policy_corpus(POLICY_DIRECTORY)

    document_ids = {
        document.metadata["document_id"]
        for document in documents
    }

    expected_ids = {
        f"POL-{number:03d}"
        for number in range(1, 12)
    }

    source_formats = {
        document.metadata["source_format"]
        for document in documents
    }

    assert document_ids == expected_ids
    assert source_formats == {"markdown", "pdf"}


def test_every_document_has_citation_metadata():
    documents = load_policy_corpus(POLICY_DIRECTORY)

    required_fields = {
        "document_id",
        "title",
        "section",
        "source_file",
        "source_path",
        "source_format",
        "page_number",
    }

    for document in documents:
        assert required_fields.issubset(document.metadata)
        assert document.metadata["document_id"]
        assert document.metadata["title"]
        assert document.metadata["section"]
        assert document.metadata["source_file"]
        assert document.page_content.strip()


def test_pdf_pages_have_page_numbers():
    documents = load_policy_corpus(POLICY_DIRECTORY)

    pdf_documents = [
        document
        for document in documents
        if document.metadata["source_format"] == "pdf"
    ]

    assert pdf_documents

    for document in pdf_documents:
        assert isinstance(document.metadata["page_number"], int)
        assert document.metadata["page_number"] >= 1