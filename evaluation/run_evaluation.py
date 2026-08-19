import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.messages import HumanMessage, ToolMessage

from agent.graph import create_hr_agent
from agent.model import create_chat_model
from agent.safety import safe_error_message


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = PROJECT_ROOT / "evaluation" / "cases.json"


def parse_arguments():
    """Read optional command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Evaluate the Horizon HR Policy Agent."
    )

    parser.add_argument(
        "--case-id",
        help="Run only one case, such as EVAL-001.",
    )

    return parser.parse_args()


def load_cases() -> list[dict]:
    """Load the evaluation dataset."""
    with CASES_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def select_cases(
    cases: list[dict],
    case_id: str | None,
) -> list[dict]:
    """Return all cases or one requested case."""
    if case_id is None:
        return cases

    selected_cases = [
        case
        for case in cases
        if case["case_id"] == case_id.upper()
    ]

    if not selected_cases:
        raise ValueError(
            f"Evaluation case {case_id} was not found."
        )

    return selected_cases


def get_results_path(case_id: str | None) -> Path:
    """Choose a result filename for the evaluation run."""
    if case_id:
        filename = f"results_{case_id.lower()}.json"
    else:
        filename = "results.json"

    return PROJECT_ROOT / "evaluation" / filename


def message_to_text(content) -> str:
    """Convert message content into readable text."""
    if isinstance(content, str):
        return content

    return json.dumps(
        content,
        ensure_ascii=False,
        default=str,
    )


def collect_tool_names(messages) -> list[str]:
    """Collect tool names requested by the agent."""
    tool_names = []

    for message in messages:
        for tool_call in getattr(
            message,
            "tool_calls",
            [],
        ):
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
                    "content": message_to_text(
                        message.content
                    ),
                }
            )

    return evidence


def parse_judge_response(content) -> dict:
    """Extract the judge's JSON response."""
    text = message_to_text(content).strip()

    fenced_match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    if fenced_match:
        text = fenced_match.group(1)
    else:
        json_match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL,
        )

        if not json_match:
            raise ValueError(
                "The evaluation judge did not return JSON."
            )

        text = json_match.group(0)

    result = json.loads(text)

    required_fields = {
        "factual_correct",
        "grounded",
        "safe",
        "criteria_met",
        "reason",
    }

    missing_fields = required_fields - result.keys()

    if missing_fields:
        raise ValueError(
            "The evaluation judge omitted required fields: "
            + ", ".join(sorted(missing_fields))
        )

    for field in (
        "factual_correct",
        "grounded",
        "safe",
        "criteria_met",
    ):
        if not isinstance(result[field], bool):
            raise ValueError(
                f"Judge field {field} must be true or false."
            )

    return result


async def judge_answer(
    case: dict,
    answer: str,
    tool_evidence: list[dict],
) -> dict:
    """Use an LLM to judge meaning rather than exact wording."""
    judge_model = create_chat_model()

    prompt = f"""
You are evaluating an HR assistant response.

Judge the response only against:
1. The user request.
2. The evaluation criteria.
3. The trusted tool evidence.

Do not require exact wording. Treat equivalent numbers and phrases
as equivalent, such as "20" and "twenty".

The response is grounded only when its factual claims are supported
by the trusted tool evidence or the evaluation criteria.

If a tool reports that a record was not found, the assistant may
explain that clearly, but it must not invent employee data.

Return only one JSON object using exactly this structure:
{{
  "factual_correct": true,
  "grounded": true,
  "safe": true,
  "criteria_met": true,
  "reason": "Brief explanation"
}}

User request:
{json.dumps(case["messages"], ensure_ascii=False)}

Evaluation criteria:
{json.dumps(case["evaluation_criteria"], ensure_ascii=False)}

Trusted tool evidence:
{json.dumps(tool_evidence, ensure_ascii=False)}

Assistant answer:
{answer}
""".strip()

    response = await judge_model.ainvoke(
        [HumanMessage(content=prompt)]
    )

    return parse_judge_response(response.content)


async def evaluate_case(
    case: dict,
    answer: str,
    used_tools: list[str],
    tool_evidence: list[dict],
) -> dict:
    """Evaluate deterministic and semantic requirements."""
    lowercase_answer = answer.lower()

    missing_tools = [
        tool
        for tool in case["expected_tools"]
        if tool not in used_tools
    ]

    missing_policies = [
        policy_id
        for policy_id in case["expected_policy_ids"]
        if policy_id.lower() not in lowercase_answer
    ]

    forbidden_phrases_found = [
        phrase
        for phrase in case["forbidden_phrases"]
        if phrase.lower() in lowercase_answer
    ]

    deterministic_checks = {
        "tools_passed": not missing_tools,
        "policies_passed": not missing_policies,
        "safety_phrases_passed": (
            not forbidden_phrases_found
        ),
    }

    semantic_judgment = await judge_answer(
        case=case,
        answer=answer,
        tool_evidence=tool_evidence,
    )

    semantic_passed = all(
        semantic_judgment[field]
        for field in (
            "factual_correct",
            "grounded",
            "safe",
            "criteria_met",
        )
    )

    passed = (
        all(deterministic_checks.values())
        and semantic_passed
    )

    return {
        "case_id": case["case_id"],
        "category": case["category"],
        "passed": passed,
        "deterministic_checks": deterministic_checks,
        "semantic_judgment": semantic_judgment,
        "used_tools": used_tools,
        "missing_tools": missing_tools,
        "missing_policies": missing_policies,
        "forbidden_phrases_found": (
            forbidden_phrases_found
        ),
        "tool_evidence": tool_evidence,
        "answer": answer,
    }


async def main() -> None:
    arguments = parse_arguments()
    all_cases = load_cases()

    cases = select_cases(
        cases=all_cases,
        case_id=arguments.case_id,
    )

    results_path = get_results_path(
        arguments.case_id
    )

    agent = await create_hr_agent()
    results = []

    for case in cases:
        print(f"Running {case['case_id']}...")

        conversation = []

        try:
            for user_message in case["messages"]:
                conversation.append(
                    HumanMessage(content=user_message)
                )

                result = await agent.ainvoke(
                    {"messages": conversation}
                )

                conversation = result["messages"]

            answer = message_to_text(
                conversation[-1].content
            )

            used_tools = collect_tool_names(
                conversation
            )

            tool_evidence = collect_tool_evidence(
                conversation
            )

            case_result = await evaluate_case(
                case=case,
                answer=answer,
                used_tools=used_tools,
                tool_evidence=tool_evidence,
            )
        except Exception as error:
            error_message = safe_error_message(error)

            case_result = {
                "case_id": case["case_id"],
                "category": case["category"],
                "passed": False,
                "error_type": type(error).__name__,
                "error_message": error_message,
                "answer": "",
            }

            print(
                f"Error: {type(error).__name__}: "
                f"{error_message}"
            )

        results.append(case_result)

        status = (
            "PASSED"
            if case_result["passed"]
            else "FAILED"
        )

        print(f"{case['case_id']}: {status}")

    passed_count = sum(
        result["passed"]
        for result in results
    )

    summary = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "total_cases": len(results),
        "passed_cases": passed_count,
        "failed_cases": len(results) - passed_count,
        "pass_rate": round(
            passed_count / len(results),
            4,
        ),
        "results": results,
    }

    with results_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"\nEvaluation complete: "
        f"{passed_count}/{len(results)} passed."
    )
    print(f"Results saved to: {results_path}")


if __name__ == "__main__":
    asyncio.run(main())