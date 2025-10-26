"""
Example usage of the BSW scheduling agent evaluation system.

This script demonstrates how to:
1. Run individual test scenarios
2. Run all scenarios in batch
3. Calculate detailed metrics
4. Generate dashboard data
5. Export results for analysis
"""

import time
from typing import Dict, Any
from evaluation.scenarios import (
    ALL_SCENARIOS,
    run_scenario,
    run_all_scenarios,
    export_results_to_json
)
from evaluation.metrics import (
    calculate_conversation_score,
    get_detailed_conversation_metrics,
    track_tool_usage,
    get_detailed_latency_metrics,
    calculate_token_metrics,
    generate_dashboard_data,
    export_dashboard_data
)


# ===== MOCK AGENT FUNCTION FOR DEMONSTRATION =====

def mock_agent_function(patient_id: str, message: str) -> Dict[str, Any]:
    """
    Mock agent function that simulates agent response.

    In production, this would call your actual agent system.
    Replace this with your real agent orchestration logic.

    Args:
        patient_id: Patient ID
        message: User's message

    Returns:
        Agent response dictionary
    """
    # Simulate processing time
    time.sleep(0.5)

    # Simulate agent response based on message keywords
    if "orthopedic" in message.lower() or "knee" in message.lower():
        return {
            "message": "I'd be happy to help schedule your orthopedic follow-up. "
                      "Let me check Dr. Martinez's availability for you. "
                      "I have appointments available this Thursday at 10:00 AM. "
                      "Would that work for you?",
            "agent": "Orthopedic Agent",
            "tools_used": ["check_provider_availability", "search_appointment_slots"],
            "success": True
        }
    elif "cardiology" in message.lower() or "chest pain" in message.lower():
        return {
            "message": "I understand you're experiencing chest pain and need to see a cardiologist. "
                      "I've verified your Medicare coverage and referral. "
                      "Given the urgency, I can schedule you for tomorrow at 2:00 PM with Dr. Patel. "
                      "Is that acceptable?",
            "agent": "Cardiology Agent",
            "tools_used": ["verify_insurance", "check_referral_status",
                          "check_provider_availability", "search_appointment_slots"],
            "success": True
        }
    elif "reschedule" in message.lower():
        return {
            "message": "I can help you reschedule your appointment with Dr. Nguyen. "
                      "To avoid Tuesday, I have Wednesday at 3:00 PM or Thursday at 9:00 AM available. "
                      "Which would you prefer?",
            "agent": "Primary Care Agent",
            "tools_used": ["check_provider_availability", "search_appointment_slots"],
            "success": True
        }
    elif "annual physical" in message.lower() or "wellness" in message.lower():
        return {
            "message": "I'd be happy to help schedule your annual physical. "
                      "Your United Healthcare plan covers preventive care at 100%. "
                      "Dr. White has availability next Monday at 8:30 AM or Friday at 1:00 PM. "
                      "Which works better for you?",
            "agent": "Primary Care Agent",
            "tools_used": ["verify_insurance", "check_provider_availability",
                          "search_appointment_slots"],
            "success": True
        }
    else:
        return {
            "message": "I'd be happy to help you schedule an appointment. "
                      "Could you tell me more about what type of appointment you need?",
            "agent": "Router Agent",
            "tools_used": [],
            "success": False
        }


# ===== EXAMPLE 1: RUN SINGLE SCENARIO =====

def example_1_single_scenario():
    """Run a single test scenario and display results."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Running Single Scenario")
    print("="*80 + "\n")

    # Get first scenario
    scenario = ALL_SCENARIOS[0]

    print(f"Testing: {scenario.name}")
    print(f"Patient: {scenario.get_patient()}")
    print(f"Message: \"{scenario.initial_message}\"\n")

    # Run scenario
    result = run_scenario(scenario, mock_agent_function, verbose=True)

    print("\nResults Summary:")
    print(f"  Success: {result.success_achieved}")
    print(f"  Duration: {result.duration_seconds:.2f}s")
    print(f"  Tools Called: {result.tools_called}")
    print(f"  Agents Used: {result.agents_used}")
    print(f"  Conversation Score: {result.metrics['conversation_score']:.3f}")
    print(f"  Success Criteria Met: {sum(result.success_criteria_met.values())}/{len(result.success_criteria_met)}")


# ===== EXAMPLE 2: RUN ALL SCENARIOS =====

def example_2_all_scenarios():
    """Run all test scenarios and display aggregate results."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Running All Scenarios")
    print("="*80 + "\n")

    # Run all scenarios
    results = run_all_scenarios(mock_agent_function, verbose=False)

    # Display individual results
    print("\nIndividual Results:")
    for result in results:
        status = "✓" if result.success_achieved else "✗"
        print(f"  {status} {result.scenario_name}: "
              f"{result.duration_seconds:.2f}s, "
              f"score={result.metrics['conversation_score']:.3f}")

    # Calculate aggregate stats
    total = len(results)
    passed = sum(1 for r in results if r.success_achieved)
    avg_score = sum(r.metrics['conversation_score'] for r in results) / total
    avg_duration = sum(r.duration_seconds for r in results) / total

    print(f"\nAggregate Statistics:")
    print(f"  Pass Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"  Avg Conversation Score: {avg_score:.3f}")
    print(f"  Avg Duration: {avg_duration:.2f}s")


# ===== EXAMPLE 3: DETAILED METRICS ANALYSIS =====

def example_3_detailed_metrics():
    """Calculate and display detailed metrics."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Detailed Metrics Analysis")
    print("="*80 + "\n")

    # Create mock conversation
    conversation = [
        {
            "role": "user",
            "content": "I need to schedule a follow-up for my knee surgery.",
            "timestamp": time.time()
        },
        {
            "role": "assistant",
            "content": "I'd be happy to help you schedule your knee surgery follow-up. "
                      "Let me check available appointments with orthopedic specialists.",
            "agent": "Router Agent",
            "tools_used": ["check_provider_availability"],
            "timestamp": time.time() + 1.5
        },
        {
            "role": "user",
            "content": "I'd prefer Dr. Martinez if possible.",
            "timestamp": time.time() + 3.0
        },
        {
            "role": "assistant",
            "content": "Great! Dr. Robert Martinez has availability this Thursday at 10:00 AM "
                      "or Friday at 2:30 PM. Both are at the Plano location. Which works for you?",
            "agent": "Orthopedic Agent",
            "tools_used": ["search_appointment_slots"],
            "timestamp": time.time() + 5.0
        }
    ]

    # Conversation metrics
    print("CONVERSATION METRICS:")
    conv_metrics = get_detailed_conversation_metrics(conversation)
    print(f"  Overall Score: {conv_metrics.overall_score:.3f}")
    print(f"  - Relevance: {conv_metrics.relevance_score:.3f}")
    print(f"  - Helpfulness: {conv_metrics.helpfulness_score:.3f}")
    print(f"  - Accuracy: {conv_metrics.accuracy_score:.3f}")
    print(f"  - Naturalness: {conv_metrics.naturalness_score:.3f}")
    print(f"  Total Turns: {conv_metrics.total_turns}")
    print(f"  Avg Response Length: {conv_metrics.avg_response_length:.1f} words")

    # Tool metrics
    print("\nTOOL USAGE METRICS:")
    tools = ["check_provider_availability", "search_appointment_slots"]
    tool_metrics = track_tool_usage(tools)
    print(f"  Total Calls: {tool_metrics['total_calls']}")
    print(f"  Unique Tools: {tool_metrics['unique_tools']}")
    print(f"  Tool Frequency: {tool_metrics['tool_frequency']}")

    # Latency metrics
    print("\nLATENCY METRICS:")
    latency_metrics = get_detailed_latency_metrics(conversation, 5.0)
    print(f"  Total Duration: {latency_metrics.total_duration:.2f}s")
    print(f"  Avg Response Time: {latency_metrics.avg_response_time:.2f}s")
    print(f"  Min/Max: {latency_metrics.min_response_time:.2f}s / {latency_metrics.max_response_time:.2f}s")

    # Token metrics
    print("\nTOKEN METRICS:")
    token_metrics = calculate_token_metrics(conversation, success=True)
    print(f"  Total Tokens: {token_metrics.total_tokens}")
    print(f"  - Prompt: {token_metrics.prompt_tokens}")
    print(f"  - Completion: {token_metrics.completion_tokens}")
    print(f"  Estimated Cost: ${token_metrics.estimated_cost:.4f}")
    print(f"  Tokens per Turn: {token_metrics.tokens_per_turn:.1f}")


# ===== EXAMPLE 4: DASHBOARD DATA GENERATION =====

def example_4_dashboard_data():
    """Generate dashboard data from evaluation results."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Dashboard Data Generation")
    print("="*80 + "\n")

    # Run scenarios
    results = run_all_scenarios(mock_agent_function, verbose=False)

    # Convert results to dict format
    results_dict = [r.to_dict() for r in results]

    # Generate dashboard data
    dashboard_data = generate_dashboard_data(results_dict)

    print("Dashboard Data Summary:")
    print(f"\n1. OVERALL SUMMARY:")
    summary = dashboard_data['summary']
    print(f"   Total Scenarios: {summary['total_scenarios']}")
    print(f"   Passed: {summary['passed']}")
    print(f"   Failed: {summary['failed']}")
    print(f"   Success Rate: {summary['success_rate']:.1%}")

    print(f"\n2. CONVERSATION METRICS:")
    conv = dashboard_data['conversation_metrics']
    print(f"   Average Score: {conv['average_score']:.3f}")
    print(f"   Score Range: {conv['min_score']:.3f} - {conv['max_score']:.3f}")

    print(f"\n3. TOOL METRICS:")
    tools = dashboard_data['tool_metrics']
    print(f"   Total Tool Calls: {tools['total_calls']}")
    print(f"   Unique Tools Used: {tools['unique_tools']}")
    print(f"   Most Used Tool: {tools['most_used']}")

    print(f"\n4. LATENCY METRICS:")
    latency = dashboard_data['latency_metrics']
    print(f"   Avg Duration: {latency['avg_duration']:.2f}s")
    print(f"   Total Duration: {latency['total_duration']:.2f}s")

    print(f"\n5. TOKEN METRICS:")
    tokens = dashboard_data['token_metrics']
    print(f"   Total Tokens: {tokens['total_tokens']:,}")
    print(f"   Avg Tokens/Scenario: {tokens['avg_tokens_per_scenario']:.0f}")
    print(f"   Estimated Cost: ${tokens['estimated_cost']:.4f}")

    print(f"\n6. AGENT PERFORMANCE:")
    for agent_name, metrics in dashboard_data['agent_performance'].items():
        print(f"   {agent_name}:")
        print(f"     - Success Rate: {metrics['success_rate']:.1%}")
        print(f"     - Avg Score: {metrics['avg_conversation_score']:.3f}")
        print(f"     - Avg Response Time: {metrics['avg_response_time']:.2f}s")


# ===== EXAMPLE 5: EXPORT RESULTS =====

def example_5_export_results():
    """Export evaluation results to JSON files."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Export Results to JSON")
    print("="*80 + "\n")

    # Run scenarios
    results = run_all_scenarios(mock_agent_function, verbose=False)

    # Export raw results
    print("Exporting raw results...")
    export_results_to_json(results, "evaluation_results.json")

    # Export dashboard data
    print("Exporting dashboard data...")
    results_dict = [r.to_dict() for r in results]
    export_dashboard_data(results_dict, "dashboard_data.json")

    print("\nExport complete! Files created:")
    print("  - evaluation_results.json (raw scenario results)")
    print("  - dashboard_data.json (aggregated metrics for dashboard)")


# ===== MAIN EXECUTION =====

if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# BSW SCHEDULING AGENT - EVALUATION SYSTEM EXAMPLES")
    print("#"*80)

    # Run all examples
    example_1_single_scenario()
    example_2_all_scenarios()
    example_3_detailed_metrics()
    example_4_dashboard_data()
    example_5_export_results()

    print("\n" + "#"*80)
    print("# ALL EXAMPLES COMPLETED")
    print("#"*80 + "\n")

    print("\nNext Steps:")
    print("1. Replace mock_agent_function with your actual agent system")
    print("2. Integrate evaluation into your CI/CD pipeline")
    print("3. Use dashboard_data.json to visualize metrics in Streamlit")
    print("4. Add more scenarios as needed for comprehensive testing")
    print("5. Track metrics over time to monitor improvements\n")
