from mcp.server.fastmcp import FastMCP

from rag.retrieval import (
    cached_vector_store,
    resolve_chroma_path,
    search_policy_documents,
)


mcp = FastMCP("Horizon Policy Server")


@mcp.tool()
def health_check() -> str:
    """Confirm that the Policy MCP server is responding."""
    return "Policy MCP server is healthy."


@mcp.tool()
async def search_policies(
    query: str,
    number_of_results: int = 5,
    document_id: str | None = None,
    diversify: bool = False,
) -> list[dict]:
    """Search Horizon's HR policies and return citation-ready evidence."""
    return search_policy_documents(
        query=query,
        k=number_of_results,
        document_id=document_id,
        diversify=diversify,
    )


if __name__ == "__main__":
    cached_vector_store(
        str(resolve_chroma_path())
    )
    mcp.run(transport="stdio")