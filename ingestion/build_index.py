import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from ingestion.chunking import chunk_documents
from ingestion.loaders import load_policy_corpus
from ingestion.vector_store import create_vector_store


PROJECT_ROOT = Path(__file__).resolve().parents[1]
POLICY_DIRECTORY = PROJECT_ROOT / "policies"


def resolve_project_path(path_value: str) -> Path:
    """Resolve configuration paths from the project root."""
    path = Path(path_value)

    if path.is_absolute():
        return path

    return (PROJECT_ROOT / path).resolve()


def build_index(recreate: bool = False) -> int:
    """Load, chunk, embed, and index the policy corpus."""
    load_dotenv(PROJECT_ROOT / ".env")

    chroma_path = resolve_project_path(
        os.getenv("CHROMA_PATH", "./data/chroma")
    )

    documents = load_policy_corpus(POLICY_DIRECTORY)
    chunks = chunk_documents(documents)

    vector_store = create_vector_store(
        chunks=chunks,
        persist_directory=chroma_path,
        recreate=recreate,
    )

    indexed_ids = vector_store.get(include=[])["ids"]
    indexed_count = len(indexed_ids)

    print(f"Loaded documents: {len(documents)}")
    print(f"Created chunks: {len(chunks)}")
    print(f"Indexed chunks: {indexed_count}")
    print(f"Chroma path: {chroma_path}")

    return indexed_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the Horizon policy vector index."
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Delete and rebuild the existing collection.",
    )
    args = parser.parse_args()

    build_index(recreate=args.recreate)


if __name__ == "__main__":
    main()