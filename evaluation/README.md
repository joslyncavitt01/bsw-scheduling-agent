# BSW Scheduling Agent - Evaluation System

Comprehensive evaluation framework for testing the multi-agent healthcare scheduling system. This system provides automated scenario testing, detailed metrics tracking, and real-time performance monitoring.

## Overview

The evaluation system consists of three main components:

1. **scenarios.py** - Test scenario definitions and execution framework
2. **metrics.py** - Metrics calculation and performance tracking
3. **example_usage.py** - Example implementations and usage patterns

## Features

### Test Scenarios

- **4 Realistic Patient Scenarios**:
  - Orthopedic Post-Op Follow-up (Medium difficulty)
  - Cardiology New Patient with Urgent Symptoms (Complex)
  - Complex Rescheduling with Provider Preference (Medium)
  - Primary Care Annual Wellness (Simple)

- **Comprehensive Success Criteria**:
  - Appointment booking success
  - Specialty identification accuracy
  - Insurance verification
  - Referral checking
  - Provider preference matching
  - Urgency assessment
  - Tool usage correctness
  - Conversation naturalness

### Metrics Tracking

- **Conversation Quality** (0-1 scores):
  - Relevance: How well agent addresses user needs
  - Helpfulness: Actionable information provided
  - Accuracy: Factual correctness
  - Naturalness: Conversation flow quality

- **Tool Usage Analytics**:
  - Tool call frequency
  - Tool usage patterns
  - Redundant call detection
  - Expected vs actual tool comparison

- **Latency Monitoring**:
  - Response time tracking
  - API call latency estimation
  - Min/max/median calculations

- **Token Consumption**:
  - Prompt vs completion tokens
  - Cost estimation (GPT-4o-mini pricing)
  - Token efficiency metrics

- **Per-Agent Performance**:
  - Success rates by agent
  - Average response times
  - Tool usage patterns
  - Common error tracking

## Quick Start

### 1. Run All Scenarios

```python
from evaluation import run_all_scenarios

def your_agent_function(patient_id: str, message: str) -> dict:
    # Your agent implementation
    return {
        "message": "Agent response",
        "agent": "Agent Name",
        "tools_used": ["tool1", "tool2"],
        "success": True
    }

results = run_all_scenarios(your_agent_function, verbose=True)
```

### 2. Run Single Scenario

```python
from evaluation import get_scenario_by_id, run_scenario

scenario = get_scenario_by_id("SC001")
result = run_scenario(scenario, your_agent_function, verbose=True)

print(f"Success: {result.success_achieved}")
print(f"Score: {result.metrics['conversation_score']}")
```

### 3. Calculate Metrics

```python
from evaluation import (
    calculate_conversation_score,
    track_tool_usage,
    calculate_token_metrics
)

# Conversation quality
score = calculate_conversation_score(conversation_history)

# Tool usage
tool_stats = track_tool_usage(["tool1", "tool2", "tool1"])

# Token consumption
token_metrics = calculate_token_metrics(conversation_history, success=True)
```

### 4. Generate Dashboard Data

```python
from evaluation import generate_dashboard_data, export_dashboard_data

results = run_all_scenarios(your_agent_function)
results_dict = [r.to_dict() for r in results]

dashboard_data = generate_dashboard_data(results_dict)
export_dashboard_data(results_dict, "dashboard_metrics.json")
```

## Usage Examples

See `example_usage.py` for comprehensive examples:

```bash
python evaluation/example_usage.py
```

This demonstrates:
- Running single scenarios
- Batch scenario execution
- Detailed metrics analysis
- Dashboard data generation
- Result export to JSON

## Test Scenarios

### SC001: Orthopedic Post-Op Follow-up
- **Patient**: Sarah Martinez (PT001)
- **Difficulty**: Medium
- **Focus**: Clinical protocol retrieval, provider matching
- **Expected Tools**: check_provider_availability, search_appointment_slots, verify_insurance, book_appointment

### SC002: Cardiology New Patient
- **Patient**: James Wilson (PT002)
- **Difficulty**: Complex
- **Focus**: Urgent symptoms, Medicare verification, referral checking
- **Expected Tools**: check_referral_status, verify_insurance, check_provider_availability, search_appointment_slots, book_appointment

### SC003: Complex Rescheduling
- **Patient**: Lisa Chen (PT003)
- **Difficulty**: Medium
- **Focus**: Constraint satisfaction, provider preference
- **Expected Tools**: check_provider_availability, search_appointment_slots, book_appointment

### SC004: Primary Care Wellness
- **Patient**: Michael Thompson (PT004)
- **Difficulty**: Simple
- **Focus**: Preventive care, insurance coverage
- **Expected Tools**: check_provider_availability, verify_insurance, search_appointment_slots, book_appointment

## Metrics Reference

### ConversationMetrics
```python
@dataclass
class ConversationMetrics:
    relevance_score: float       # 0-1
    helpfulness_score: float     # 0-1
    accuracy_score: float        # 0-1
    naturalness_score: float     # 0-1
    overall_score: float         # 0-1
    total_turns: int
    avg_response_length: float
```

### ToolUsageMetrics
```python
@dataclass
class ToolUsageMetrics:
    total_calls: int
    unique_tools: int
    tool_frequency: Dict[str, int]
    tool_success_rate: Dict[str, float]
    most_used_tool: str
    redundant_calls: int
```

### LatencyMetrics
```python
@dataclass
class LatencyMetrics:
    total_duration: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    median_response_time: float
    api_call_count: int
```

### TokenMetrics
```python
@dataclass
class TokenMetrics:
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    estimated_cost: float        # USD
    tokens_per_turn: float
    token_efficiency: float
```

## Integration with Streamlit

Use dashboard data in your Streamlit app:

```python
import streamlit as st
from evaluation import generate_dashboard_data

# Load results
with open('dashboard_metrics.json') as f:
    dashboard_data = json.load(f)

# Display metrics
st.metric("Success Rate",
          f"{dashboard_data['summary']['success_rate']:.1%}")

st.metric("Avg Conversation Score",
          f"{dashboard_data['conversation_metrics']['average_score']:.3f}")

# Plot tool usage
st.bar_chart(dashboard_data['tool_metrics']['tool_frequency'])
```

## Extending the System

### Add New Scenarios

```python
from evaluation import TestScenario, SuccessCriteria, TestObjectives

new_scenario = TestScenario(
    scenario_id="SC005",
    name="Your Scenario Name",
    description="Scenario description",
    patient_id="PT001",
    initial_message="User's initial message",
    expected_specialty="Specialty",
    success_criteria=SuccessCriteria(
        appointment_booked=True,
        correct_specialty_identified=True,
        # ... other criteria
    ),
    test_objectives=TestObjectives(
        primary_objectives=["Objective 1", "Objective 2"],
        secondary_objectives=["Secondary 1"],
        rag_components=["RAG doc 1"],
        expected_tools=["tool1", "tool2"],
        expected_agent_flow=["Agent1 -> Agent2"]
    ),
    difficulty_level="medium",
    estimated_turns=5,
    tags=["tag1", "tag2"]
)
```

### Add Custom Metrics

```python
from evaluation.metrics import ConversationMetrics

def calculate_custom_metric(conversation: List[Dict]) -> float:
    # Your custom metric logic
    score = 0.0
    # ... calculations ...
    return score
```

## File Structure

```
evaluation/
├── __init__.py           # Module exports
├── scenarios.py          # Test scenario definitions (21KB)
├── metrics.py            # Metrics calculation logic (32KB)
├── example_usage.py      # Usage examples (13KB)
└── README.md            # This file
```

## Best Practices

1. **Run scenarios regularly** - Integrate into CI/CD pipeline
2. **Track metrics over time** - Monitor improvements and regressions
3. **Review failed scenarios** - Analyze conversation history for issues
4. **Adjust success criteria** - As system evolves, update criteria
5. **Add domain-specific scenarios** - Cover edge cases and special workflows

## Performance Benchmarks

Target metrics for production-ready system:

- **Success Rate**: ≥ 90%
- **Conversation Score**: ≥ 0.75
- **Avg Response Time**: ≤ 3 seconds
- **Tool Usage Accuracy**: ≥ 85% (expected tools called)
- **Token Efficiency**: ≤ 2000 tokens per conversation

## Troubleshooting

### ImportError: No module named 'mock_data'
```bash
# Run from project root with PYTHONPATH
PYTHONPATH=/path/to/bsw-scheduling-agent python evaluation/scenarios.py
```

### Scenarios Failing
- Check that agent function returns correct format
- Verify tools_used list is populated
- Ensure conversation history has proper structure

### Metrics Show 0.0
- Verify conversation list is not empty
- Check that messages have "role" and "content" keys
- Ensure assistant messages include agent/tools_used

## API Reference

### Scenarios Module

- `run_scenario(scenario, agent_func, verbose)` - Run single scenario
- `run_all_scenarios(agent_func, scenarios, verbose)` - Run multiple scenarios
- `get_scenario_by_id(scenario_id)` - Get scenario by ID
- `get_scenarios_by_tag(tag)` - Filter scenarios by tag
- `get_scenarios_by_difficulty(level)` - Filter by difficulty
- `export_results_to_json(results, filepath)` - Export results

### Metrics Module

- `calculate_conversation_score(conversation)` - Overall quality score
- `get_detailed_conversation_metrics(conversation)` - Full metrics object
- `track_tool_usage(tools_used)` - Tool usage statistics
- `get_detailed_tool_metrics(tools_used, expected)` - Full tool metrics
- `measure_latency(start_time, end_time)` - Calculate latency
- `calculate_token_metrics(conversation, success)` - Token consumption
- `evaluate_task_success(conversation, criteria, tools, expected)` - Evaluate success
- `generate_dashboard_data(results)` - Aggregate metrics for dashboard
- `export_dashboard_data(results, filepath)` - Export dashboard JSON

## Contributing

When adding new scenarios or metrics:

1. Follow existing dataclass patterns
2. Add type hints for all functions
3. Include docstrings with Args/Returns
4. Update this README with new functionality
5. Add usage examples to example_usage.py

## License

Part of BSW Scheduling Agent Demo System
Copyright 2025 Baylor Scott & White Health

---

**Questions?** See example_usage.py for complete working examples.
