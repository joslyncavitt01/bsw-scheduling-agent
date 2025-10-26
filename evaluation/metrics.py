"""
Metrics tracking and evaluation for BSW scheduling agent.

Provides comprehensive metrics for conversation quality, task success,
tool usage analytics, latency monitoring, and per-agent performance comparison.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import Counter, defaultdict
import time
import json
import re


@dataclass
class ConversationMetrics:
    """Metrics for conversation quality assessment."""
    relevance_score: float  # 0-1: How relevant responses are to user queries
    helpfulness_score: float  # 0-1: How helpful responses are
    accuracy_score: float  # 0-1: Factual accuracy of information
    naturalness_score: float  # 0-1: How natural the conversation flows
    overall_score: float  # 0-1: Weighted average
    total_turns: int
    avg_response_length: float
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "relevance_score": round(self.relevance_score, 3),
            "helpfulness_score": round(self.helpfulness_score, 3),
            "accuracy_score": round(self.accuracy_score, 3),
            "naturalness_score": round(self.naturalness_score, 3),
            "overall_score": round(self.overall_score, 3),
            "total_turns": self.total_turns,
            "avg_response_length": round(self.avg_response_length, 1),
            "details": self.details
        }


@dataclass
class ToolUsageMetrics:
    """Metrics for tool/function calling analysis."""
    total_calls: int
    unique_tools: int
    tool_frequency: Dict[str, int]
    tool_success_rate: Dict[str, float]
    avg_tools_per_conversation: float
    most_used_tool: Optional[str]
    least_used_tool: Optional[str]
    tool_sequence: List[str]
    redundant_calls: int  # Same tool called multiple times unnecessarily

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_calls": self.total_calls,
            "unique_tools": self.unique_tools,
            "tool_frequency": self.tool_frequency,
            "tool_success_rate": self.tool_success_rate,
            "avg_tools_per_conversation": round(self.avg_tools_per_conversation, 2),
            "most_used_tool": self.most_used_tool,
            "least_used_tool": self.least_used_tool,
            "tool_sequence": self.tool_sequence,
            "redundant_calls": self.redundant_calls
        }


@dataclass
class LatencyMetrics:
    """Metrics for performance and response time tracking."""
    total_duration: float  # seconds
    avg_response_time: float  # seconds per turn
    min_response_time: float
    max_response_time: float
    median_response_time: float
    response_times: List[float]
    api_call_count: int
    estimated_api_latency: float  # seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_duration": round(self.total_duration, 2),
            "avg_response_time": round(self.avg_response_time, 2),
            "min_response_time": round(self.min_response_time, 2),
            "max_response_time": round(self.max_response_time, 2),
            "median_response_time": round(self.median_response_time, 2),
            "api_call_count": self.api_call_count,
            "estimated_api_latency": round(self.estimated_api_latency, 2)
        }


@dataclass
class TokenMetrics:
    """Metrics for token consumption tracking."""
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    estimated_cost: float  # USD
    tokens_per_turn: float
    token_efficiency: float  # Success / tokens ratio

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "estimated_cost": round(self.estimated_cost, 4),
            "tokens_per_turn": round(self.tokens_per_turn, 1),
            "token_efficiency": round(self.token_efficiency, 4)
        }


@dataclass
class AgentPerformanceMetrics:
    """Per-agent performance comparison metrics."""
    agent_name: str
    total_invocations: int
    success_rate: float
    avg_conversation_score: float
    avg_response_time: float
    total_tokens_used: int
    tools_called: Dict[str, int]
    common_errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "total_invocations": self.total_invocations,
            "success_rate": round(self.success_rate, 3),
            "avg_conversation_score": round(self.avg_conversation_score, 3),
            "avg_response_time": round(self.avg_response_time, 2),
            "total_tokens_used": self.total_tokens_used,
            "tools_called": self.tools_called,
            "common_errors": self.common_errors
        }


@dataclass
class TaskSuccessMetrics:
    """Metrics for task completion and success rate."""
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    success_rate: float
    criteria_met: Dict[str, int]  # Count of each criterion met
    common_failure_reasons: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": round(self.success_rate, 3),
            "criteria_met": self.criteria_met,
            "common_failure_reasons": self.common_failure_reasons
        }


# ===== CONVERSATION QUALITY SCORING =====

def calculate_conversation_score(conversation: List[Dict]) -> float:
    """
    Calculate overall conversation quality score (0-1).

    Evaluates:
    - Relevance: Does agent address user's needs?
    - Helpfulness: Does agent provide actionable information?
    - Accuracy: Are facts and data correct?
    - Naturalness: Does conversation flow naturally?

    Args:
        conversation: List of conversation turns with role/content

    Returns:
        Overall conversation quality score (0-1)
    """
    if not conversation or len(conversation) < 2:
        return 0.0

    # Extract assistant messages
    assistant_messages = [
        msg for msg in conversation
        if msg.get("role") == "assistant"
    ]

    if not assistant_messages:
        return 0.0

    # Component scores
    relevance = _score_relevance(conversation)
    helpfulness = _score_helpfulness(assistant_messages)
    accuracy = _score_accuracy(assistant_messages)
    naturalness = _score_naturalness(assistant_messages)

    # Weighted average (can be tuned)
    weights = {
        "relevance": 0.30,
        "helpfulness": 0.30,
        "accuracy": 0.25,
        "naturalness": 0.15
    }

    overall = (
        relevance * weights["relevance"] +
        helpfulness * weights["helpfulness"] +
        accuracy * weights["accuracy"] +
        naturalness * weights["naturalness"]
    )

    return round(overall, 3)


def _score_relevance(conversation: List[Dict]) -> float:
    """Score how relevant agent responses are to user queries."""
    if len(conversation) < 2:
        return 0.0

    relevant_indicators = [
        "appointment", "schedule", "available", "book", "confirm",
        "insurance", "provider", "doctor", "time", "date"
    ]

    score = 0.0
    pairs = 0

    for i in range(len(conversation) - 1):
        if conversation[i].get("role") == "user":
            user_msg = conversation[i].get("content", "").lower()
            agent_msg = conversation[i + 1].get("content", "").lower()

            # Check if agent response mentions keywords from user message
            user_keywords = set(re.findall(r'\b\w+\b', user_msg))
            agent_keywords = set(re.findall(r'\b\w+\b', agent_msg))

            overlap = len(user_keywords & agent_keywords)
            relevance_ratio = overlap / max(len(user_keywords), 1)

            # Bonus for healthcare-specific relevance
            has_relevant_terms = any(
                term in agent_msg for term in relevant_indicators
            )

            pair_score = min(1.0, relevance_ratio + (0.2 if has_relevant_terms else 0))
            score += pair_score
            pairs += 1

    return score / max(pairs, 1)


def _score_helpfulness(assistant_messages: List[Dict]) -> float:
    """Score how helpful agent responses are."""
    if not assistant_messages:
        return 0.0

    helpful_indicators = [
        r'\d{1,2}:\d{2}',  # Times
        r'\d{4}-\d{2}-\d{2}',  # Dates
        r'dr\.?\s+\w+',  # Doctor names
        r'\$\d+',  # Costs
        r'appointment',
        r'confirmed',
        r'available',
        r'insurance',
        r'copay'
    ]

    total_score = 0.0

    for msg in assistant_messages:
        content = msg.get("content", "").lower()
        msg_score = 0.0

        # Check for specific, actionable information
        for pattern in helpful_indicators:
            if re.search(pattern, content):
                msg_score += 0.15

        # Length penalty: Too short may not be helpful
        word_count = len(content.split())
        if word_count < 10:
            msg_score *= 0.5
        elif word_count > 100:
            msg_score *= 0.9  # Slight penalty for verbosity

        total_score += min(1.0, msg_score)

    return total_score / len(assistant_messages)


def _score_accuracy(assistant_messages: List[Dict]) -> float:
    """
    Score factual accuracy of agent responses.

    In a real system, this would verify against ground truth.
    For now, we check for hallucination indicators and consistency.
    """
    if not assistant_messages:
        return 0.0

    # Indicators of potential inaccuracy
    uncertain_phrases = [
        "i think", "maybe", "probably", "i'm not sure",
        "i don't know", "possibly"
    ]

    # Indicators of confidence/accuracy
    confident_phrases = [
        "confirmed", "verified", "available", "scheduled",
        "according to", "based on"
    ]

    total_score = 0.0

    for msg in assistant_messages:
        content = msg.get("content", "").lower()
        msg_score = 0.7  # Start with baseline

        # Penalize uncertainty
        uncertainty_count = sum(
            1 for phrase in uncertain_phrases if phrase in content
        )
        msg_score -= (uncertainty_count * 0.1)

        # Reward confidence with facts
        confidence_count = sum(
            1 for phrase in confident_phrases if phrase in content
        )
        msg_score += (confidence_count * 0.1)

        # Check if tools were used (indicates data lookup)
        if msg.get("tools_used"):
            msg_score += 0.2

        total_score += max(0.0, min(1.0, msg_score))

    return total_score / len(assistant_messages)


def _score_naturalness(assistant_messages: List[Dict]) -> float:
    """Score how natural and conversational the responses are."""
    if not assistant_messages:
        return 0.0

    natural_indicators = [
        r'\b(hi|hello|thanks|thank you|please)\b',
        r'\b(great|perfect|wonderful|excellent)\b',
        r'\?',  # Questions
        r'!',  # Exclamations
    ]

    robotic_indicators = [
        r'^\s*error:',
        r'^\s*warning:',
        r'\{.*\}',  # JSON-like responses
        r'^\s*\[.*\]'  # Array-like responses
    ]

    total_score = 0.0

    for msg in assistant_messages:
        content = msg.get("content", "")
        msg_score = 0.5  # Baseline

        # Check for natural language indicators
        natural_count = sum(
            1 for pattern in natural_indicators
            if re.search(pattern, content, re.IGNORECASE)
        )
        msg_score += (natural_count * 0.1)

        # Penalize robotic responses
        robotic_count = sum(
            1 for pattern in robotic_indicators
            if re.search(pattern, content)
        )
        msg_score -= (robotic_count * 0.3)

        # Check sentence variety
        sentences = content.split('.')
        if len(sentences) > 1:
            msg_score += 0.1

        total_score += max(0.0, min(1.0, msg_score))

    return total_score / len(assistant_messages)


def get_detailed_conversation_metrics(conversation: List[Dict]) -> ConversationMetrics:
    """
    Get detailed conversation quality metrics.

    Args:
        conversation: List of conversation turns

    Returns:
        ConversationMetrics object with detailed scoring
    """
    if not conversation:
        return ConversationMetrics(
            relevance_score=0.0,
            helpfulness_score=0.0,
            accuracy_score=0.0,
            naturalness_score=0.0,
            overall_score=0.0,
            total_turns=0,
            avg_response_length=0.0
        )

    assistant_messages = [
        msg for msg in conversation
        if msg.get("role") == "assistant"
    ]

    relevance = _score_relevance(conversation)
    helpfulness = _score_helpfulness(assistant_messages)
    accuracy = _score_accuracy(assistant_messages)
    naturalness = _score_naturalness(assistant_messages)

    overall = calculate_conversation_score(conversation)

    avg_length = (
        sum(len(msg.get("content", "").split()) for msg in assistant_messages) /
        max(len(assistant_messages), 1)
    )

    return ConversationMetrics(
        relevance_score=relevance,
        helpfulness_score=helpfulness,
        accuracy_score=accuracy,
        naturalness_score=naturalness,
        overall_score=overall,
        total_turns=len(conversation),
        avg_response_length=avg_length,
        details={
            "user_turns": len([m for m in conversation if m.get("role") == "user"]),
            "assistant_turns": len(assistant_messages)
        }
    )


# ===== TOOL USAGE ANALYTICS =====

def track_tool_usage(tools_used: List[str]) -> Dict[str, Any]:
    """
    Track and analyze tool/function calling patterns.

    Args:
        tools_used: List of tool names that were called

    Returns:
        Dictionary with tool usage statistics
    """
    if not tools_used:
        return {
            "total_calls": 0,
            "unique_tools": 0,
            "tool_frequency": {},
            "most_used": None,
            "least_used": None,
            "tool_sequence": []
        }

    frequency = Counter(tools_used)

    return {
        "total_calls": len(tools_used),
        "unique_tools": len(frequency),
        "tool_frequency": dict(frequency),
        "most_used": frequency.most_common(1)[0][0] if frequency else None,
        "least_used": frequency.most_common()[-1][0] if frequency else None,
        "tool_sequence": tools_used
    }


def get_detailed_tool_metrics(
    tools_used: List[str],
    expected_tools: Optional[List[str]] = None
) -> ToolUsageMetrics:
    """
    Get detailed tool usage metrics with comparison to expected tools.

    Args:
        tools_used: List of tools that were actually called
        expected_tools: List of tools that should have been called

    Returns:
        ToolUsageMetrics object
    """
    if not tools_used:
        return ToolUsageMetrics(
            total_calls=0,
            unique_tools=0,
            tool_frequency={},
            tool_success_rate={},
            avg_tools_per_conversation=0.0,
            most_used_tool=None,
            least_used_tool=None,
            tool_sequence=[],
            redundant_calls=0
        )

    frequency = Counter(tools_used)

    # Detect redundant calls (same tool called multiple times in sequence)
    redundant = 0
    for i in range(len(tools_used) - 1):
        if tools_used[i] == tools_used[i + 1]:
            redundant += 1

    # Calculate success rate (if expected tools provided)
    success_rate = {}
    if expected_tools:
        for tool in expected_tools:
            success_rate[tool] = 1.0 if tool in tools_used else 0.0

    return ToolUsageMetrics(
        total_calls=len(tools_used),
        unique_tools=len(frequency),
        tool_frequency=dict(frequency),
        tool_success_rate=success_rate,
        avg_tools_per_conversation=len(tools_used),
        most_used_tool=frequency.most_common(1)[0][0],
        least_used_tool=frequency.most_common()[-1][0],
        tool_sequence=tools_used,
        redundant_calls=redundant
    )


# ===== LATENCY MEASUREMENT =====

def measure_latency(start_time: float, end_time: float) -> float:
    """
    Measure latency between two timestamps.

    Args:
        start_time: Start timestamp (from time.time())
        end_time: End timestamp (from time.time())

    Returns:
        Latency in seconds
    """
    return round(end_time - start_time, 3)


def get_detailed_latency_metrics(
    conversation: List[Dict],
    total_duration: float
) -> LatencyMetrics:
    """
    Calculate detailed latency metrics from conversation timestamps.

    Args:
        conversation: List of conversation turns with timestamps
        total_duration: Total conversation duration in seconds

    Returns:
        LatencyMetrics object
    """
    response_times = []

    # Calculate time between turns
    for i in range(len(conversation) - 1):
        t1 = conversation[i].get("timestamp", 0)
        t2 = conversation[i + 1].get("timestamp", 0)
        if t1 and t2:
            response_times.append(t2 - t1)

    if not response_times:
        response_times = [total_duration]

    # Sort for median calculation
    sorted_times = sorted(response_times)
    median_idx = len(sorted_times) // 2
    median = sorted_times[median_idx] if sorted_times else 0.0

    # Estimate API calls (agent responses)
    api_calls = len([m for m in conversation if m.get("role") == "assistant"])

    return LatencyMetrics(
        total_duration=total_duration,
        avg_response_time=sum(response_times) / max(len(response_times), 1),
        min_response_time=min(response_times) if response_times else 0.0,
        max_response_time=max(response_times) if response_times else 0.0,
        median_response_time=median,
        response_times=response_times,
        api_call_count=api_calls,
        estimated_api_latency=total_duration * 0.8  # Assume 80% is API time
    )


# ===== TOKEN CONSUMPTION TRACKING =====

def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.
    Rough approximation: 1 token ~= 0.75 words
    """
    words = len(text.split())
    return int(words * 1.3)


def calculate_token_metrics(
    conversation: List[Dict],
    success: bool = False
) -> TokenMetrics:
    """
    Calculate token consumption metrics.

    Args:
        conversation: List of conversation turns
        success: Whether the task was successful

    Returns:
        TokenMetrics object
    """
    prompt_tokens = 0
    completion_tokens = 0

    for msg in conversation:
        content = msg.get("content", "")
        tokens = estimate_tokens(content)

        if msg.get("role") == "user":
            prompt_tokens += tokens
        elif msg.get("role") == "assistant":
            completion_tokens += tokens

    total_tokens = prompt_tokens + completion_tokens

    # Pricing for GPT-4o-mini (as of 2024)
    # $0.150 per 1M input tokens, $0.600 per 1M output tokens
    cost = (
        (prompt_tokens / 1_000_000 * 0.150) +
        (completion_tokens / 1_000_000 * 0.600)
    )

    turns = len(conversation)
    tokens_per_turn = total_tokens / max(turns, 1)

    # Token efficiency: Success per token
    efficiency = (1.0 if success else 0.0) / max(total_tokens, 1)

    return TokenMetrics(
        total_tokens=total_tokens,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        estimated_cost=cost,
        tokens_per_turn=tokens_per_turn,
        token_efficiency=efficiency
    )


# ===== TASK SUCCESS EVALUATION =====

def evaluate_task_success(
    conversation: List[Dict],
    success_criteria: Dict[str, bool],
    tools_called: List[str],
    expected_tools: List[str]
) -> Dict[str, bool]:
    """
    Evaluate whether task success criteria were met.

    Args:
        conversation: List of conversation turns
        success_criteria: Dictionary of criteria to check
        tools_called: List of tools that were called
        expected_tools: List of tools that should be called

    Returns:
        Dictionary mapping criteria to whether they were met
    """
    results = {}

    # Join all conversation content for analysis
    all_content = " ".join(
        msg.get("content", "").lower()
        for msg in conversation
    )

    # Check appointment_booked
    if "appointment_booked" in success_criteria:
        booked_indicators = ["confirmed", "scheduled", "booked", "appointment set"]
        results["appointment_booked"] = any(
            indicator in all_content for indicator in booked_indicators
        ) and "book_appointment" in tools_called

    # Check correct_specialty_identified
    if "correct_specialty_identified" in success_criteria:
        specialty_indicators = ["orthopedic", "cardiology", "primary care"]
        results["correct_specialty_identified"] = any(
            indicator in all_content for indicator in specialty_indicators
        )

    # Check insurance_verified
    if "insurance_verified" in success_criteria:
        results["insurance_verified"] = (
            "verify_insurance" in tools_called or
            "insurance" in all_content
        )

    # Check referral_checked
    if "referral_checked" in success_criteria:
        results["referral_checked"] = (
            "check_referral" in tools_called or
            "referral" in all_content
        )

    # Check provider_matched_preferences
    if "provider_matched_preferences" in success_criteria:
        provider_indicators = ["dr.", "doctor", "provider"]
        results["provider_matched_preferences"] = (
            any(indicator in all_content for indicator in provider_indicators) and
            "check_provider" in tools_called
        )

    # Check appropriate_urgency
    if "appropriate_urgency" in success_criteria:
        urgency_indicators = ["urgent", "asap", "soon", "emergency", "priority"]
        results["appropriate_urgency"] = any(
            indicator in all_content for indicator in urgency_indicators
        )

    # Check tools_used_correctly
    if "tools_used_correctly" in success_criteria:
        # At least 50% of expected tools should be called
        if expected_tools:
            tools_matched = sum(1 for tool in expected_tools if tool in tools_called)
            results["tools_used_correctly"] = (
                tools_matched / len(expected_tools) >= 0.5
            )
        else:
            results["tools_used_correctly"] = len(tools_called) > 0

    # Check conversation_natural
    if "conversation_natural" in success_criteria:
        score = calculate_conversation_score(conversation)
        results["conversation_natural"] = score >= 0.6

    return results


# ===== AGENT PERFORMANCE COMPARISON =====

def calculate_agent_performance(
    agent_name: str,
    results: List[Dict[str, Any]]
) -> AgentPerformanceMetrics:
    """
    Calculate performance metrics for a specific agent.

    Args:
        agent_name: Name of the agent to analyze
        results: List of scenario results

    Returns:
        AgentPerformanceMetrics object
    """
    # Filter results for this agent
    agent_results = [
        r for r in results
        if agent_name in r.get("agents_used", [])
    ]

    if not agent_results:
        return AgentPerformanceMetrics(
            agent_name=agent_name,
            total_invocations=0,
            success_rate=0.0,
            avg_conversation_score=0.0,
            avg_response_time=0.0,
            total_tokens_used=0,
            tools_called={},
            common_errors=[]
        )

    total = len(agent_results)
    successful = sum(1 for r in agent_results if r.get("success_achieved"))

    avg_score = sum(
        r.get("metrics", {}).get("conversation_score", 0.0)
        for r in agent_results
    ) / total

    avg_time = sum(
        r.get("duration_seconds", 0.0)
        for r in agent_results
    ) / total

    total_tokens = sum(
        r.get("metrics", {}).get("total_tokens_estimate", 0)
        for r in agent_results
    )

    # Aggregate tool usage
    all_tools = []
    for r in agent_results:
        all_tools.extend(r.get("tools_called", []))

    tools_freq = dict(Counter(all_tools))

    # Collect errors
    all_errors = []
    for r in agent_results:
        all_errors.extend(r.get("errors", []))

    common_errors = [
        error for error, _ in Counter(all_errors).most_common(5)
    ]

    return AgentPerformanceMetrics(
        agent_name=agent_name,
        total_invocations=total,
        success_rate=successful / total,
        avg_conversation_score=avg_score,
        avg_response_time=avg_time,
        total_tokens_used=int(total_tokens),
        tools_called=tools_freq,
        common_errors=common_errors
    )


def compare_agent_performance(
    results: List[Dict[str, Any]]
) -> Dict[str, AgentPerformanceMetrics]:
    """
    Compare performance across all agents.

    Args:
        results: List of scenario results

    Returns:
        Dictionary mapping agent names to their performance metrics
    """
    # Find all unique agents
    all_agents = set()
    for result in results:
        all_agents.update(result.get("agents_used", []))

    # Calculate metrics for each agent
    agent_metrics = {}
    for agent in all_agents:
        agent_metrics[agent] = calculate_agent_performance(agent, results)

    return agent_metrics


# ===== DASHBOARD DATA GENERATION =====

def generate_dashboard_data(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate comprehensive metrics data for dashboard visualization.

    Args:
        results: List of scenario results from evaluation

    Returns:
        Dictionary with all metrics formatted for dashboard display
    """
    if not results:
        return {
            "summary": {},
            "conversation_metrics": {},
            "tool_metrics": {},
            "latency_metrics": {},
            "token_metrics": {},
            "agent_performance": {},
            "success_metrics": {}
        }

    # Overall summary
    total = len(results)
    passed = sum(1 for r in results if r.get("success_achieved"))

    summary = {
        "total_scenarios": total,
        "passed": passed,
        "failed": total - passed,
        "success_rate": round(passed / total, 3) if total > 0 else 0.0,
        "timestamp": datetime.now().isoformat()
    }

    # Aggregate conversation metrics
    all_conversations = [r.get("conversation_history", []) for r in results]
    conv_scores = [
        calculate_conversation_score(conv) for conv in all_conversations
    ]

    conversation_metrics = {
        "average_score": round(sum(conv_scores) / len(conv_scores), 3) if conv_scores else 0.0,
        "min_score": round(min(conv_scores), 3) if conv_scores else 0.0,
        "max_score": round(max(conv_scores), 3) if conv_scores else 0.0,
        "score_distribution": conv_scores
    }

    # Aggregate tool metrics
    all_tools = []
    for r in results:
        all_tools.extend(r.get("tools_called", []))

    tool_metrics = track_tool_usage(all_tools)

    # Aggregate latency metrics
    durations = [r.get("duration_seconds", 0.0) for r in results]
    latency_metrics = {
        "avg_duration": round(sum(durations) / len(durations), 2) if durations else 0.0,
        "min_duration": round(min(durations), 2) if durations else 0.0,
        "max_duration": round(max(durations), 2) if durations else 0.0,
        "total_duration": round(sum(durations), 2)
    }

    # Aggregate token metrics
    token_estimates = [
        r.get("metrics", {}).get("total_tokens_estimate", 0)
        for r in results
    ]
    token_metrics = {
        "total_tokens": int(sum(token_estimates)),
        "avg_tokens_per_scenario": round(sum(token_estimates) / len(token_estimates), 1) if token_estimates else 0.0,
        "estimated_cost": round(sum(token_estimates) / 1_000_000 * 0.15, 4)  # Rough estimate
    }

    # Agent performance comparison
    agent_performance = compare_agent_performance(results)
    agent_performance_dict = {
        name: metrics.to_dict()
        for name, metrics in agent_performance.items()
    }

    # Success criteria aggregate
    all_criteria = defaultdict(int)
    for r in results:
        for criterion, met in r.get("success_criteria_met", {}).items():
            if met:
                all_criteria[criterion] += 1

    success_metrics = {
        "criteria_met_counts": dict(all_criteria),
        "criteria_success_rates": {
            criterion: round(count / total, 3)
            for criterion, count in all_criteria.items()
        }
    }

    return {
        "summary": summary,
        "conversation_metrics": conversation_metrics,
        "tool_metrics": tool_metrics,
        "latency_metrics": latency_metrics,
        "token_metrics": token_metrics,
        "agent_performance": agent_performance_dict,
        "success_metrics": success_metrics
    }


def export_dashboard_data(results: List[Dict[str, Any]], filepath: str) -> None:
    """Export dashboard metrics to JSON file."""
    dashboard_data = generate_dashboard_data(results)

    with open(filepath, 'w') as f:
        json.dump(dashboard_data, f, indent=2)

    print(f"\nDashboard data exported to: {filepath}")


if __name__ == "__main__":
    """Demo: Show metrics calculation examples."""
    print("\n" + "="*80)
    print("BSW SCHEDULING AGENT - METRICS SYSTEM")
    print("="*80 + "\n")

    # Example conversation
    example_conversation = [
        {
            "role": "user",
            "content": "I need to schedule an appointment with Dr. Martinez for my knee surgery follow-up.",
            "timestamp": time.time()
        },
        {
            "role": "assistant",
            "content": "I'd be happy to help you schedule your follow-up appointment with Dr. Robert Martinez. I can see you had knee replacement surgery two weeks ago. Let me check his availability for you.",
            "agent": "Orthopedic Agent",
            "tools_used": ["check_provider_availability", "search_appointment_slots"],
            "timestamp": time.time() + 2.5
        },
        {
            "role": "user",
            "content": "Great, I'm flexible on times.",
            "timestamp": time.time() + 5.0
        },
        {
            "role": "assistant",
            "content": "Perfect! Dr. Martinez has availability this Thursday at 10:00 AM or Friday at 2:30 PM. Both appointments are at the Plano location. Which works better for you?",
            "agent": "Orthopedic Agent",
            "tools_used": [],
            "timestamp": time.time() + 7.2
        }
    ]

    # Calculate metrics
    print("CONVERSATION QUALITY METRICS:")
    conv_metrics = get_detailed_conversation_metrics(example_conversation)
    print(f"  Overall Score: {conv_metrics.overall_score:.3f}")
    print(f"  Relevance: {conv_metrics.relevance_score:.3f}")
    print(f"  Helpfulness: {conv_metrics.helpfulness_score:.3f}")
    print(f"  Accuracy: {conv_metrics.accuracy_score:.3f}")
    print(f"  Naturalness: {conv_metrics.naturalness_score:.3f}")
    print(f"  Total Turns: {conv_metrics.total_turns}")

    print("\nTOOL USAGE METRICS:")
    tools = ["check_provider_availability", "search_appointment_slots", "book_appointment"]
    tool_metrics = track_tool_usage(tools)
    print(f"  Total Calls: {tool_metrics['total_calls']}")
    print(f"  Unique Tools: {tool_metrics['unique_tools']}")
    print(f"  Most Used: {tool_metrics['most_used']}")
    print(f"  Frequency: {tool_metrics['tool_frequency']}")

    print("\nLATENCY METRICS:")
    latency = measure_latency(time.time(), time.time() + 7.5)
    print(f"  Total Latency: {latency:.2f}s")

    print("\nTOKEN METRICS:")
    token_metrics = calculate_token_metrics(example_conversation, success=True)
    print(f"  Total Tokens: {token_metrics.total_tokens}")
    print(f"  Estimated Cost: ${token_metrics.estimated_cost:.4f}")
    print(f"  Tokens per Turn: {token_metrics.tokens_per_turn:.1f}")

    print("\n" + "="*80 + "\n")
