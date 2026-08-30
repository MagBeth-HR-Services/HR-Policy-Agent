import json

from langchain_core.messages import ToolMessage


OUTPUT_SUMMARY_LIMIT = 280
POLICY_SEARCH_TOOL = "policy_search_policies"


def message_to_text(content) -> str:
    """Convert message content into readable text."""
    if content is None:
        return ""

    if isinstance(content, str):
        return content

    return json.dumps(
        content,
        ensure_ascii=False,
        default=str,
    )


def parse_json_value(value):
    """Parse JSON when the tool result is a string."""
    if isinstance(value, str):
        stripped = value.strip()

        if not stripped:
            return stripped

        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return value

    return value


def unwrap_mcp_content(value):
    """Flatten MCP text wrappers into Python values."""
    parsed = parse_json_value(value)

    if isinstance(parsed, list) and parsed:
        first_item = parsed[0]

        if (
            isinstance(first_item, dict)
            and first_item.get("type") == "text"
            and "text" in first_item
        ):
            unwrapped = [
                parse_json_value(item.get("text", ""))
                for item in parsed
                if isinstance(item, dict)
            ]

            if len(unwrapped) == 1:
                return unwrapped[0]

            return unwrapped

    return parsed


def summarize_output(value) -> str:
    """Create a short, grader-readable tool output."""
    parsed = unwrap_mcp_content(value)

    if isinstance(parsed, (dict, list)):
        text = json.dumps(
            parsed,
            ensure_ascii=False,
            default=str,
        )
    else:
        text = str(parsed)

    text = " ".join(text.split())

    if len(text) <= OUTPUT_SUMMARY_LIMIT:
        return text

    return text[: OUTPUT_SUMMARY_LIMIT - 3] + "..."


def collect_tool_names(messages) -> list[str]:
    """Collect tool names requested by the agent."""
    tool_names = []

    for message in messages:
        for tool_call in getattr(message, "tool_calls", []):
            tool_names.append(tool_call["name"])

    return tool_names


def collect_tool_evidence(messages) -> list[dict]:
    """Collect trusted results returned by MCP tools."""
    evidence = []

    for message in messages:
        if isinstance(message, ToolMessage):
            evidence.append(
                {
                    "tool_name": message.name,
                    "content": message_to_text(message.content),
                }
            )

    return evidence


def collect_tool_trace(messages) -> list[dict]:
    """Build a concise operational trace of MCP tool calls."""
    arguments_by_id = {}

    for message in messages:
        for tool_call in getattr(message, "tool_calls", []):
            call_id = tool_call.get("id")

            if call_id:
                arguments_by_id[call_id] = {
                    "tool": tool_call.get("name", ""),
                    "arguments": tool_call.get("args", {}),
                }

    trace = []

    for message in messages:
        if not isinstance(message, ToolMessage):
            continue

        call_info = arguments_by_id.get(
            getattr(message, "tool_call_id", ""),
            {},
        )

        arguments = call_info.get("arguments", {})

        if not isinstance(arguments, dict):
            arguments = {"value": arguments}

        trace.append(
            {
                "tool": message.name or call_info.get("tool", ""),
                "arguments": arguments,
                "output_summary": summarize_output(
                    message.content
                ),
            }
        )

    return trace


def _citation_from_mapping(item: dict) -> dict | None:
    """Convert one policy-search result into a citation."""
    document_id = item.get("document_id")

    if not document_id:
        return None

    page_number = item.get("page_number", 0)

    try:
        page_number = int(page_number or 0)
    except (TypeError, ValueError):
        page_number = 0

    return {
        "document_id": str(document_id),
        "title": str(item.get("title") or ""),
        "section": str(item.get("section") or ""),
        "page_number": page_number,
        "source_file": str(item.get("source_file") or ""),
        "snippet": str(item.get("snippet") or ""),
    }


def collect_citations(messages) -> list[dict]:
    """Extract unique policy citations from MCP search results."""
    citations = []
    seen = set()

    for message in messages:
        if not isinstance(message, ToolMessage):
            continue

        if message.name != POLICY_SEARCH_TOOL:
            continue

        parsed = unwrap_mcp_content(message.content)

        if isinstance(parsed, dict):
            items = [parsed]
        elif isinstance(parsed, list):
            items = parsed
        else:
            continue

        for item in items:
            if not isinstance(item, dict):
                continue

            citation = _citation_from_mapping(item)

            if citation is None:
                continue

            identity = (
                citation["document_id"],
                citation["section"],
                citation["snippet"],
            )

            if identity in seen:
                continue

            seen.add(identity)
            citations.append(citation)

    return citations
