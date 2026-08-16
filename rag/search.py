import argparse

from rag.retrieval import search_policy_documents


def main():
    parser = argparse.ArgumentParser(
        description="Search the HR policy knowledge base."
    )

    parser.add_argument(
        "query",
        help="The policy question or search phrase.",
    )

    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of results to return.",
    )

    parser.add_argument(
        "--document-id",
        help="Limit results to one policy, such as POL-004.",
    )

    parser.add_argument(
        "--diversify",
        action="store_true",
        help="Return evidence from a wider range of policies.",
    )

    args = parser.parse_args()

    results = search_policy_documents(
        query=args.query,
        k=args.k,
        document_id=args.document_id,
        diversify=args.diversify,
    )

    for result in results:
        print(
            f"\n{result['rank']}. "
            f"{result['document_id']} | "
            f"{result['section']} | "
            f"score: {result['score']}"
        )
        print(f"Chunk: {result['chunk_id']}")
        print(f"Source: {result['source_file']}")
        print(f"Snippet: {result['snippet']}")


if __name__ == "__main__":
    main()