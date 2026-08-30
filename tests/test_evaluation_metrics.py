from evaluation.run_evaluation import compute_aggregates


def test_compute_aggregates_from_scored_cases():
    results = [
        {
            "category": "policy_rag",
            "passed": True,
            "latency_seconds": 1.0,
            "deterministic_checks": {
                "tools_passed": True,
                "policies_passed": True,
                "safety_phrases_passed": True,
            },
            "semantic_judgment": {
                "grounded": True,
                "safe": True,
            },
        },
        {
            "category": "combined_workflow",
            "passed": False,
            "latency_seconds": 3.0,
            "deterministic_checks": {
                "tools_passed": False,
                "policies_passed": True,
                "safety_phrases_passed": True,
            },
            "semantic_judgment": {
                "grounded": False,
                "safe": True,
            },
        },
        {
            "category": "out_of_scope",
            "passed": True,
            "latency_seconds": 2.0,
            "deterministic_checks": {
                "tools_passed": True,
                "policies_passed": True,
                "safety_phrases_passed": True,
            },
            "semantic_judgment": {
                "grounded": True,
                "safe": True,
            },
        },
    ]

    metrics = compute_aggregates(results)

    assert metrics["groundedness"] == 0.6667
    assert metrics["citation_accuracy"] == 1.0
    assert metrics["tool_selection_accuracy"] == 0.6667
    assert metrics["workflow_completion_rate"] == 0.0
    assert metrics["escalation_or_clarification_accuracy"] == 1.0
    assert metrics["action_safety_pass_rate"] == 1.0
    assert metrics["warm_latency_seconds"]["sample_size"] == 3
    assert metrics["warm_latency_seconds"]["p50"] == 2.0
