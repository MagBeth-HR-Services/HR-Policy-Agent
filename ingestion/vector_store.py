from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings


EMBEDDING_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)
COLLECTION_NAME = "horizon_policies"


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Create the local embedding model."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def get_chroma_client(
    persist_directory: str | Path,
) -> chromadb.PersistentClient:
    """Create a persistent local Chroma client."""
    persist_directory = Path(persist_directory)
    persist_directory.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(
        path=str(persist_directory)
    )


def create_vector_store(
    chunks: list[Document],
    persist_directory: str | Path,
    recreate: bool = False,
) -> Chroma:
    """Create or rebuild the persistent policy collection."""
    if not chunks:
        raise ValueError("Cannot index an empty chunk list.")

    client = get_chroma_client(persist_directory)

    existing_names = {
        collection.name
        for collection in client.list_collections()
    }

    if recreate and COLLECTION_NAME in existing_names:
        client.delete_collection(COLLECTION_NAME)

    vector_store = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
    )

    existing_ids = set(
        vector_store.get(include=[])["ids"]
    )

    new_chunks = [
        chunk
        for chunk in chunks
        if chunk.metadata["chunk_id"] not in existing_ids
    ]

    if new_chunks:
        vector_store.add_documents(
            documents=new_chunks,
            ids=[
                chunk.metadata["chunk_id"]
                for chunk in new_chunks
            ],
        )

    return vector_store


def get_vector_store(
    persist_directory: str | Path,
) -> Chroma:
    """Open an existing persistent policy collection."""
    client = get_chroma_client(persist_directory)

    existing_names = {
        collection.name
        for collection in client.list_collections()
    }

    if COLLECTION_NAME not in existing_names:
        raise FileNotFoundError(
            "The Chroma policy collection has not been built."
        )

    return Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
    )