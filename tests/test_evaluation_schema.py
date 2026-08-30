import json
from pathlib import Path


CASES_PATH = (
    Path(__file__).resolve().parents[1]
    / "evaluation"
    / "cases.json"
)

REQUIRED_CATEGORIES = {
    "policy_rag",
    "employee_data",
    "combined_workflow",
    "missing_information",
    "invalid_employee",
    "unknown_employee",
    "confirmation_safety",
    "multi_document",
    "out_of_scope",
}


def test_evaluation_dataset_meets_assignment_shape():
    cases = json.loads(
        CASES_PATH.read_text(encoding="utf-8")
    )

    assert 20 <= len(cases) <= 30

    case_ids = [case["case_id"] for case in cases]
    assert len(case_ids) == len(set(case_ids))

    categories = {case["category"] for case in cases}
    assert REQUIRED_CATEGORIES.issubset(categories)

    multi_document_cases = [
        case
        for case in cases
        if len(case["expected_policy_ids"]) >= 2
    ]

    assert multi_document_cases

    for case in cases:
        assert case["gold_answer"].strip()
        assert case["messages"]
        assert isinstance(case["expected_tools"], list)
        assert isinstance(case["evaluation_criteria"], list)
        assert isinstance(case["forbidden_phrases"], list)
