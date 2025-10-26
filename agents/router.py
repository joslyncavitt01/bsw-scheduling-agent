"""
Router Agent - Intelligent Patient Intent Classification and Routing

This module implements the router agent that analyzes patient messages and routes
them to the appropriate specialty agent (orthopedic, cardiology, or primary care).

The router uses GPT-4o-mini with the ROUTER_AGENT_PROMPT to understand patient
intent and select the best specialty agent for their needs.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from openai import OpenAI

# Import prompts and RAG system
try:
    from prompts import ROUTER_AGENT_PROMPT
    from rag import retrieve_policies
except ImportError:
    # Fallback for testing
    ROUTER_AGENT_PROMPT = "You are a routing agent for a healthcare scheduling system."
    def retrieve_policies(query: str, n_results: int = 3) -> List[Dict]:
        return []

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Routing statistics (for analytics)
ROUTING_STATS = {
    "total_routes": 0,
    "routes_by_agent": {
        "orthopedic": 0,
        "cardiology": 0,
        "primary_care": 0,
        "unclear": 0
    },
    "average_confidence": 0.0,
    "last_reset": datetime.now().isoformat()
}


def route_patient(
    user_message: str,
    conversation_history: Optional[List[Dict]] = None,
    use_rag: bool = True
) -> Dict[str, Any]:
    """
    Route patient to appropriate specialty agent based on their message.

    This function uses GPT-4o-mini with the ROUTER_AGENT_PROMPT to analyze
    the patient's message and determine which specialty agent should handle
    their request.

    Args:
        user_message: The patient's current message
        conversation_history: Optional list of previous conversation messages
                            Format: [{"role": "user/assistant", "content": "..."}]
        use_rag: Whether to retrieve relevant policies from RAG system

    Returns:
        Dictionary containing:
            - agent: "orthopedic" | "cardiology" | "primary_care" | "unclear"
            - confidence: "high" | "medium" | "low"
            - reasoning: Explanation of routing decision
            - keywords_detected: List of relevant keywords found
            - rag_context_used: Whether RAG context was included
            - success: Boolean indicating if routing was successful
            - timestamp: ISO timestamp of routing decision

    Example:
        >>> result = route_patient("I need a knee replacement follow-up")
        >>> print(result['agent'])
        'orthopedic'
    """
    try:
        # Build conversation context
        messages = []

        # Add system prompt
        system_prompt = ROUTER_AGENT_PROMPT

        # Optionally add RAG context
        rag_context_used = False
        if use_rag and user_message:
            try:
                rag_results = retrieve_policies(user_message, n_results=2)
                if rag_results:
                    rag_context = "\n\n".join([
                        f"Policy: {r['metadata'].get('title', 'Unknown')}\n{r['content'][:300]}..."
                        for r in rag_results
                    ])
                    system_prompt += f"\n\nRELEVANT POLICIES:\n{rag_context}"
                    rag_context_used = True
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")

        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Last 5 messages for context

        # Add current message
        messages.append({"role": "user", "content": user_message})

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,  # Lower temperature for consistent routing
            max_tokens=300
        )

        # Parse response
        routing_response = response.choices[0].message.content.strip()

        # Extract routing decision (look for agent name in response)
        agent = "unclear"
        confidence = "medium"

        routing_lower = routing_response.lower()

        # Detect agent
        if "orthopedic" in routing_lower:
            agent = "orthopedic"
        elif "cardiology" in routing_lower or "cardiac" in routing_lower:
            agent = "cardiology"
        elif "primary" in routing_lower or "primary care" in routing_lower:
            agent = "primary_care"

        # Detect confidence
        if "high confidence" in routing_lower or "clearly" in routing_lower:
            confidence = "high"
        elif "low confidence" in routing_lower or "unclear" in routing_lower or "uncertain" in routing_lower:
            confidence = "low"

        # Extract keywords
        keywords = []
        orthopedic_keywords = ["knee", "hip", "joint", "bone", "fracture", "orthopedic",
                              "sports injury", "arthritis", "surgery", "replacement"]
        cardiology_keywords = ["heart", "chest pain", "cardiology", "cardiac", "afib",
                              "a-fib", "stress test", "pacemaker", "stent"]
        primary_keywords = ["physical", "wellness", "checkup", "annual", "preventive",
                           "diabetes", "hypertension", "blood pressure"]

        message_lower = user_message.lower()
        for keyword in orthopedic_keywords + cardiology_keywords + primary_keywords:
            if keyword in message_lower:
                keywords.append(keyword)

        # Update statistics
        ROUTING_STATS["total_routes"] += 1
        ROUTING_STATS["routes_by_agent"][agent] += 1

        # Return routing decision
        return {
            "success": True,
            "agent": agent,
            "confidence": confidence,
            "reasoning": routing_response,
            "keywords_detected": keywords,
            "rag_context_used": rag_context_used,
            "timestamp": datetime.now().isoformat(),
            "tokens_used": response.usage.total_tokens
        }

    except Exception as e:
        logger.error(f"Routing error: {e}")
        return {
            "success": False,
            "agent": "unclear",
            "confidence": "low",
            "reasoning": "Error during routing",
            "error": str(e),
            "keywords_detected": [],
            "rag_context_used": False,
            "timestamp": datetime.now().isoformat()
        }


def route_with_fallback(
    user_message: str,
    conversation_history: Optional[List[Dict]] = None,
    default_agent: str = "primary_care"
) -> Dict[str, Any]:
    """
    Route patient with fallback to default agent if routing is unclear.

    Args:
        user_message: Patient's message
        conversation_history: Optional conversation history
        default_agent: Agent to use if routing is unclear (default: "primary_care")

    Returns:
        Routing result with guaranteed agent assignment
    """
    result = route_patient(user_message, conversation_history)

    if result["agent"] == "unclear" or result["confidence"] == "low":
        result["agent"] = default_agent
        result["reasoning"] += f"\n\nFallback: Routing to {default_agent} for general assistance."
        result["fallback_used"] = True
    else:
        result["fallback_used"] = False

    return result


def batch_route(messages: List[str]) -> List[Dict[str, Any]]:
    """
    Route multiple messages in batch (useful for testing/evaluation).

    Args:
        messages: List of patient messages to route

    Returns:
        List of routing results
    """
    results = []
    for message in messages:
        result = route_patient(message)
        results.append(result)

    return results


def get_routing_statistics() -> Dict[str, Any]:
    """
    Get routing statistics for analytics.

    Returns:
        Dictionary with routing statistics including:
            - total_routes
            - routes_by_agent
            - average_confidence
            - last_reset
    """
    # Calculate average confidence
    total = ROUTING_STATS["total_routes"]
    if total > 0:
        # This is simplified - in production you'd track actual confidence scores
        ROUTING_STATS["average_confidence"] = 0.8  # Placeholder

    return ROUTING_STATS.copy()


def reset_routing_statistics():
    """Reset routing statistics (useful for testing)."""
    global ROUTING_STATS
    ROUTING_STATS = {
        "total_routes": 0,
        "routes_by_agent": {
            "orthopedic": 0,
            "cardiology": 0,
            "primary_care": 0,
            "unclear": 0
        },
        "average_confidence": 0.0,
        "last_reset": datetime.now().isoformat()
    }


# Export public functions
__all__ = [
    "route_patient",
    "route_with_fallback",
    "batch_route",
    "get_routing_statistics",
    "reset_routing_statistics"
]


if __name__ == "__main__":
    """Test the router agent with various scenarios."""
    print("=" * 80)
    print("Router Agent Test Suite")
    print("=" * 80)
    print()

    # Test messages covering different specialties
    test_messages = [
        "I need to schedule a follow-up for my knee replacement surgery",
        "I've been having chest pain and need to see a cardiologist",
        "I'd like to book my annual physical exam",
        "My hip has been hurting after my surgery last month",
        "I need a stress test for my heart condition",
        "Can I schedule a wellness visit for a general checkup?",
        "I'm having trouble breathing and my heart is racing",
        "I sprained my ankle playing basketball last week",
    ]

    print("Testing routing for various patient messages:\n")

    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: \"{message}\"")
        result = route_patient(message)

        print(f"  → Agent: {result['agent']}")
        print(f"  → Confidence: {result['confidence']}")
        print(f"  → Keywords: {', '.join(result['keywords_detected'][:3])}")
        print(f"  → Success: {'✓' if result['success'] else '✗'}")
        print()

    # Display statistics
    print("=" * 80)
    print("Routing Statistics")
    print("=" * 80)
    stats = get_routing_statistics()
    print(f"Total Routes: {stats['total_routes']}")
    print(f"Routes by Agent:")
    for agent, count in stats['routes_by_agent'].items():
        print(f"  - {agent}: {count}")
    print()

    print("Router Agent Ready! ✓")
