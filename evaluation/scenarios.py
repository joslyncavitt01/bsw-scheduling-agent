"""
Test scenarios for BSW scheduling agent evaluation.

Defines realistic patient scenarios to test multi-agent orchestration,
RAG retrieval, function calling, and conversation quality.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any
import time
import json

from mock_data import PATIENTS, get_patient_by_id


@dataclass
class SuccessCriteria:
    """Defines success criteria for a test scenario."""
    appointment_booked: bool = True
    correct_specialty_identified: bool = True
    insurance_verified: bool = False
    referral_checked: bool = False
    provider_matched_preferences: bool = False
    appropriate_urgency: bool = False
    tools_used_correctly: bool = True
    conversation_natural: bool = True

    def to_dict(self) -> Dict[str, bool]:
        """Convert to dictionary for evaluation."""
        return {
            "appointment_booked": self.appointment_booked,
            "correct_specialty_identified": self.correct_specialty_identified,
            "insurance_verified": self.insurance_verified,
            "referral_checked": self.referral_checked,
            "provider_matched_preferences": self.provider_matched_preferences,
            "appropriate_urgency": self.appropriate_urgency,
            "tools_used_correctly": self.tools_used_correctly,
            "conversation_natural": self.conversation_natural,
        }


@dataclass
class TestObjectives:
    """Test objectives and what capabilities are being evaluated."""
    primary_objectives: List[str]
    secondary_objectives: List[str]
    rag_components: List[str]  # What RAG knowledge should be retrieved
    expected_tools: List[str]  # Tools that should be called
    expected_agent_flow: List[str]  # Expected agent routing path

    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary."""
        return {
            "primary_objectives": self.primary_objectives,
            "secondary_objectives": self.secondary_objectives,
            "rag_components": self.rag_components,
            "expected_tools": self.expected_tools,
            "expected_agent_flow": self.expected_agent_flow,
        }


@dataclass
class TestScenario:
    """A complete test scenario for agent evaluation."""
    scenario_id: str
    name: str
    description: str
    patient_id: str
    initial_message: str
    expected_specialty: str
    success_criteria: SuccessCriteria
    test_objectives: TestObjectives
    difficulty_level: str  # "simple", "medium", "complex"
    estimated_turns: int  # Expected conversation length
    tags: List[str] = field(default_factory=list)

    def get_patient(self):
        """Get the patient object for this scenario."""
        return get_patient_by_id(self.patient_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert scenario to dictionary for serialization."""
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "description": self.description,
            "patient_id": self.patient_id,
            "initial_message": self.initial_message,
            "expected_specialty": self.expected_specialty,
            "success_criteria": self.success_criteria.to_dict(),
            "test_objectives": self.test_objectives.to_dict(),
            "difficulty_level": self.difficulty_level,
            "estimated_turns": self.estimated_turns,
            "tags": self.tags,
        }


# ===== SCENARIO DEFINITIONS =====

SCENARIO_1_ORTHOPEDIC_FOLLOWUP = TestScenario(
    scenario_id="SC001",
    name="Orthopedic Post-Op Follow-up",
    description="Patient Sarah Martinez needs 2-week post-op knee replacement follow-up",
    patient_id="PT001",
    initial_message="Hi, I had knee replacement surgery two weeks ago and need to schedule my follow-up appointment with Dr. Martinez.",
    expected_specialty="Orthopedic Surgery",
    success_criteria=SuccessCriteria(
        appointment_booked=True,
        correct_specialty_identified=True,
        insurance_verified=True,
        referral_checked=False,
        provider_matched_preferences=True,  # Should book with Dr. Martinez (DR003)
        appropriate_urgency=True,  # Post-op follow-ups are routine but important
        tools_used_correctly=True,
        conversation_natural=True,
    ),
    test_objectives=TestObjectives(
        primary_objectives=[
            "Route to orthopedic specialty agent",
            "Identify correct provider (Dr. Robert Martinez)",
            "Retrieve clinical protocol for post-op knee replacement",
            "Find appropriate follow-up appointment slots",
            "Successfully book appointment"
        ],
        secondary_objectives=[
            "Verify insurance coverage (BCBS)",
            "Confirm patient identity and recent surgery",
            "Provide pre-appointment instructions (bring PT notes)"
        ],
        rag_components=[
            "Post-Operative Knee Replacement Follow-up protocol",
            "Blue Cross Blue Shield insurance policy",
            "Orthopedic scheduling guidelines"
        ],
        expected_tools=[
            "check_provider_availability",
            "search_appointment_slots",
            "verify_insurance",
            "book_appointment"
        ],
        expected_agent_flow=[
            "Router Agent -> Orthopedic Agent"
        ]
    ),
    difficulty_level="medium",
    estimated_turns=6,
    tags=["orthopedic", "post-op", "follow-up", "clinical-protocol", "provider-matching"]
)


SCENARIO_2_CARDIOLOGY_NEW_PATIENT = TestScenario(
    scenario_id="SC002",
    name="Cardiology New Patient with Urgent Symptoms",
    description="Patient James Wilson has chest pain, needs cardiologist, Medicare insurance with referral requirements",
    patient_id="PT002",
    initial_message="Hello, I've been having some chest pain and my doctor referred me to see a cardiologist. I'm on Medicare. Can you help me schedule an appointment?",
    expected_specialty="Cardiology",
    success_criteria=SuccessCriteria(
        appointment_booked=True,
        correct_specialty_identified=True,
        insurance_verified=True,
        referral_checked=True,  # Should check for referral from PCP
        provider_matched_preferences=False,  # No specific provider requested
        appropriate_urgency=True,  # Chest pain is urgent
        tools_used_correctly=True,
        conversation_natural=True,
    ),
    test_objectives=TestObjectives(
        primary_objectives=[
            "Route to cardiology specialty agent",
            "Assess urgency of chest pain symptoms",
            "Verify Medicare coverage for cardiology",
            "Check for valid PCP referral",
            "Prioritize urgent appointment slots",
            "Successfully book appointment"
        ],
        secondary_objectives=[
            "Identify accepting cardiologists near patient",
            "Provide pre-appointment instructions (fasting, medications)",
            "Educate about Medicare coverage and costs"
        ],
        rag_components=[
            "Chest Pain Evaluation protocol",
            "Medicare insurance policy",
            "Cardiology referral requirements",
            "Urgent appointment scheduling guidelines"
        ],
        expected_tools=[
            "check_referral_status",
            "verify_insurance",
            "check_provider_availability",
            "search_appointment_slots",
            "book_appointment"
        ],
        expected_agent_flow=[
            "Router Agent -> Cardiology Agent"
        ]
    ),
    difficulty_level="complex",
    estimated_turns=8,
    tags=["cardiology", "new-patient", "urgent", "medicare", "referral", "chest-pain"]
)


SCENARIO_3_COMPLEX_RESCHEDULING = TestScenario(
    scenario_id="SC003",
    name="Complex Rescheduling with Provider Preference",
    description="Patient Lisa Chen has appointment conflict and needs to reschedule with specific provider preference",
    patient_id="PT003",
    initial_message="I have an appointment scheduled for next Tuesday but I have a work conflict. Can I reschedule to a different day? I'd prefer to stay with Dr. Nguyen if possible.",
    expected_specialty="Primary Care",
    success_criteria=SuccessCriteria(
        appointment_booked=True,
        correct_specialty_identified=True,
        insurance_verified=False,  # Not critical for reschedule
        referral_checked=False,
        provider_matched_preferences=True,  # Should prioritize Dr. Nguyen
        appropriate_urgency=False,  # Routine rescheduling
        tools_used_correctly=True,
        conversation_natural=True,
    ),
    test_objectives=TestObjectives(
        primary_objectives=[
            "Identify existing appointment (if stored)",
            "Route to primary care agent",
            "Find alternative slots with Dr. Nguyen (DR009)",
            "Handle constraint satisfaction (avoid Tuesday)",
            "Successfully reschedule appointment"
        ],
        secondary_objectives=[
            "Confirm patient preferences (day/time)",
            "Check for appointment cancellation policies",
            "Provide confirmation of new appointment"
        ],
        rag_components=[
            "Primary Care scheduling policies",
            "Aetna insurance policy (for coverage verification if needed)",
            "Appointment cancellation guidelines"
        ],
        expected_tools=[
            "check_provider_availability",
            "search_appointment_slots",
            "book_appointment"
        ],
        expected_agent_flow=[
            "Router Agent -> Primary Care Agent"
        ]
    ),
    difficulty_level="medium",
    estimated_turns=5,
    tags=["primary-care", "rescheduling", "provider-preference", "constraint-satisfaction"]
)


SCENARIO_4_PRIMARY_CARE_WELLNESS = TestScenario(
    scenario_id="SC004",
    name="Primary Care Annual Physical",
    description="Patient Michael Thompson wants to schedule annual wellness exam with insurance coverage verification",
    patient_id="PT004",
    initial_message="I'd like to schedule my annual physical. I have United Healthcare insurance. What times are available?",
    expected_specialty="Primary Care",
    success_criteria=SuccessCriteria(
        appointment_booked=True,
        correct_specialty_identified=True,
        insurance_verified=True,
        referral_checked=False,
        provider_matched_preferences=True,  # Should book with PCP Dr. White (DR008)
        appropriate_urgency=False,  # Preventive care is routine
        tools_used_correctly=True,
        conversation_natural=True,
    ),
    test_objectives=TestObjectives(
        primary_objectives=[
            "Route to primary care agent",
            "Identify this as preventive care/wellness visit",
            "Verify United Healthcare coverage for annual physical",
            "Match with patient's PCP (Dr. Susan White)",
            "Find appropriate appointment slots",
            "Successfully book appointment"
        ],
        secondary_objectives=[
            "Educate about preventive care coverage (typically 100% covered)",
            "Provide pre-appointment instructions (fasting labs)",
            "Mention age-appropriate screenings",
            "Confirm appointment details"
        ],
        rag_components=[
            "Annual Wellness Visit protocol",
            "United Healthcare insurance policy",
            "Preventive care coverage guidelines",
            "Primary care scheduling policies"
        ],
        expected_tools=[
            "check_provider_availability",
            "verify_insurance",
            "search_appointment_slots",
            "book_appointment"
        ],
        expected_agent_flow=[
            "Router Agent -> Primary Care Agent"
        ]
    ),
    difficulty_level="simple",
    estimated_turns=4,
    tags=["primary-care", "preventive", "wellness", "insurance-verification", "routine"]
)


# Collection of all scenarios
ALL_SCENARIOS = [
    SCENARIO_1_ORTHOPEDIC_FOLLOWUP,
    SCENARIO_2_CARDIOLOGY_NEW_PATIENT,
    SCENARIO_3_COMPLEX_RESCHEDULING,
    SCENARIO_4_PRIMARY_CARE_WELLNESS,
]


@dataclass
class ScenarioResult:
    """Results from running a test scenario."""
    scenario_id: str
    scenario_name: str
    patient_id: str
    start_time: float
    end_time: float
    duration_seconds: float
    conversation_history: List[Dict[str, Any]]
    tools_called: List[str]
    agents_used: List[str]
    success_achieved: bool
    success_criteria_met: Dict[str, bool]
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "patient_id": self.patient_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "conversation_history": self.conversation_history,
            "tools_called": self.tools_called,
            "agents_used": self.agents_used,
            "success_achieved": self.success_achieved,
            "success_criteria_met": self.success_criteria_met,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
        }


def run_scenario(
    scenario: TestScenario,
    agent_function: Callable[[str, str], Dict[str, Any]],
    verbose: bool = False
) -> ScenarioResult:
    """
    Run a single test scenario against the agent system.

    Args:
        scenario: The test scenario to run
        agent_function: Callable that takes (patient_id, message) and returns agent response
        verbose: Whether to print detailed progress

    Returns:
        ScenarioResult with detailed evaluation data
    """
    if verbose:
        print(f"\n{'='*80}")
        print(f"Running Scenario: {scenario.name}")
        print(f"Patient: {scenario.get_patient()}")
        print(f"Expected Specialty: {scenario.expected_specialty}")
        print(f"{'='*80}\n")

    start_time = time.time()
    conversation_history = []
    tools_called = []
    agents_used = []
    errors = []
    warnings = []

    try:
        # Initialize conversation with patient's initial message
        conversation_history.append({
            "role": "user",
            "content": scenario.initial_message,
            "timestamp": time.time()
        })

        if verbose:
            print(f"User: {scenario.initial_message}\n")

        # Call agent function
        response = agent_function(scenario.patient_id, scenario.initial_message)

        # Record agent response
        conversation_history.append({
            "role": "assistant",
            "content": response.get("message", ""),
            "agent": response.get("agent", "unknown"),
            "tools_used": response.get("tools_used", []),
            "timestamp": time.time()
        })

        if verbose:
            print(f"Agent ({response.get('agent', 'unknown')}): {response.get('message', '')}\n")

        # Track tools and agents
        if "tools_used" in response:
            tools_called.extend(response["tools_used"])
        if "agent" in response:
            agents_used.append(response["agent"])

        # Record any errors
        if "error" in response:
            errors.append(response["error"])

    except Exception as e:
        errors.append(f"Exception during scenario execution: {str(e)}")
        if verbose:
            print(f"ERROR: {str(e)}\n")

    end_time = time.time()
    duration = end_time - start_time

    # Import metrics module to evaluate results
    from evaluation.metrics import (
        evaluate_task_success,
        calculate_conversation_score,
        track_tool_usage
    )

    # Evaluate success criteria
    success_criteria_met = evaluate_task_success(
        conversation_history,
        scenario.success_criteria.to_dict(),
        tools_called,
        scenario.test_objectives.expected_tools
    )

    # Calculate overall success
    critical_criteria = ["appointment_booked", "correct_specialty_identified"]
    success_achieved = all(
        success_criteria_met.get(criterion, False)
        for criterion in critical_criteria
    )

    # Calculate metrics
    conversation_score = calculate_conversation_score(conversation_history)
    tool_usage_stats = track_tool_usage(tools_called)

    metrics = {
        "conversation_score": conversation_score,
        "tool_usage": tool_usage_stats,
        "conversation_turns": len(conversation_history),
        "total_tokens_estimate": sum(len(msg.get("content", "").split()) * 1.3 for msg in conversation_history),
    }

    # Create result object
    result = ScenarioResult(
        scenario_id=scenario.scenario_id,
        scenario_name=scenario.name,
        patient_id=scenario.patient_id,
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration,
        conversation_history=conversation_history,
        tools_called=tools_called,
        agents_used=agents_used,
        success_achieved=success_achieved,
        success_criteria_met=success_criteria_met,
        errors=errors,
        warnings=warnings,
        metrics=metrics
    )

    if verbose:
        print(f"\n{'='*80}")
        print(f"Scenario Complete: {'SUCCESS' if success_achieved else 'FAILED'}")
        print(f"Duration: {duration:.2f}s")
        print(f"Conversation Score: {conversation_score:.2f}")
        print(f"Tools Used: {len(tools_called)}")
        print(f"Success Criteria Met: {sum(success_criteria_met.values())}/{len(success_criteria_met)}")
        print(f"{'='*80}\n")

    return result


def run_all_scenarios(
    agent_function: Callable[[str, str], Dict[str, Any]],
    scenarios: Optional[List[TestScenario]] = None,
    verbose: bool = False
) -> List[ScenarioResult]:
    """
    Run all test scenarios and collect results.

    Args:
        agent_function: Callable that takes (patient_id, message) and returns agent response
        scenarios: List of scenarios to run (defaults to ALL_SCENARIOS)
        verbose: Whether to print detailed progress

    Returns:
        List of ScenarioResult objects
    """
    if scenarios is None:
        scenarios = ALL_SCENARIOS

    results = []

    print(f"\n{'#'*80}")
    print(f"# RUNNING {len(scenarios)} TEST SCENARIOS")
    print(f"{'#'*80}\n")

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[{i}/{len(scenarios)}] Starting: {scenario.name}")
        result = run_scenario(scenario, agent_function, verbose=verbose)
        results.append(result)

        status = " PASS" if result.success_achieved else " FAIL"
        print(f"[{i}/{len(scenarios)}] {status}: {scenario.name} ({result.duration_seconds:.2f}s)")

    # Print summary
    print(f"\n{'#'*80}")
    print(f"# EVALUATION SUMMARY")
    print(f"{'#'*80}")

    total = len(results)
    passed = sum(1 for r in results if r.success_achieved)
    failed = total - passed

    print(f"\nTotal Scenarios: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")

    avg_duration = sum(r.duration_seconds for r in results) / total
    avg_score = sum(r.metrics["conversation_score"] for r in results) / total

    print(f"\nAverage Duration: {avg_duration:.2f}s")
    print(f"Average Conversation Score: {avg_score:.2f}")

    return results


def get_scenario_by_id(scenario_id: str) -> Optional[TestScenario]:
    """Get a specific scenario by ID."""
    for scenario in ALL_SCENARIOS:
        if scenario.scenario_id == scenario_id:
            return scenario
    return None


def get_scenarios_by_tag(tag: str) -> List[TestScenario]:
    """Get all scenarios matching a specific tag."""
    return [s for s in ALL_SCENARIOS if tag in s.tags]


def get_scenarios_by_difficulty(difficulty: str) -> List[TestScenario]:
    """Get all scenarios of a specific difficulty level."""
    return [s for s in ALL_SCENARIOS if s.difficulty_level == difficulty]


def export_results_to_json(results: List[ScenarioResult], filepath: str) -> None:
    """Export scenario results to JSON file."""
    data = {
        "timestamp": datetime.now().isoformat(),
        "total_scenarios": len(results),
        "passed": sum(1 for r in results if r.success_achieved),
        "failed": sum(1 for r in results if not r.success_achieved),
        "results": [r.to_dict() for r in results]
    }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\nResults exported to: {filepath}")


if __name__ == "__main__":
    """Demo: Show all scenarios and their details."""
    print("\n" + "="*80)
    print("BSW SCHEDULING AGENT - TEST SCENARIOS")
    print("="*80 + "\n")

    for scenario in ALL_SCENARIOS:
        print(f"\n{scenario.scenario_id}: {scenario.name}")
        print(f"  Difficulty: {scenario.difficulty_level.upper()}")
        print(f"  Patient: {scenario.get_patient()}")
        print(f"  Specialty: {scenario.expected_specialty}")
        print(f"  Initial Message: \"{scenario.initial_message}\"")
        print(f"  Tags: {', '.join(scenario.tags)}")
        print(f"\n  Primary Objectives:")
        for obj in scenario.test_objectives.primary_objectives:
            print(f"    • {obj}")
        print(f"\n  Expected Tools: {', '.join(scenario.test_objectives.expected_tools)}")
        print(f"  Estimated Turns: {scenario.estimated_turns}")
        print(f"  {'-'*76}")

    print(f"\n{'='*80}")
    print(f"Total Scenarios: {len(ALL_SCENARIOS)}")
    print(f"  Simple: {len(get_scenarios_by_difficulty('simple'))}")
    print(f"  Medium: {len(get_scenarios_by_difficulty('medium'))}")
    print(f"  Complex: {len(get_scenarios_by_difficulty('complex'))}")
    print(f"{'='*80}\n")
