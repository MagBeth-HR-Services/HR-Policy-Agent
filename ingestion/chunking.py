from collections import defaultdict

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("##", "section"),
        ("###", "subsection"),
    ],
    strip_headers=False,
)


def normalize_snippet(text: str, maximum_length: int = 240) -> str:
    """Create a compact source snippet for citations."""
    compact_text = " ".join(text.split())

    if len(compact_text) <= maximum_length:
        return compact_text

    return compact_text[: maximum_length - 3].rstrip() + "..."


def split_markdown_document(document: Document) -> list[Document]:
    """Split Markdown by headings before applying size limits."""
    heading_documents = markdown_splitter.split_text(
        document.page_content
    )

    prepared_documents = []

    for heading_document in heading_documents:
        metadata = dict(document.metadata)
        metadata.update(heading_document.metadata)

        if "section" not in heading_document.metadata:
            metadata["section"] = document.metadata["section"]

        prepared_documents.append(
            Document(
                page_content=heading_document.page_content,
                metadata=metadata,
            )
        )

    return recursive_splitter.split_documents(prepared_documents)


def split_pdf_document(document: Document) -> list[Document]:
    """Split one PDF page while preserving its page metadata."""
    return recursive_splitter.split_documents([document])


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Create deterministic, citation-ready chunks."""
    raw_chunks = []

    for document in documents:
        source_format = document.metadata["source_format"]

        if source_format == "markdown":
            raw_chunks.extend(split_markdown_document(document))
        elif source_format == "pdf":
            raw_chunks.extend(split_pdf_document(document))
        else:
            raise ValueError(
                f"Unsupported source format: {source_format}"
            )

    counters = defaultdict(int)
    final_chunks = []

    for chunk in raw_chunks:
        document_id = chunk.metadata["document_id"]
        counters[document_id] += 1
        chunk_number = counters[document_id]

        metadata = dict(chunk.metadata)
        metadata["page_number"] = metadata["page_number"] or 0
        metadata["chunk_index"] = chunk_number
        metadata["chunk_id"] = (
            f"{document_id}-C{chunk_number:04d}"
        )
        metadata["source_snippet"] = normalize_snippet(
            chunk.page_content
        )

        final_chunks.append(
            Document(
                page_content=chunk.page_content,
                metadata=metadata,
            )
        )

    return final_chunks