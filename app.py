"""
BSW Scheduling Agent - Main Streamlit Application
Multi-page app for AI-powered healthcare appointment scheduling.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from rag import initialize_rag

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="BSW Health - AI Scheduling Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.bswhealth.com',
        'About': "BSW Health AI Scheduling Agent - Demo System"
    }
)

# Custom CSS for healthcare-appropriate styling
st.markdown("""
<style>
    /* Main theme colors - BSW brand colors */
    :root {
        --primary-color: #00447c;
        --secondary-color: #00a4e4;
        --success-color: #00A86B;
        --warning-color: #FFB81C;
        --danger-color: #E31C3D;
        --text-primary: #212529;
        --text-secondary: #6c757d;
        --bg-light: #f8f9fa;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #00447c 0%, #00a4e4 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }

    /* Card styling */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #00a4e4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    .info-card h3 {
        color: #00447c;
        margin-top: 0;
        font-size: 1.3rem;
    }

    .info-card p {
        color: #6c757d;
        margin-bottom: 0;
    }

    /* Feature grid */
    .feature-item {
        background: #f8f9fa;
        padding: 1.25rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
        transition: transform 0.2s;
    }

    .feature-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .feature-title {
        color: #00447c;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }

    .feature-description {
        color: #6c757d;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }

    /* Button styling */
    .stButton > button {
        background-color: #00447c;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        border: none;
        font-weight: 500;
        transition: background-color 0.3s;
    }

    .stButton > button:hover {
        background-color: #00a4e4;
    }

    /* Alert boxes */
    .alert-info {
        background-color: #e7f3ff;
        border-left: 4px solid #00a4e4;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .alert-warning {
        background-color: #fff4e5;
        border-left: 4px solid #FFB81C;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        border-top: 1px solid #e9ecef;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.openai_api_key = os.getenv('OPENAI_API_KEY', '')
    st.session_state.conversation_history = []
    st.session_state.current_agent = 'router'
    st.session_state.rag_initialized = False

# Initialize RAG system if not already done
if not st.session_state.rag_initialized:
    try:
        with st.spinner("Initializing healthcare policy database..."):
            initialize_rag()
            st.session_state.rag_initialized = True
    except Exception as e:
        st.error(f"Error initializing RAG system: {e}")

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/250x80/00447c/ffffff?text=BSW+Health", use_column_width=True)

    st.markdown("---")

    st.markdown("### Navigation")
    st.markdown("""
    - **Home** - Welcome and overview
    - **Chat** - Schedule appointments
    - **Metrics Dashboard** - View analytics
    - **Feedback** - Rate conversations
    """)

    st.markdown("---")

    # API Key Status
    st.markdown("### System Status")
    if st.session_state.openai_api_key:
        st.success("OpenAI API: Connected")
    else:
        st.warning("OpenAI API: Not configured")
        st.markdown("Set `OPENAI_API_KEY` in `.env` file")

    if st.session_state.rag_initialized:
        st.success("RAG System: Ready")
    else:
        st.info("RAG System: Initializing...")

    st.markdown("---")

    # Quick Stats
    st.markdown("### Quick Stats")
    try:
        from evaluation.metrics import get_metrics_tracker
        tracker = get_metrics_tracker()

        total_convs = len(tracker.conversations)
        success_rate = tracker.get_success_rate()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Chats", total_convs)
        with col2:
            st.metric("Success Rate", f"{success_rate:.0%}")
    except:
        st.info("No metrics available yet")

    st.markdown("---")

    # Important Notice
    st.markdown("### Important Notice")
    st.info("""
    **Demo System**

    This is a demonstration system using mock data.
    No real patient information is processed or stored.

    For real appointments, call:
    **1-844-BSW-DOCS**
    """)

# Main content
st.markdown("""
<div class="main-header">
    <h1><� Baylor Scott & White Health</h1>
    <p>AI-Powered Appointment Scheduling Assistant</p>
</div>
""", unsafe_allow_html=True)

# Welcome message
st.markdown("""
<div class="info-card">
    <h3>Welcome to BSW Health's AI Scheduling Assistant</h3>
    <p>
        Experience the future of healthcare appointment scheduling with our intelligent AI agent system.
        Our multi-agent platform seamlessly routes your requests to specialty-specific scheduling assistants
        for Orthopedics, Cardiology, and Primary Care.
    </p>
</div>
""", unsafe_allow_html=True)

# Feature highlights
st.markdown("## Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-item">
        <div class="feature-icon">></div>
        <div class="feature-title">Multi-Agent Intelligence</div>
        <div class="feature-description">
            Intelligent routing system directs you to the right specialist agent based on your needs.
            Orthopedic, Cardiology, and Primary Care experts at your service.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-item">
        <div class="feature-icon">=</div>
        <div class="feature-title">RAG-Enhanced Policies</div>
        <div class="feature-description">
            Real-time retrieval of insurance coverage rules, clinical protocols, and scheduling policies
            to provide accurate, policy-compliant guidance.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-item">
        <div class="feature-icon">�</div>
        <div class="feature-title">Smart Function Calling</div>
        <div class="feature-description">
            Advanced AI uses function calling to check provider availability, verify insurance,
            search appointment slots, and book appointments seamlessly.
        </div>
    </div>
    """, unsafe_allow_html=True)

# How it works
st.markdown("## How It Works")

with st.expander("1. Start a Conversation", expanded=False):
    st.markdown("""
    Navigate to the **Chat** page and describe your appointment needs in natural language.

    Examples:
    - "I need a follow-up for my knee replacement surgery"
    - "I'm having chest pain and need to see a cardiologist"
    - "I'd like to schedule my annual physical exam"
    """)

with st.expander("2. Intelligent Routing", expanded=False):
    st.markdown("""
    Our Router Agent analyzes your request and automatically directs you to the appropriate specialist agent:

    - **Orthopedic Agent**: Joint pain, sports injuries, bone/muscle issues, post-op follow-ups
    - **Cardiology Agent**: Heart-related concerns, chest pain, cardiovascular conditions
    - **Primary Care Agent**: General health, wellness exams, preventive care, routine checkups
    """)

with st.expander("3. Policy-Aware Assistance", expanded=False):
    st.markdown("""
    The specialist agent checks relevant policies and requirements:

    - Insurance coverage verification and copay information
    - Referral requirements based on your insurance plan
    - Clinical scheduling protocols for your condition
    - Provider availability and specialty matching
    """)

with st.expander("4. Seamless Booking", expanded=False):
    st.markdown("""
    The agent helps you:

    - Find available providers matching your criteria
    - Search appointment slots based on your preferences
    - Verify insurance coverage and referral status
    - Book your appointment with instant confirmation
    """)

# Demo scenarios
st.markdown("## Try These Demo Scenarios")

scenarios_col1, scenarios_col2 = st.columns(2)

with scenarios_col1:
    st.markdown("""
    ### Orthopedic Follow-up
    **Patient**: Sarah Martinez (PT001)

    "I had knee replacement surgery 2 weeks ago with Dr. Martinez and need to schedule
    my follow-up appointment."

    *Demonstrates*: Post-op protocols, provider matching, clinical scheduling
    """)

    st.markdown("""
    ### Annual Wellness Visit
    **Patient**: Michael Thompson (PT004)

    "I need to schedule my annual physical exam with my primary care doctor."

    *Demonstrates*: Preventive care scheduling, insurance coverage, routine appointments
    """)

with scenarios_col2:
    st.markdown("""
    ### Cardiology Consultation
    **Patient**: James Wilson (PT002)

    "I've been having chest pain and my PCP referred me to cardiology for evaluation."

    *Demonstrates*: Urgency assessment, referral verification, Medicare coverage
    """)

    st.markdown("""
    ### Complex Rescheduling
    **Patient**: Lisa Chen (PT003)

    "I need to reschedule my appointment with Dr. Kim due to a conflict."

    *Demonstrates*: Appointment management, provider preferences, constraint satisfaction
    """)

# Technology stack
with st.expander("Technology Stack & Architecture"):
    st.markdown("""
    ### Core Technologies

    - **Frontend**: Streamlit (Multi-page application)
    - **LLM**: OpenAI GPT-4o-mini (Function calling & reasoning)
    - **Vector DB**: ChromaDB (RAG for healthcare policies)
    - **Data**: Python dataclasses (Mock Epic EMR data)
    - **Visualization**: Plotly (Real-time metrics dashboards)

    ### Architecture Highlights

    - **Multi-Agent Orchestration**: Router agent coordinates specialty agents
    - **RAG Integration**: Real-time policy retrieval from vector database
    - **Function Calling**: OpenAI function calling for tool use
    - **Metrics Tracking**: Comprehensive conversation quality monitoring
    - **HIPAA-Aware Design**: Mock data only, demonstrates PHI handling awareness
    """)

# Get started
st.markdown("---")

st.markdown("## Ready to Get Started?")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("=� Start Chatting", use_container_width=True):
        st.switch_page("pages/chat.py")

with col2:
    if st.button("=� View Metrics", use_container_width=True):
        st.switch_page("pages/metrics_dashboard.py")

with col3:
    if st.button("P Give Feedback", use_container_width=True):
        st.switch_page("pages/feedback.py")

with col4:
    if st.button("=� Test Scenarios", use_container_width=True):
        st.info("Navigate to Chat page to try demo scenarios")

# Footer
st.markdown("""
<div class="footer">
    <p><strong>Baylor Scott & White Health - AI Scheduling Agent Demo</strong></p>
    <p>Developed for BSW Health Interview | October 2025</p>
    <p>Tech Stack: Python 3.11 | Streamlit | OpenAI GPT-4o-mini | ChromaDB</p>
    <p style="margin-top: 1rem; font-size: 0.85rem; color: #999;">
        This is a demonstration system using mock data only. No real patient information is stored or processed.
    </p>
</div>
""", unsafe_allow_html=True)
