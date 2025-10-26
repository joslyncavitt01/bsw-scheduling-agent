# Baylor Scott & White Health - AI Scheduling Agent Demo

> **Production-quality AI agent system demonstrating multi-agent orchestration, RAG, and function calling for healthcare appointment scheduling**

## 🎯 Project Overview

This demo showcases an enterprise-grade AI scheduling assistant designed for Baylor Scott & White Health's healthcare system. The system uses advanced LLM capabilities (GPT-4o-mini) with function calling, RAG retrieval, and multi-agent orchestration to intelligently handle appointment scheduling across multiple medical specialties.

**Purpose**: Interview demonstration showcasing expertise in:
- Multi-agent AI systems with intelligent routing
- Healthcare domain knowledge (HIPAA considerations, clinical workflows, insurance)
- Production-ready architecture and code quality
- Real-time evaluation and metrics tracking

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI                           │
│  (Multi-page: Chat | Metrics Dashboard | Feedback)          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
           ┌─────────────────┐
           │  Router Agent   │ ◄─── RAG: Healthcare Policies
           │  (gpt-4o-mini)  │      (ChromaDB Vector Store)
           └────────┬────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   ┌─────────┐ ┌──────────┐ ┌──────────┐
   │Orthopedic│ │Cardiology│ │ Primary  │
   │  Agent   │ │  Agent   │ │   Care   │
   └────┬─────┘ └─────┬────┘ └─────┬────┘
        │             │            │
        └─────────────┼────────────┘
                      │
            ┌─────────▼──────────┐
            │  Function Calling  │
            │                    │
            │ • check_provider   │
            │ • search_slots     │
            │ • book_appointment │
            │ • verify_insurance │
            │ • check_referral   │
            └────────┬───────────┘
                     │
                     ▼
            ┌─────────────────┐
            │   Mock Epic EMR │
            │   (mock_data.py)│
            └─────────────────┘
```

## ✨ Key Features

### 1. **Multi-Agent Orchestration**
- **Router Agent**: Analyzes patient intent and routes to appropriate specialty agent
- **Specialty Agents**: Domain-specific agents for orthopedics, cardiology, and primary care
- **Intelligent Handoff**: Seamless context transfer between agents

### 2. **Function Calling (Tool Use)**
- Real-time provider availability lookup
- Appointment slot search with constraint satisfaction
- Insurance verification and prior authorization checks
- Appointment booking with conflict detection
- Referral validation

### 3. **RAG (Retrieval Augmented Generation)**
- Vector store of healthcare policies (ChromaDB)
- Insurance coverage rules (BCBS, Aetna, Medicare, Medicaid)
- Clinical scheduling protocols (post-op follow-ups, urgent care)
- Real-time policy retrieval during conversations

### 4. **Evaluation & Metrics**
- Real-time conversation quality scoring
- Task success rate tracking
- Tool usage analytics
- Latency and token consumption monitoring
- Per-agent performance comparison

### 5. **Preference Labeling System**
- Side-by-side response comparison
- Human-in-the-loop feedback collection
- Builds dataset for fine-tuning and evaluation

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+
- OpenAI API key

### Installation

1. **Clone and navigate to project**
```bash
cd bsw-scheduling-agent
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-...
```

5. **Initialize RAG knowledge base** (first run)
```bash
python rag.py
```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📋 Demo Scenarios

The system includes realistic test scenarios demonstrating various capabilities:

### Scenario 1: Orthopedic Follow-up
**Patient**: Sarah Martinez (knee replacement post-op)
- **Challenge**: 2-week post-op follow-up scheduling
- **Demonstrates**: Clinical protocol RAG, provider matching, availability search

### Scenario 2: Cardiology New Patient
**Patient**: James Wilson (chest pain, needs cardiologist)
- **Challenge**: Insurance verification (Medicare), referral requirement
- **Demonstrates**: Insurance policy RAG, multi-step booking flow, urgent prioritization

### Scenario 3: Complex Rescheduling
**Patient**: Lisa Chen (existing appointment conflict)
- **Challenge**: Find alternative slots respecting provider preference
- **Demonstrates**: Constraint satisfaction, conflict detection, patient preference handling

### Scenario 4: Primary Care Wellness
**Patient**: Michael Thompson (annual physical)
- **Challenge**: Preventive care scheduling with insurance coverage check
- **Demonstrates**: Insurance coverage verification, routine appointment booking

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Multi-page interactive UI |
| **LLM** | OpenAI GPT-4o-mini | Agent reasoning & function calling |
| **Vector DB** | ChromaDB | RAG for healthcare policies |
| **Data Layer** | Python dataclasses | Structured mock data |
| **Visualization** | Plotly | Real-time metrics dashboards |
| **Orchestration** | Custom Python | Multi-agent routing logic |

## 📁 Project Structure

```
bsw-scheduling-agent/
├── app.py                      # Streamlit entry point
├── agents/
│   ├── router.py              # Router agent (intent classification)
│   ├── orthopedic_agent.py    # Orthopedic specialty agent
│   └── cardiology_agent.py    # Cardiology specialty agent
├── pages/
│   ├── chat.py                # Main chat interface
│   ├── metrics_dashboard.py   # Real-time metrics
│   └── feedback.py            # Preference labeling UI
├── evaluation/
│   ├── scenarios.py           # Test scenarios
│   └── metrics.py             # Evaluation logic
├── mock_data.py               # Healthcare mock data
├── rag.py                     # RAG setup & retrieval
├── tools.py                   # Function calling tools
├── prompts.py                 # System prompts
└── requirements.txt           # Dependencies
```

## 🎯 Production Considerations

This demo incorporates production-ready patterns:

- **Error Handling**: Graceful fallbacks for API failures
- **Type Safety**: Pydantic models and type hints throughout
- **Logging**: Structured logging for debugging and monitoring
- **Modularity**: Clean separation of concerns, extensible architecture
- **Security**: Environment-based configuration, no hardcoded credentials
- **Testing**: Evaluation framework with automated scenarios
- **HIPAA Awareness**: Mock data only, demonstrates understanding of PHI handling

## 🔮 Future Enhancements

- Integrate with real EHR systems (Epic, Cerner)
- Add voice interface for accessibility
- Implement FHIR standard compliance
- Multi-language support (Spanish for Texas demographics)
- SMS/Email appointment reminders
- Waitlist management and automatic rebooking

## 📝 Notes

- This is a **demonstration system** using mock data only
- No real patient information is stored or processed
- OpenAI API calls may incur costs (minimal with gpt-4o-mini)
- ChromaDB runs in-memory for simplicity (production would use persistent storage)

---

**Developed for**: Baylor Scott & White Health Interview  
**Date**: October 2025  
**Tech Stack**: Python 3.11 | Streamlit | OpenAI GPT-4o-mini | ChromaDB


