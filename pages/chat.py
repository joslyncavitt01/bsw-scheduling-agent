"""
Chat Interface - Main conversation page for BSW Scheduling Agent.

This page provides an interactive chat interface where patients can converse
with the AI scheduling assistant to book appointments. Features include:
- Multi-agent routing (Router -> Specialty agents)
- Real-time tool usage tracking
- Patient quick-select dropdown
- Conversation history management
- Session state persistence
"""

import streamlit as st
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import agent and tool modules
try:
    from agents.router import route_patient
    from tools import execute_tool, TOOLS_DEFINITIONS
    from mock_data import PATIENTS, get_patient_by_id
    from openai import OpenAI
    from prompts import (
        ORTHOPEDIC_AGENT_PROMPT,
        CARDIOLOGY_AGENT_PROMPT,
        PRIMARY_CARE_AGENT_PROMPT
    )
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Chat - BSW Scheduling Agent",
    page_icon="",
    layout="wide"
)

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    """Initialize and cache OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

client = get_openai_client()

# Check if patient is logged in
if "logged_in_patient" not in st.session_state or st.session_state.logged_in_patient is None:
    st.warning("Please login first to access the scheduling assistant.")
    st.markdown("### Patient Login Required")
    st.info("You need to select a patient profile before you can schedule appointments.")

    if st.button("Go to Login Page", type="primary"):
        st.switch_page("pages/login.py")

    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_agent" not in st.session_state:
    st.session_state.current_agent = "router"

if "tools_used" not in st.session_state:
    st.session_state.tools_used = []

if "conversation_start_time" not in st.session_state:
    st.session_state.conversation_start_time = None

# Set the selected patient from logged-in patient
st.session_state.selected_patient = st.session_state.logged_in_patient

# Helper functions
def get_agent_prompt(agent_name: str) -> str:
    """Get the system prompt for a specific agent."""
    agent_prompts = {
        "orthopedic": ORTHOPEDIC_AGENT_PROMPT,
        "cardiology": CARDIOLOGY_AGENT_PROMPT,
        "primary_care": PRIMARY_CARE_AGENT_PROMPT
    }
    return agent_prompts.get(agent_name, "You are a helpful healthcare scheduling assistant.")

def call_agent(messages: List[Dict], agent_name: str, use_tools: bool = True) -> Dict[str, Any]:
    """
    Call the LLM with agent-specific prompt and optional tool use.

    Args:
        messages: Conversation history
        agent_name: Name of agent (orthopedic, cardiology, primary_care)
        use_tools: Whether to enable function calling

    Returns:
        Dict with response content and tool calls
    """
    if not client:
        return {
            "content": "Error: OpenAI API key not configured. Please set OPENAI_API_KEY in .env file.",
            "tool_calls": []
        }

    # Build messages with system prompt
    system_prompt = get_agent_prompt(agent_name)
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        # Call OpenAI API
        if use_tools:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=full_messages,
                tools=TOOLS_DEFINITIONS,
                temperature=0.7,
                max_tokens=1000
            )
        else:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=full_messages,
                temperature=0.7,
                max_tokens=1000
            )

        message = response.choices[0].message

        # Extract tool calls if any
        tool_calls = []
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append({
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                })

        return {
            "content": message.content or "",
            "tool_calls": tool_calls
        }

    except Exception as e:
        return {
            "content": f"Error calling agent: {str(e)}",
            "tool_calls": []
        }

def execute_tool_calls(tool_calls: List[Dict]) -> List[Dict[str, Any]]:
    """Execute tool calls and return results."""
    results = []

    for tool_call in tool_calls:
        tool_name = tool_call["name"]

        # Parse arguments
        import json
        try:
            arguments = json.loads(tool_call["arguments"])
        except:
            arguments = {}

        # Execute tool
        result = execute_tool(tool_name, arguments)

        # Track tool usage
        st.session_state.tools_used.append(tool_name)

        results.append({
            "tool_call_id": tool_call["id"],
            "tool_name": tool_name,
            "result": result
        })

    return results

def format_agent_name(agent: str) -> str:
    """Format agent name for display."""
    names = {
        "router": "Router Agent",
        "orthopedic": "Orthopedic Specialist",
        "cardiology": "Cardiology Specialist",
        "primary_care": "Primary Care Specialist"
    }
    return names.get(agent, agent.title())

# Page header
st.markdown("""
<div style="background: linear-gradient(135deg, #00447c 0%, #00a4e4 100%);
            padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;"> Chat with AI Scheduling Assistant</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
        Schedule appointments with our intelligent multi-agent system
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Current Session")

    # Display logged-in patient info
    patient = st.session_state.logged_in_patient
    st.markdown("#### Logged in as:")
    st.success(f"**{patient.first_name} {patient.last_name}**")

    # Quick reference for demo - show DOB prominently for identity verification
    st.info(f"**Your DOB**: {patient.date_of_birth}")
    st.caption("(You'll need this for identity verification)")

    with st.expander("Full Patient Details", expanded=False):
        st.markdown(f"""
        **ID**: {patient.patient_id}
        **Date of Birth**: {patient.date_of_birth}
        **Age**: {patient.age}
        **Location**: {patient.city}, {patient.state} {patient.zip_code}
        **Address**: {patient.address}
        **Insurance**: {patient.insurance_provider}
        **Conditions**: {', '.join(patient.medical_conditions) if patient.medical_conditions else 'None'}
        """)

    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in_patient = None
        st.session_state.messages = []
        st.session_state.current_agent = "router"
        st.switch_page("pages/login.py")

    st.markdown("---")

    # Current agent display
    st.markdown("#### Active Agent")
    agent_display = format_agent_name(st.session_state.current_agent)
    st.info(f"🤖 {agent_display}")

    st.markdown("---")

    # Tools used
    st.markdown("#### Tools Used This Session")
    if st.session_state.tools_used:
        tool_counts = {}
        for tool in st.session_state.tools_used:
            tool_counts[tool] = tool_counts.get(tool, 0) + 1

        for tool, count in tool_counts.items():
            st.markdown(f"- `{tool}` ({count}x)")
    else:
        st.markdown("_No tools used yet_")

    st.markdown("---")

    # Session controls
    st.markdown("#### Session Controls")

    if st.button(" Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_agent = "router"
        st.session_state.tools_used = []
        st.session_state.conversation_start_time = None
        st.rerun()

    if st.session_state.messages:
        conversation_duration = ""
        if st.session_state.conversation_start_time:
            duration = int(time.time() - st.session_state.conversation_start_time)
            mins, secs = divmod(duration, 60)
            conversation_duration = f"{mins}m {secs}s"

        st.markdown(f"""
        **Messages**: {len(st.session_state.messages)}
        **Duration**: {conversation_duration}
        """)

    st.markdown("---")

    # Help
    st.markdown("####  Demo Scenarios")

    with st.expander("Orthopedic Follow-up"):
        st.markdown("""
        **Patient**: PT001 - Sarah Martinez
        **Try**: "I had knee replacement surgery 2 weeks ago and need my follow-up appointment."
        """)

    with st.expander("Cardiology Consultation"):
        st.markdown("""
        **Patient**: PT002 - James Wilson
        **Try**: "I've been having chest pain and need to see a cardiologist."
        """)

    with st.expander("Annual Physical"):
        st.markdown("""
        **Patient**: PT004 - Michael Thompson
        **Try**: "I need to schedule my annual physical exam."
        """)

# Main chat area
st.markdown("### Conversation")

# Display chat messages
for message in st.session_state.messages:
    role = message["role"]
    # Use display_content if available (for user messages with patient context)
    content = message.get("display_content", message["content"])

    if role == "user":
        with st.chat_message("user"):
            st.markdown(content)

    elif role == "assistant":
        with st.chat_message("assistant"):
            st.markdown(content)

            # Show tool usage if any
            if message.get("tools_used"):
                with st.expander(" Tools Used"):
                    for tool in message["tools_used"]:
                        st.code(tool, language="text")

# Chat input
if prompt := st.chat_input("Type your message here..."):

    # Start conversation timer
    if not st.session_state.conversation_start_time:
        st.session_state.conversation_start_time = time.time()

    # Add patient context if selected
    enhanced_prompt = prompt
    if st.session_state.selected_patient:
        patient = st.session_state.selected_patient
        # Add patient context to the message (patient will provide name and DOB for verification)
        enhanced_prompt = f"[System: Patient ID {patient.patient_id} is logged in] {prompt}"

    # Add user message (store original prompt for display, but use enhanced_prompt for agent)
    st.session_state.messages.append({
        "role": "user",
        "content": enhanced_prompt,  # Changed from prompt to enhanced_prompt
        "display_content": prompt,  # Store original for display purposes
        "timestamp": time.time()
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Determine routing (if on router agent)
    if st.session_state.current_agent == "router":
        with st.spinner("Routing to appropriate specialist..."):
            routing_result = route_patient(
                enhanced_prompt,
                conversation_history=st.session_state.messages[-5:]
            )

            if routing_result.get("success") and routing_result["agent"] != "unclear":
                st.session_state.current_agent = routing_result["agent"]
    # If already with a specialist - no routing needed, proceed directly to agent

    # Call appropriate agent
    current_agent = st.session_state.current_agent

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        with st.spinner(f"{format_agent_name(current_agent)} is thinking..."):
            # Call agent
            response = call_agent(
                st.session_state.messages,
                current_agent,
                use_tools=True
            )

            response_content = response["content"]
            tool_calls = response["tool_calls"]

            # Execute tools if needed
            tools_used_in_turn = []
            if tool_calls:
                with st.spinner("Using tools..."):
                    tool_results = execute_tool_calls(tool_calls)
                    tools_used_in_turn = [t["tool_name"] for t in tool_results]

                    # Format tool results for context
                    tool_context = "\n\n".join([
                        f"Tool: {r['tool_name']}\nResult: {r['result']}"
                        for r in tool_results
                    ])

                    # Get follow-up response with tool results
                    followup_messages = st.session_state.messages + [
                        {"role": "assistant", "content": response_content or ""},
                        {"role": "system", "content": f"Tool Results:\n{tool_context}"}
                    ]

                    followup_response = call_agent(
                        followup_messages,
                        current_agent,
                        use_tools=False
                    )

                    response_content = followup_response["content"]

            # Display response
            message_placeholder.markdown(response_content)

            # Show tools used
            if tools_used_in_turn:
                with st.expander(" Tools Used"):
                    for tool in tools_used_in_turn:
                        st.code(tool, language="text")

        # Add assistant message to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_content,
            "agent": current_agent,
            "tools_used": tools_used_in_turn,
            "timestamp": time.time()
        })

# Empty state
if not st.session_state.messages:
    st.info("""
     **Welcome to BSW Health AI Scheduling!**

    Start a conversation by typing a message below, or select a demo patient from the sidebar
    and try one of the example scenarios.

    The Router Agent will analyze your request and direct you to the appropriate specialist:
    - **Orthopedic Agent**: Joint pain, sports injuries, post-op follow-ups
    - **Cardiology Agent**: Heart conditions, chest pain, cardiac procedures
    - **Primary Care Agent**: Wellness visits, preventive care, general health
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
    <p>BSW Health AI Scheduling Agent Demo | Powered by GPT-4o-mini</p>
    <p style="font-size: 0.8rem;">This is a demonstration system using mock data only.</p>
</div>
""", unsafe_allow_html=True)
