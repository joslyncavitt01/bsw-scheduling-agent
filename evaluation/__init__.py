"""
BSW Scheduling Agent - Evaluation System

Comprehensive evaluation framework for testing multi-agent healthcare scheduling system.
Includes test scenarios, metrics tracking, and dashboard data generation.
"""

from evaluation.scenarios import (
    TestScenario,
    SuccessCriteria,
    TestObjectives,
    ScenarioResult,
    ALL_SCENARIOS,
    SCENARIO_1_ORTHOPEDIC_FOLLOWUP,
    SCENARIO_2_CARDIOLOGY_NEW_PATIENT,
    SCENARIO_3_COMPLEX_RESCHEDULING,
    SCENARIO_4_PRIMARY_CARE_WELLNESS,
    run_scenario,
    run_all_scenarios,
    get_scenario_by_id,
    get_scenarios_by_tag,
    get_scenarios_by_difficulty,
    export_results_to_json
)

from evaluation.metrics import (
    ConversationMetrics,
    ToolUsageMetrics,
    LatencyMetrics,
    TokenMetrics,
    AgentPerformanceMetrics,
    TaskSuccessMetrics,
    calculate_conversation_score,
    get_detailed_conversation_metrics,
    track_tool_usage,
    get_detailed_tool_metrics,
    measure_latency,
    get_detailed_latency_metrics,
    estimate_tokens,
    calculate_token_metrics,
    evaluate_task_success,
    calculate_agent_performance,
    compare_agent_performance,
    generate_dashboard_data,
    export_dashboard_data
)

__all__ = [
    # Scenarios
    "TestScenario",
    "SuccessCriteria",
    "TestObjectives",
    "ScenarioResult",
    "ALL_SCENARIOS",
    "SCENARIO_1_ORTHOPEDIC_FOLLOWUP",
    "SCENARIO_2_CARDIOLOGY_NEW_PATIENT",
    "SCENARIO_3_COMPLEX_RESCHEDULING",
    "SCENARIO_4_PRIMARY_CARE_WELLNESS",
    "run_scenario",
    "run_all_scenarios",
    "get_scenario_by_id",
    "get_scenarios_by_tag",
    "get_scenarios_by_difficulty",
    "export_results_to_json",

    # Metrics
    "ConversationMetrics",
    "ToolUsageMetrics",
    "LatencyMetrics",
    "TokenMetrics",
    "AgentPerformanceMetrics",
    "TaskSuccessMetrics",
    "calculate_conversation_score",
    "get_detailed_conversation_metrics",
    "track_tool_usage",
    "get_detailed_tool_metrics",
    "measure_latency",
    "get_detailed_latency_metrics",
    "estimate_tokens",
    "calculate_token_metrics",
    "evaluate_task_success",
    "calculate_agent_performance",
    "compare_agent_performance",
    "generate_dashboard_data",
    "export_dashboard_data"
]

__version__ = "1.0.0"
__author__ = "BSW Health AI Team"
