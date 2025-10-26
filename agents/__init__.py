"""
BSW Scheduling Agent System - Multi-Agent Orchestration

This module provides the complete agent system for Baylor Scott & White Health's
AI-powered appointment scheduling system.

Agents:
    - Router Agent: Intelligent routing to specialty agents
    - Orthopedic Agent: Bone, joint, and orthopedic surgery scheduling
    - Cardiology Agent: Heart and cardiovascular care scheduling
    - Primary Care Agent: Wellness, preventive care, and general health (optional)

Key Features:
    - Multi-agent orchestration with intelligent routing
    - OpenAI function calling for tool execution
    - RAG integration for policy and protocol retrieval
    - Production-quality error handling and logging
    - Comprehensive metrics and analytics

Usage Example:
    ```python
    from agents import route_patient, handle_orthopedic_request, handle_cardiology_request

    # Route patient to appropriate agent
    routing = route_patient("I need to schedule a knee replacement follow-up")
    agent = routing['agent']

    # Handle with specialty agent
    if agent == 'orthopedic':
        result = handle_orthopedic_request(
            "I need my 2-week post-op appointment",
            conversation_history=[]
        )
        print(result['response'])
    ```
"""

# Import router agent functions
from .router import (
    route_patient,
    route_with_fallback,
    batch_route,
    get_routing_statistics
)

# Import orthopedic agent functions
from .orthopedic_agent import (
    handle_orthopedic_request,
    handle_orthopedic_conversation,
    get_orthopedic_metrics
)

# Import cardiology agent functions
from .cardiology_agent import (
    handle_cardiology_request,
    handle_cardiology_conversation,
    assess_cardiac_urgency,
    get_cardiology_metrics
)


__version__ = "1.0.0"
__author__ = "BSW Health AI Team"


# Export all public functions
__all__ = [
    # Router functions
    "route_patient",
    "route_with_fallback",
    "batch_route",
    "get_routing_statistics",

    # Orthopedic agent functions
    "handle_orthopedic_request",
    "handle_orthopedic_conversation",
    "get_orthopedic_metrics",

    # Cardiology agent functions
    "handle_cardiology_request",
    "handle_cardiology_conversation",
    "assess_cardiac_urgency",
    "get_cardiology_metrics",
]


# Convenience mapping for agent execution
AGENT_HANDLERS = {
    "orthopedic": handle_orthopedic_request,
    "cardiology": handle_cardiology_request,
    "primary_care": None  # Could be implemented in the future
}


def execute_agent(agent_name: str, user_message: str, conversation_history=None):
    """
    Convenience function to execute an agent by name.

    Args:
        agent_name: Name of agent ("orthopedic", "cardiology", "primary_care")
        user_message: User's message
        conversation_history: Optional conversation history

    Returns:
        Agent execution result

    Raises:
        ValueError: If agent name is invalid or not implemented
    """
    if agent_name not in AGENT_HANDLERS:
        raise ValueError(f"Invalid agent name: {agent_name}. Valid options: {list(AGENT_HANDLERS.keys())}")

    handler = AGENT_HANDLERS[agent_name]
    if handler is None:
        raise ValueError(f"Agent '{agent_name}' is not yet implemented")

    return handler(user_message, conversation_history)


def route_and_execute(user_message: str, conversation_history=None):
    """
    Complete end-to-end: route and execute appropriate agent.

    This is a convenience function that combines routing and execution in one call.

    Args:
        user_message: User's message
        conversation_history: Optional conversation history

    Returns:
        Dictionary containing:
            - routing: Routing decision
            - agent_result: Agent execution result
            - success: Overall success status
    """
    # Route the request
    routing = route_patient(user_message, conversation_history)

    if not routing.get('success'):
        return {
            "success": False,
            "routing": routing,
            "agent_result": None,
            "error": routing.get('error', 'Routing failed')
        }

    agent_name = routing['agent']

    # Execute the appropriate agent
    try:
        agent_result = execute_agent(agent_name, user_message, conversation_history)

        return {
            "success": True,
            "routing": routing,
            "agent_result": agent_result,
            "agent": agent_name
        }
    except Exception as e:
        return {
            "success": False,
            "routing": routing,
            "agent_result": None,
            "error": f"Agent execution failed: {str(e)}"
        }


# Module metadata
AGENT_INFO = {
    "orthopedic": {
        "name": "Orthopedic Specialist Agent",
        "description": "Handles appointment scheduling for orthopedic surgery including joint replacements, sports injuries, and post-operative care",
        "specialties": ["Joint Replacement", "Sports Medicine", "Foot and Ankle", "Spine Surgery"],
        "handler": handle_orthopedic_request
    },
    "cardiology": {
        "name": "Cardiology Specialist Agent",
        "description": "Handles appointment scheduling for cardiology including heart conditions, chest pain evaluation, and cardiac procedures",
        "specialties": ["General Cardiology", "Interventional Cardiology", "Electrophysiology", "Heart Failure"],
        "handler": handle_cardiology_request
    },
    "primary_care": {
        "name": "Primary Care Agent",
        "description": "Handles appointment scheduling for preventive care, wellness visits, and general health concerns",
        "specialties": ["Family Medicine", "Internal Medicine", "Geriatric Medicine"],
        "handler": None  # Not yet implemented
    }
}


def get_agent_info(agent_name: str = None):
    """
    Get information about available agents.

    Args:
        agent_name: Optional specific agent name, or None for all agents

    Returns:
        Agent information dictionary
    """
    if agent_name:
        return AGENT_INFO.get(agent_name, {"error": f"Agent '{agent_name}' not found"})
    return AGENT_INFO


def list_available_agents():
    """
    List all available agent names.

    Returns:
        List of agent names
    """
    return [name for name, info in AGENT_INFO.items() if info['handler'] is not None]


# Version information
def get_version():
    """Get the version of the agents module."""
    return __version__


if __name__ == "__main__":
    """
    Test the agent system with a complete workflow.
    """
    print("=" * 80)
    print("BSW Scheduling Agent System - Complete Workflow Test")
    print(f"Version: {__version__}")
    print("=" * 80)
    print()

    # Display available agents
    print("Available Agents:")
    for agent_name in list_available_agents():
        info = get_agent_info(agent_name)
        print(f"  - {info['name']}")
        print(f"    Description: {info['description']}")
        print(f"    Specialties: {', '.join(info['specialties'])}")
        print()

    # Test complete workflow
    print("=" * 80)
    print("Testing Complete Workflow: Route and Execute")
    print("=" * 80)
    print()

    test_messages = [
        "I need to schedule a follow-up for my knee replacement surgery. I'm patient PT001.",
        "I've been having chest pain and need to see a cardiologist. I have Medicare insurance."
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: {message}")
        print()

        result = route_and_execute(message)

        print(f"Success: {'' if result.get('success') else ''}")
        if result.get('routing'):
            print(f"Routed to: {result['routing'].get('agent', 'N/A')}")
            print(f"Confidence: {result['routing'].get('confidence', 'N/A')}")

        if result.get('agent_result'):
            print(f"Response: {result['agent_result'].get('response', 'N/A')[:200]}...")
            tools_used = result['agent_result'].get('tools_used', [])
            if tools_used:
                print(f"Tools Used: {', '.join(tools_used)}")

        if result.get('error'):
            print(f"Error: {result['error']}")

        print()
        print("-" * 80)
        print()

    print("=" * 80)
    print("Agent System Ready!")
    print("=" * 80)
