import re
from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


POLICY_FILENAME_PATTERN = re.compile(r"^POL-\d{3}-.+\.(md|pdf)$")


def clean_text(text: str) -> str:
    """Remove unwanted characters and excessive blank lines."""
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_document_id(text: str, filename: str) -> str:
    """Extract a stable policy ID such as POL-001."""
    match = re.search(r"POL-\d{3}", text)

    if match:
        return match.group(0)

    filename_match = re.match(r"(POL-\d{3})", filename)

    if filename_match:
        return filename_match.group(1)

    raise ValueError(f"Document ID not found in {filename}")


def extract_markdown_title(text: str, filename: str) -> str:
    """Extract the first level-one Markdown heading."""
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)

    if not match:
        raise ValueError(f"Title not found in {filename}")

    return match.group(1).strip()


def extract_pdf_title(reader: PdfReader, first_page_text: str, filename: str) -> str:
    """Extract the PDF title from metadata or visible page text."""
    if reader.metadata and reader.metadata.title:
        return reader.metadata.title.strip()

    for line in first_page_text.splitlines():
        line = line.strip()

        if line.endswith("Policy") and not line.startswith("HORIZON"):
            return line

    raise ValueError(f"Title not found in {filename}")


def extract_section(text: str) -> str:
    """Extract the first numbered section heading from a page."""
    match = re.search(r"^\d+\.\s+(.+)$", text, re.MULTILINE)

    if match:
        return match.group(0).strip()

    return "Cover or introductory material"


def load_markdown_policy(path: Path) -> list[Document]:
    """Load one Markdown policy as a LangChain Document."""
    text = clean_text(path.read_text(encoding="utf-8"))

    metadata = {
        "document_id": extract_document_id(text, path.name),
        "title": extract_markdown_title(text, path.name),
        "section": "Complete Markdown document",
        "source_file": path.name,
        "source_path": str(path.resolve()),
        "source_format": "markdown",
        "page_number": None,
    }

    return [Document(page_content=text, metadata=metadata)]


def load_pdf_policy(path: Path) -> list[Document]:
    """Load one PDF policy as one LangChain Document per page."""
    reader = PdfReader(path)
    page_texts = [
        clean_text(page.extract_text() or "")
        for page in reader.pages
    ]

    if not page_texts or not any(page_texts):
        raise ValueError(f"No readable text found in {path.name}")

    document_id = extract_document_id(page_texts[0], path.name)
    title = extract_pdf_title(reader, page_texts[0], path.name)

    documents = []

    for page_number, text in enumerate(page_texts, start=1):
        if not text:
            continue

        metadata = {
            "document_id": document_id,
            "title": title,
            "section": extract_section(text),
            "source_file": path.name,
            "source_path": str(path.resolve()),
            "source_format": "pdf",
            "page_number": page_number,
        }

        documents.append(
            Document(page_content=text, metadata=metadata)
        )

    return documents


def load_policy_corpus(policy_directory: str | Path) -> list[Document]:
    """Load every valid policy file from the corpus directory."""
    policy_directory = Path(policy_directory)

    if not policy_directory.is_dir():
        raise FileNotFoundError(
            f"Policy directory not found: {policy_directory}"
        )

    policy_files = sorted(
        path
        for path in policy_directory.iterdir()
        if path.is_file()
        and POLICY_FILENAME_PATTERN.match(path.name)
    )

    if not policy_files:
        raise ValueError(
            f"No policy files found in {policy_directory}"
        )

    documents = []

    for path in policy_files:
        if path.suffix.lower() == ".md":
            documents.extend(load_markdown_policy(path))
        elif path.suffix.lower() == ".pdf":
            documents.extend(load_pdf_policy(path))

    return documents