"""
Feedback Page - Preference labeling and conversation rating system.

This page provides:
- Side-by-side response comparison for preference labeling
- Conversation quality rating
- Human-in-the-loop feedback collection
- Dataset building for fine-tuning and evaluation
- Feedback history and analytics
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import os

# Page configuration
st.set_page_config(
    page_title="Feedback - BSW Scheduling Agent",
    page_icon="⭐",
    layout="wide"
)

# Initialize session state
if "feedback_history" not in st.session_state:
    st.session_state.feedback_history = []

if "current_comparison" not in st.session_state:
    st.session_state.current_comparison = None

# Helper functions
def save_feedback(feedback_data: Dict[str, Any]):
    """Save feedback to session state and optionally to file."""
    feedback_data["timestamp"] = datetime.now().isoformat()
    st.session_state.feedback_history.append(feedback_data)

    # Optionally save to file (in production, would go to database)
    try:
        feedback_file = "feedback_data.jsonl"
        with open(feedback_file, 'a') as f:
            f.write(json.dumps(feedback_data) + '\n')
    except Exception as e:
        st.warning(f"Could not save to file: {e}")

def generate_sample_responses() -> Dict[str, str]:
    """Generate sample responses for comparison demo."""
    samples = [
        {
            "scenario": "Patient needs orthopedic follow-up",
            "prompt": "I had knee replacement surgery 2 weeks ago and need a follow-up appointment with Dr. Martinez.",
            "response_a": "I can help you schedule that follow-up. Let me check Dr. Martinez's availability. I see he has openings on Thursday at 10 AM and Friday at 2:30 PM at the Plano location. Which time works better for you?",
            "response_b": "I'll help you book your post-operative follow-up with Dr. Martinez. For knee replacement patients, we recommend a 2-week follow-up, which aligns perfectly with your timeline. Dr. Martinez has availability this Thursday at 10:00 AM or Friday at 2:30 PM, both at BSW Medical Center - Plano (4708 Alliance Blvd). Please bring your physical therapy notes to the appointment. Which time would you prefer?"
        },
        {
            "scenario": "Patient with chest pain needs cardiology",
            "prompt": "I've been having chest pain and my doctor referred me to see a cardiologist.",
            "response_a": "I can schedule you with a cardiologist. We have Dr. Patel available next week. Would you like morning or afternoon?",
            "response_b": "I understand you've been experiencing chest pain and have a referral for cardiology evaluation. First, I want to make sure this isn't an emergency - are you experiencing chest pain right now? If yes, please call 911. If this is for scheduled follow-up, I can help you book an urgent appointment with our cardiology team. Dr. Patel has availability within the next 3 days. Let me also verify your insurance coverage and referral status."
        },
        {
            "scenario": "Annual wellness visit",
            "prompt": "I need to schedule my annual physical exam.",
            "response_a": "Sure, I can schedule your annual physical. Which day works best for you?",
            "response_b": "Great! I'm glad you're staying on top of your preventive care. Annual wellness visits are typically covered at no copay by most insurance plans. I recommend scheduling a morning appointment since we'll likely be doing fasting bloodwork. Do you have an existing primary care provider with us, or would you like me to help you find a PCP? Also, which BSW location is most convenient for you?"
        }
    ]

    import random
    return random.choice(samples)

# Page header
st.markdown("""
<div style="background: linear-gradient(135deg, #00447c 0%, #00a4e4 100%);
            padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">⭐ Feedback & Preference Labeling</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
        Help improve the AI scheduling assistant through human feedback
    </p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs([
    "📊 Response Comparison",
    "⭐ Rate Conversation",
    "📈 Feedback Analytics"
])

# Tab 1: Response Comparison
with tab1:
    st.markdown("### Side-by-Side Response Comparison")

    st.info("""
    **Purpose**: Compare two agent responses to the same prompt and indicate which is better.
    This helps build a preference dataset for fine-tuning and evaluation.
    """)

    # Generate or use existing comparison
    if st.button("🔄 Generate New Comparison", use_container_width=False):
        st.session_state.current_comparison = generate_sample_responses()

    if st.session_state.current_comparison is None:
        st.session_state.current_comparison = generate_sample_responses()

    comparison = st.session_state.current_comparison

    # Display scenario and prompt
    st.markdown("#### Scenario")
    st.markdown(f"**{comparison['scenario']}**")

    st.markdown("#### Patient Prompt")
    st.code(comparison['prompt'], language="text")

    st.markdown("---")

    # Side-by-side comparison
    st.markdown("#### Compare Responses")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Response A")
        st.markdown(f"""
        <div style="background-color: #f0f8ff; padding: 1.5rem; border-radius: 8px;
                    border-left: 4px solid #00a4e4; min-height: 200px;">
            {comparison['response_a']}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("##### Response B")
        st.markdown(f"""
        <div style="background-color: #f0fff0; padding: 1.5rem; border-radius: 8px;
                    border-left: 4px solid #00cc88; min-height: 200px;">
            {comparison['response_b']}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Preference selection
    st.markdown("#### Your Preference")

    col1, col2, col3, col4 = st.columns([2, 2, 2, 4])

    with col1:
        prefer_a = st.button("👈 Prefer Response A", use_container_width=True)

    with col2:
        prefer_b = st.button("👉 Prefer Response B", use_container_width=True)

    with col3:
        prefer_tie = st.button("🤝 Both Equal", use_container_width=True)

    # Process selection
    if prefer_a or prefer_b or prefer_tie:
        preference = "A" if prefer_a else ("B" if prefer_b else "Tie")

        st.success(f"✅ Preference recorded: **{preference}**")

        # Collect additional feedback
        with st.form("detailed_feedback"):
            st.markdown("##### Why did you choose this response?")

            reasons = st.multiselect(
                "Select all that apply:",
                [
                    "More thorough and detailed",
                    "Better addresses patient needs",
                    "More empathetic tone",
                    "Includes important safety considerations",
                    "Better uses medical protocols",
                    "More natural and conversational",
                    "Provides clearer next steps",
                    "Better insurance/coverage handling"
                ]
            )

            additional_comments = st.text_area(
                "Additional comments (optional):",
                placeholder="Any other observations or suggestions..."
            )

            submitted = st.form_submit_button("Submit Feedback")

            if submitted:
                feedback_data = {
                    "type": "preference_comparison",
                    "scenario": comparison["scenario"],
                    "prompt": comparison["prompt"],
                    "response_a": comparison["response_a"],
                    "response_b": comparison["response_b"],
                    "preference": preference,
                    "reasons": reasons,
                    "comments": additional_comments
                }

                save_feedback(feedback_data)

                st.success("🎉 Thank you! Your feedback has been saved.")

                # Generate new comparison
                st.session_state.current_comparison = generate_sample_responses()
                st.rerun()

# Tab 2: Rate Conversation
with tab2:
    st.markdown("### Rate a Conversation")

    st.info("""
    **Purpose**: Evaluate the overall quality of a conversation between patient and agent.
    Rate different aspects to help identify areas for improvement.
    """)

    # Sample conversation display
    st.markdown("#### Sample Conversation")

    sample_conversation = [
        ("user", "I need to schedule an appointment for my knee pain."),
        ("assistant", "I can help you schedule an appointment for your knee pain. To find the right specialist, can you tell me more about your knee pain? Is this from an injury, surgery, or chronic condition?"),
        ("user", "It's from arthritis. I need to see an orthopedic doctor."),
        ("assistant", "I understand. Let me find an orthopedic specialist for you. Do you have a location preference - Dallas, Plano, Arlington, or Temple? Also, do you have insurance I should verify?"),
        ("user", "Plano is good. I have Blue Cross Blue Shield."),
        ("assistant", "Perfect. I found Dr. David Anderson, an orthopedic surgeon specializing in joint replacement at BSW Medical Center - Plano. He accepts Blue Cross Blue Shield. I should note that BCBS requires a referral for specialist visits. Do you have a referral from your primary care physician?")
    ]

    for role, message in sample_conversation:
        if role == "user":
            st.markdown(f"""
            <div style="background-color: #e3f2fd; padding: 1rem; border-radius: 8px;
                        margin: 0.5rem 0; border-left: 4px solid #2196f3;">
                <strong>Patient:</strong> {message}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color: #f3e5f5; padding: 1rem; border-radius: 8px;
                        margin: 0.5rem 0; border-left: 4px solid #9c27b0;">
                <strong>Assistant:</strong> {message}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Rating form
    with st.form("conversation_rating"):
        st.markdown("#### Rate This Conversation")

        col1, col2 = st.columns(2)

        with col1:
            relevance = st.slider(
                "**Relevance**: Responses address patient needs",
                min_value=1, max_value=5, value=4,
                help="How well did the agent understand and address what the patient needed?"
            )

            helpfulness = st.slider(
                "**Helpfulness**: Provides actionable information",
                min_value=1, max_value=5, value=4,
                help="Did the agent provide useful, actionable information?"
            )

            accuracy = st.slider(
                "**Accuracy**: Information is correct",
                min_value=1, max_value=5, value=5,
                help="Was the information factually accurate?"
            )

        with col2:
            naturalness = st.slider(
                "**Naturalness**: Conversation flows naturally",
                min_value=1, max_value=5, value=4,
                help="Did the conversation feel natural and human-like?"
            )

            empathy = st.slider(
                "**Empathy**: Shows understanding and care",
                min_value=1, max_value=5, value=4,
                help="Did the agent show appropriate empathy and bedside manner?"
            )

            efficiency = st.slider(
                "**Efficiency**: Gets to the point quickly",
                min_value=1, max_value=5, value=3,
                help="Was the agent efficient without unnecessary back-and-forth?"
            )

        st.markdown("---")

        task_completed = st.checkbox("✅ Task was successfully completed")

        overall_sentiment = st.radio(
            "Overall sentiment about this conversation:",
            ["😊 Very Satisfied", "🙂 Satisfied", "😐 Neutral", "😕 Unsatisfied", "😞 Very Unsatisfied"],
            index=1
        )

        what_went_well = st.text_area(
            "What went well?",
            placeholder="What did the agent do particularly well?"
        )

        what_needs_improvement = st.text_area(
            "What needs improvement?",
            placeholder="What could be better?"
        )

        submitted_rating = st.form_submit_button("Submit Rating")

        if submitted_rating:
            rating_data = {
                "type": "conversation_rating",
                "ratings": {
                    "relevance": relevance,
                    "helpfulness": helpfulness,
                    "accuracy": accuracy,
                    "naturalness": naturalness,
                    "empathy": empathy,
                    "efficiency": efficiency,
                    "average": round((relevance + helpfulness + accuracy + naturalness + empathy + efficiency) / 6, 2)
                },
                "task_completed": task_completed,
                "overall_sentiment": overall_sentiment,
                "what_went_well": what_went_well,
                "what_needs_improvement": what_needs_improvement
            }

            save_feedback(rating_data)

            st.success("🎉 Thank you! Your rating has been recorded.")

# Tab 3: Feedback Analytics
with tab3:
    st.markdown("### Feedback Analytics")

    if not st.session_state.feedback_history:
        st.info("""
        📊 **No feedback data yet**

        Provide feedback in the other tabs to see analytics here.

        This section will show:
        - Preference distribution (Response A vs B vs Tie)
        - Average conversation ratings
        - Common improvement themes
        - Feedback trends over time
        """)
    else:
        # Summary metrics
        st.markdown("#### Summary")

        total_feedback = len(st.session_state.feedback_history)

        comparisons = [f for f in st.session_state.feedback_history if f["type"] == "preference_comparison"]
        ratings = [f for f in st.session_state.feedback_history if f["type"] == "conversation_rating"]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Feedback Items", total_feedback)

        with col2:
            st.metric("Response Comparisons", len(comparisons))

        with col3:
            st.metric("Conversation Ratings", len(ratings))

        st.markdown("---")

        # Preference distribution
        if comparisons:
            st.markdown("#### Preference Distribution")

            from collections import Counter
            preferences = [c["preference"] for c in comparisons]
            pref_counts = Counter(preferences)

            col1, col2 = st.columns([2, 3])

            with col1:
                st.markdown("**Preference Counts**")
                for pref, count in pref_counts.items():
                    st.metric(f"Response {pref}", count)

            with col2:
                st.markdown("**Common Reasons**")
                all_reasons = []
                for c in comparisons:
                    all_reasons.extend(c.get("reasons", []))

                reason_counts = Counter(all_reasons)
                for reason, count in reason_counts.most_common(5):
                    st.markdown(f"- {reason}: **{count}** times")

        st.markdown("---")

        # Average ratings
        if ratings:
            st.markdown("#### Average Conversation Ratings")

            avg_ratings = {
                "Relevance": sum(r["ratings"]["relevance"] for r in ratings) / len(ratings),
                "Helpfulness": sum(r["ratings"]["helpfulness"] for r in ratings) / len(ratings),
                "Accuracy": sum(r["ratings"]["accuracy"] for r in ratings) / len(ratings),
                "Naturalness": sum(r["ratings"]["naturalness"] for r in ratings) / len(ratings),
                "Empathy": sum(r["ratings"]["empathy"] for r in ratings) / len(ratings),
                "Efficiency": sum(r["ratings"]["efficiency"] for r in ratings) / len(ratings),
            }

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Relevance", f"{avg_ratings['Relevance']:.2f} / 5")
                st.metric("Helpfulness", f"{avg_ratings['Helpfulness']:.2f} / 5")

            with col2:
                st.metric("Accuracy", f"{avg_ratings['Accuracy']:.2f} / 5")
                st.metric("Naturalness", f"{avg_ratings['Naturalness']:.2f} / 5")

            with col3:
                st.metric("Empathy", f"{avg_ratings['Empathy']:.2f} / 5")
                st.metric("Efficiency", f"{avg_ratings['Efficiency']:.2f} / 5")

        st.markdown("---")

        # Feedback history
        st.markdown("#### Feedback History")

        for i, feedback in enumerate(reversed(st.session_state.feedback_history[-10:])):
            with st.expander(f"Feedback #{len(st.session_state.feedback_history) - i} - {feedback.get('timestamp', 'Unknown')}"):
                st.json(feedback)

        # Export button
        if st.button("📥 Export All Feedback as JSON"):
            json_str = json.dumps(st.session_state.feedback_history, indent=2)

            st.download_button(
                label="Download Feedback JSON",
                data=json_str,
                file_name=f"bsw_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
    <p>BSW Health AI Scheduling Agent - Feedback System</p>
    <p style="font-size: 0.8rem;">
        Your feedback helps improve the AI assistant and builds datasets for future enhancements.
    </p>
</div>
""", unsafe_allow_html=True)
