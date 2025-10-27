"""
Cardiology Specialist Agent for BSW Scheduling System.

Handles appointment scheduling for cardiology including:
- General cardiology consultations
- Interventional cardiology
- Electrophysiology (arrhythmias, pacemakers)
- Heart failure management
- Chest pain evaluation
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI

# Import dependencies
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts import CARDIOLOGY_AGENT_PROMPT
from tools import TOOL_DEFINITIONS, execute_tool_call
from rag import retrieve_policies

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_cardiology_request(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Handle cardiology appointment scheduling request.

    Uses OpenAI GPT-4o-mini with function calling to execute tools for:
    - Provider lookup
    - Appointment slot search
    - Insurance verification
    - Referral checking
    - Appointment booking
    - Emergency triage

    Args:
        user_message: Current user message
        conversation_history: Previous conversation messages
                            Format: [{"role": "user|assistant|tool", "content": "..."}]

    Returns:
        Dictionary containing:
            - response: str - Agent's response to user
            - tools_used: List[str] - Names of tools called
            - appointment_details: Dict - Appointment info if booked
            - urgency_level: str - "emergent"|"urgent"|"routine"
            - success: bool - Whether request was handled successfully
            - error: str - Error message if failed
            - tokens_used: Dict - Token usage metrics
    """
    try:
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment")
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "response": "I apologize, but I'm having trouble connecting to my scheduling system. Please contact our office directly at 1-800-BSW-HEALTH."
            }

        client = OpenAI(api_key=api_key)

        # Retrieve relevant clinical protocols for cardiology
        rag_context = ""
        try:
            policies = retrieve_policies(f"cardiology {user_message}", n_results=2)
            if policies:
                rag_context = "\n\n---RELEVANT PROTOCOLS & POLICIES---\n"
                for policy in policies:
                    rag_context += f"\n{policy['metadata'].get('title', 'Policy')}\n"
                    rag_context += f"{policy['content'][:400]}...\n"
                logger.info(f"Retrieved {len(policies)} relevant cardiology protocols")
        except Exception as e:
            logger.warning(f"Error retrieving RAG context: {str(e)}")

        # Build conversation context
        if conversation_history is None:
            conversation_history = []

        # Create messages for OpenAI API
        messages = [
            {"role": "system", "content": CARDIOLOGY_AGENT_PROMPT + rag_context}
        ]

        # Add conversation history
        for msg in conversation_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # Handle tool messages from previous calls
            if role == "tool":
                messages.append({
                    "role": "tool",
                    "tool_call_id": msg.get("tool_call_id", "unknown"),
                    "content": content
                })
            else:
                messages.append({
                    "role": role,
                    "content": content
                })

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        logger.info(f"Processing cardiology request: '{user_message[:100]}...'")

        # Track tools used, appointment details, and urgency
        tools_used = []
        appointment_details = None
        urgency_level = "routine"  # Default
        total_tokens = {"prompt": 0, "completion": 0, "total": 0}

        # Check for emergency keywords in user message
        emergency_keywords = [
            "chest pain", "severe pain", "heart attack", "can't breathe",
            "shortness of breath", "passing out", "unconscious", "crushing pain",
            "radiating pain", "sweating", "nausea and chest pain"
        ]

        message_lower = user_message.lower()
        if any(keyword in message_lower for keyword in emergency_keywords):
            urgency_level = "emergent"
            logger.warning(f"EMERGENCY KEYWORDS DETECTED: {user_message[:100]}")

        # Iterative function calling loop (max 10 iterations)
        max_iterations = 10
        for iteration in range(max_iterations):
            # Call OpenAI API with function calling (parallel enabled)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                parallel_tool_calls=True,  # Enable parallel function calling
                temperature=0.7,
                max_tokens=1000
            )

            # Track token usage
            total_tokens["prompt"] += response.usage.prompt_tokens
            total_tokens["completion"] += response.usage.completion_tokens
            total_tokens["total"] += response.usage.total_tokens

            assistant_message = response.choices[0].message

            # Check if we're done (no tool calls)
            if not assistant_message.tool_calls:
                # Final response
                final_response = assistant_message.content

                # If emergency detected, prepend warning
                if urgency_level == "emergent" and "911" not in final_response and "emergency" not in final_response.lower():
                    final_response = "=� IMPORTANT: If you are experiencing severe chest pain or cardiac symptoms, please call 911 or go to the nearest emergency room immediately. Do not wait for an appointment.\n\n" + final_response

                result = {
                    "success": True,
                    "response": final_response,
                    "tools_used": tools_used,
                    "appointment_details": appointment_details,
                    "urgency_level": urgency_level,
                    "model_used": "gpt-4o-mini",
                    "tokens_used": total_tokens,
                    "iterations": iteration + 1
                }

                logger.info(f"Cardiology request completed in {iteration + 1} iterations")
                logger.info(f"Tools used: {', '.join(tools_used) if tools_used else 'None'}")
                logger.info(f"Urgency level: {urgency_level}")

                return result

            # Process tool calls
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                logger.info(f"Calling tool: {function_name} with args: {function_args}")
                tools_used.append(function_name)

                # Execute the tool
                tool_result = execute_tool_call(function_name, function_args)

                # Track appointment details if booking occurred
                if function_name == "book_appointment" and tool_result.get("success"):
                    appointment_details = tool_result.get("appointment_details", {})

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

        # If we hit max iterations, return what we have
        logger.warning(f"Reached max iterations ({max_iterations})")
        return {
            "success": False,
            "error": "Maximum iteration limit reached",
            "response": "I apologize, but I'm having trouble completing your request. Please call our cardiology office directly for assistance.",
            "tools_used": tools_used,
            "appointment_details": appointment_details,
            "urgency_level": urgency_level,
            "tokens_used": total_tokens
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to parse tool arguments: {str(e)}",
            "response": "I encountered an error processing your request. Please try again or contact our office.",
            "tools_used": [],
            "appointment_details": None,
            "urgency_level": "routine"
        }

    except Exception as e:
        logger.error(f"Error in handle_cardiology_request: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "response": "I apologize for the inconvenience. Please contact our cardiology scheduling line directly at 1-800-BSW-HEALTH.",
            "tools_used": [],
            "appointment_details": None,
            "urgency_level": "routine"
        }


def handle_cardiology_conversation(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    patient_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Handle cardiology request with additional patient context.

    Args:
        user_message: Current user message
        conversation_history: Previous messages
        patient_context: Additional context (patient_id, insurance, symptoms, etc.)

    Returns:
        Response dictionary
    """
    # Enhance user message with patient context if provided
    enhanced_message = user_message
    if patient_context:
        context_str = "\n\nPatient Context:\n"
        if "patient_id" in patient_context:
            context_str += f"- Patient ID: {patient_context['patient_id']}\n"
        if "insurance" in patient_context:
            context_str += f"- Insurance: {patient_context['insurance']}\n"
        if "symptoms" in patient_context:
            context_str += f"- Symptoms: {patient_context['symptoms']}\n"
        if "medical_history" in patient_context:
            context_str += f"- Medical History: {patient_context['medical_history']}\n"

        enhanced_message = f"{user_message}{context_str}"

    return handle_cardiology_request(enhanced_message, conversation_history)


def assess_cardiac_urgency(user_message: str) -> Dict[str, Any]:
    """
    Quick triage assessment of cardiac urgency based on symptoms mentioned.

    Args:
        user_message: Patient's message

    Returns:
        Dictionary with urgency assessment
    """
    message_lower = user_message.lower()

    # Emergency indicators
    emergent_keywords = [
        "chest pain", "severe pain", "crushing pain", "radiating pain",
        "can't breathe", "shortness of breath", "passing out", "unconscious",
        "heart attack", "sweating and pain", "nausea and chest pain"
    ]

    # Urgent indicators
    urgent_keywords = [
        "abnormal", "stress test", "palpitations", "rapid heart",
        "irregular heartbeat", "dizzy", "lightheaded", "recent er visit"
    ]

    # Check for emergency
    if any(keyword in message_lower for keyword in emergent_keywords):
        return {
            "urgency_level": "emergent",
            "recommendation": "CALL 911 IMMEDIATELY - Do not schedule appointment",
            "reasoning": "Potential cardiac emergency detected"
        }

    # Check for urgent
    if any(keyword in message_lower for keyword in urgent_keywords):
        return {
            "urgency_level": "urgent",
            "recommendation": "Schedule within 24-48 hours",
            "reasoning": "Urgent cardiac symptoms or abnormal test results"
        }

    # Default to routine
    return {
        "urgency_level": "routine",
        "recommendation": "Schedule within 1-2 weeks",
        "reasoning": "Routine follow-up or consultation"
    }


def get_cardiology_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate metrics from cardiology agent results.

    Args:
        results: List of agent response dictionaries

    Returns:
        Metrics dictionary
    """
    if not results:
        return {
            "total_requests": 0,
            "success_rate": 0.0,
            "appointment_booking_rate": 0.0,
            "average_tokens": 0,
            "tool_usage": {},
            "urgency_distribution": {}
        }

    total = len(results)
    successful = sum(1 for r in results if r.get("success", False))
    appointments_booked = sum(1 for r in results if r.get("appointment_details") is not None)

    # Tool usage statistics
    tool_usage = {}
    for result in results:
        for tool in result.get("tools_used", []):
            tool_usage[tool] = tool_usage.get(tool, 0) + 1

    # Urgency distribution
    urgency_distribution = {}
    for result in results:
        urgency = result.get("urgency_level", "routine")
        urgency_distribution[urgency] = urgency_distribution.get(urgency, 0) + 1

    # Token usage
    total_tokens = sum(
        result.get("tokens_used", {}).get("total", 0)
        for result in results
    )
    avg_tokens = total_tokens / total if total > 0 else 0

    return {
        "total_requests": total,
        "success_rate": successful / total if total > 0 else 0.0,
        "appointment_booking_rate": appointments_booked / total if total > 0 else 0.0,
        "average_tokens": avg_tokens,
        "total_tokens": total_tokens,
        "tool_usage": tool_usage,
        "appointments_booked": appointments_booked,
        "urgency_distribution": urgency_distribution
    }


if __name__ == "__main__":
    """Test the cardiology agent with sample requests."""

    print("=" * 80)
    print("BSW Cardiology Specialist Agent - Test Suite")
    print("=" * 80)
    print()

    # Test cases
    test_cases = [
        {
            "message": "I need to follow up on my stress test results. My doctor said they were abnormal. Patient ID is PT002.",
            "description": "Urgent stress test follow-up"
        },
        {
            "message": "I'm managing atrial fibrillation and need my 6-month check-up. I'm on warfarin. Patient PT006.",
            "description": "Routine A-fib management"
        },
        {
            "message": "Does Medicare require a referral to see a cardiologist?",
            "description": "Insurance policy question"
        },
        {
            "message": "I have severe chest pain radiating to my left arm",
            "description": "EMERGENCY - should direct to 911"
        }
    ]

    results = []
    for i, test in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test['description']}")
        print(f"Message: {test['message']}")
        print()

        result = handle_cardiology_request(test['message'])
        results.append(result)

        print(f"Success: {'' if result.get('success') else ''}")
        print(f"Urgency Level: {result.get('urgency_level', 'N/A')}")
        print(f"Response: {result.get('response', 'N/A')[:300]}...")
        print(f"Tools Used: {', '.join(result.get('tools_used', [])) if result.get('tools_used') else 'None'}")

        if result.get('appointment_details'):
            print("Appointment Booked:")
            details = result['appointment_details']
            print(f"  - Patient: {details.get('patient', 'N/A')}")
            print(f"  - Provider: {details.get('provider', 'N/A')}")
            print(f"  - Date: {details.get('date', 'N/A')}")
            print(f"  - Time: {details.get('time', 'N/A')}")

        if result.get('tokens_used'):
            print(f"Tokens Used: {result['tokens_used'].get('total', 0)}")

        print()
        print("-" * 80)
        print()

    # Calculate metrics
    print("=" * 80)
    print("Cardiology Agent Metrics:")
    print("=" * 80)
    metrics = get_cardiology_metrics(results)
    print(f"Total Requests: {metrics['total_requests']}")
    print(f"Success Rate: {metrics['success_rate']:.1%}")
    print(f"Appointment Booking Rate: {metrics['appointment_booking_rate']:.1%}")
    print(f"Average Tokens: {metrics['average_tokens']:.1f}")
    print()
    print("Tool Usage:")
    for tool, count in metrics['tool_usage'].items():
        print(f"  {tool}: {count}")
    print()
    print("Urgency Distribution:")
    for urgency, count in metrics['urgency_distribution'].items():
        print(f"  {urgency}: {count}")
    print()
    print("=" * 80)
