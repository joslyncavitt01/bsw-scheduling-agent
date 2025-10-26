"""
BSW Scheduling Agent - Feedback & Preference Labeling
Interface for collecting user feedback and preference labeling for model improvement.
"""

import streamlit as st
from datetime import datetime
import json
import pandas as pd

from evaluation.metrics import get_metrics_tracker

# Page configuration
st.set_page_config(
    page_title="Feedback - BSW Scheduling Agent",
    page_icon="P",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .feedback-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border-left: 4px solid #00a4e4;
    }

    .conversation-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }

    .user-message {
        background: #e7f3ff;
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #00a4e4;
    }

    .agent-message {
        background: #f1f3f5;
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #00447c;
    }

    .rating-button {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 6px;
        background: #f8f9fa;
        border: 2px solid #dee2e6;
        cursor: pointer;
        transition: all 0.2s;
    }

    .rating-button:hover {
        background: #e9ecef;
        border-color: #00a4e4;
    }

    .rating-button.selected {
        background: #00a4e4;
        color: white;
        border-color: #00447c;
    }

    .star-rating {
        font-size: 2rem;
        color: #ffc107;
    }

    .feedback-summary {
        background: linear-gradient(135deg, #00447c 0%, #00a4e4 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .summary-stat {
        text-align: center;
        padding: 1rem;
    }

    .summary-stat .number {
        font-size: 2rem;
        font-weight: 700;
        color: white;
    }

    .summary-stat .label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("P Feedback & Preference Labeling")
st.markdown("Help improve the AI scheduling agent by rating conversations and providing feedback")

# Get metrics tracker
tracker = get_metrics_tracker()

# Initialize session state
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = False

if 'current_conv_index' not in st.session_state:
    st.session_state.current_conv_index = 0

# Tabs for different feedback modes
tab1, tab2, tab3 = st.tabs(["=Ý Rate Conversations", "<š Compare Responses", "=Ê Feedback Summary"])

# Tab 1: Rate individual conversations
with tab1:
    st.markdown("### Rate Recent Conversations")
    st.markdown("Provide feedback on individual conversations to help improve response quality")

    # Get conversations without feedback
    conversations_without_feedback = [
        c for c in tracker.conversations
        if c.feedback_score is None
    ]

    if conversations_without_feedback:
        # Show conversation count
        st.info(f"**{len(conversations_without_feedback)}** conversations awaiting feedback")

        # Pagination
        items_per_page = 5
        total_pages = (len(conversations_without_feedback) + items_per_page - 1) // items_per_page

        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            if st.button(" Previous") and st.session_state.current_conv_index > 0:
                st.session_state.current_conv_index -= items_per_page
                st.rerun()

        with col2:
            current_page = st.session_state.current_conv_index // items_per_page + 1
            st.markdown(f"<div style='text-align: center;'>Page {current_page} of {total_pages}</div>",
                       unsafe_allow_html=True)

        with col3:
            if st.button("Next ¡") and st.session_state.current_conv_index + items_per_page < len(conversations_without_feedback):
                st.session_state.current_conv_index += items_per_page
                st.rerun()

        # Display conversations for current page
        start_idx = st.session_state.current_conv_index
        end_idx = min(start_idx + items_per_page, len(conversations_without_feedback))

        for i, conv in enumerate(conversations_without_feedback[start_idx:end_idx], start=start_idx):
            with st.container():
                st.markdown(f"""
                <div class="feedback-card">
                    <h4>Conversation #{i + 1} - {conv.agent_type.replace('_', ' ').title()}</h4>
                    <small>{datetime.fromisoformat(conv.timestamp).strftime('%Y-%m-%d %H:%M:%S')}</small>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>User:</strong> {conv.user_message}
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="agent-message">
                        <strong>Agent:</strong> {conv.agent_response}
                    </div>
                    """, unsafe_allow_html=True)

                    if conv.tools_used:
                        with st.expander(f"=' Tools Used ({len(conv.tools_used)})"):
                            for tool in conv.tools_used:
                                st.markdown(f"- `{tool}`")

                with col2:
                    st.markdown("#### Rate this conversation")

                    # Star rating
                    rating = st.radio(
                        "Quality Rating",
                        options=[1, 2, 3, 4, 5],
                        format_func=lambda x: "P" * x,
                        key=f"rating_{conv.conversation_id}",
                        horizontal=True
                    )

                    # Feedback comment
                    comment = st.text_area(
                        "Comments (optional)",
                        placeholder="What worked well? What could be improved?",
                        key=f"comment_{conv.conversation_id}",
                        height=100
                    )

                    # Submit button
                    if st.button("Submit Feedback", key=f"submit_{conv.conversation_id}", use_container_width=True):
                        tracker.add_feedback(
                            conversation_id=conv.conversation_id,
                            score=rating,
                            comment=comment if comment else None
                        )
                        st.success("Feedback submitted successfully!")
                        st.rerun()

                st.markdown("---")

    else:
        st.info("All recent conversations have been rated. Thank you for your feedback!")

        # Show button to view rated conversations
        if st.button("View Rated Conversations"):
            st.session_state.show_rated = True

        if st.session_state.get('show_rated', False):
            rated_conversations = [c for c in tracker.conversations if c.feedback_score is not None]

            for conv in rated_conversations[-10:]:  # Show last 10 rated
                with st.expander(
                    f"{'P' * conv.feedback_score} {conv.agent_type.title()} - {datetime.fromisoformat(conv.timestamp).strftime('%Y-%m-%d %H:%M')}"
                ):
                    st.markdown(f"**User**: {conv.user_message}")
                    st.markdown(f"**Agent**: {conv.agent_response}")
                    if conv.feedback_comment:
                        st.markdown(f"**Comment**: {conv.feedback_comment}")

# Tab 2: Compare responses (preference labeling)
with tab2:
    st.markdown("### Side-by-Side Response Comparison")
    st.markdown("Compare different agent responses to help identify preferred patterns")

    st.info("""
    **Coming Soon!**

    This feature will allow you to:
    - View two different agent responses to similar queries
    - Select which response is better
    - Provide reasoning for your preference
    - Build a dataset for fine-tuning and evaluation
    """)

    # Placeholder for future implementation
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Response A")
        st.markdown("""
        <div class="conversation-box">
            <div class="agent-message">
                <strong>Agent:</strong> I can help you schedule an appointment with Dr. Anderson,
                our orthopedic specialist. He has availability next Tuesday at 2:00 PM.
                Would you like me to book that for you?
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.button("Prefer Response A", key="prefer_a", disabled=True)

    with col2:
        st.markdown("#### Response B")
        st.markdown("""
        <div class="conversation-box">
            <div class="agent-message">
                <strong>Agent:</strong> I'd be happy to help schedule your orthopedic follow-up.
                Let me check Dr. Anderson's availability since you saw him for surgery.
                I have several options: Tuesday 2:00 PM, Wednesday 10:00 AM, or Thursday 3:30 PM.
                Which works best for you?
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.button("Prefer Response B", key="prefer_b", disabled=True)

    st.text_area(
        "Explain your preference (optional)",
        placeholder="Why did you prefer this response?",
        disabled=True
    )

    st.button("Submit Comparison", disabled=True)

# Tab 3: Feedback summary
with tab3:
    st.markdown("### Feedback Summary & Analytics")

    # Overall feedback stats
    rated_conversations = [c for c in tracker.conversations if c.feedback_score is not None]

    if rated_conversations:
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("""
            <div class="feedback-summary">
                <div class="summary-stat">
                    <div class="number">{}</div>
                    <div class="label">Total Ratings</div>
                </div>
            </div>
            """.format(len(rated_conversations)), unsafe_allow_html=True)

        with col2:
            avg_rating = sum(c.feedback_score for c in rated_conversations) / len(rated_conversations)
            st.markdown("""
            <div class="feedback-summary">
                <div class="summary-stat">
                    <div class="number">{:.2f}</div>
                    <div class="label">Average Rating</div>
                </div>
            </div>
            """.format(avg_rating), unsafe_allow_html=True)

        with col3:
            five_star = sum(1 for c in rated_conversations if c.feedback_score == 5)
            st.markdown("""
            <div class="feedback-summary">
                <div class="summary-stat">
                    <div class="number">{}P</div>
                    <div class="label">5-Star Ratings</div>
                </div>
            </div>
            """.format(five_star), unsafe_allow_html=True)

        with col4:
            low_rating = sum(1 for c in rated_conversations if c.feedback_score <= 2)
            st.markdown("""
            <div class="feedback-summary">
                <div class="summary-stat">
                    <div class="number">{}</div>
                    <div class="label">Low Ratings</div>
                </div>
            </div>
            """.format(low_rating), unsafe_allow_html=True)

        # Rating distribution
        st.markdown("#### Rating Distribution")

        rating_counts = {i: 0 for i in range(1, 6)}
        for conv in rated_conversations:
            rating_counts[conv.feedback_score] = rating_counts.get(conv.feedback_score, 0) + 1

        import plotly.graph_objects as go

        fig = go.Figure(go.Bar(
            x=[f"{i} Star{'s' if i > 1 else ''}" for i in range(1, 6)],
            y=[rating_counts[i] for i in range(1, 6)],
            marker=dict(
                color=['#dc3545', '#fd7e14', '#ffc107', '#28a745', '#28a745'],
                line=dict(color='#00447c', width=2)
            ),
            text=[rating_counts[i] for i in range(1, 6)],
            textposition='outside'
        ))

        fig.update_layout(
            yaxis_title="Count",
            height=300,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # Feedback by agent type
        st.markdown("#### Average Rating by Agent Type")

        agent_ratings = {}
        for conv in rated_conversations:
            if conv.agent_type not in agent_ratings:
                agent_ratings[conv.agent_type] = []
            agent_ratings[conv.agent_type].append(conv.feedback_score)

        df_agent_feedback = pd.DataFrame([
            {
                'Agent': agent.replace('_', ' ').title(),
                'Average Rating': sum(scores) / len(scores),
                'Total Ratings': len(scores),
                '5-Star %': f"{sum(1 for s in scores if s == 5) / len(scores) * 100:.1f}%"
            }
            for agent, scores in agent_ratings.items()
        ])

        st.dataframe(df_agent_feedback, use_container_width=True, hide_index=True)

        # Recent feedback comments
        st.markdown("#### Recent Feedback Comments")

        comments = [c for c in rated_conversations if c.feedback_comment][-10:]

        if comments:
            for conv in comments:
                with st.expander(
                    f"{'P' * conv.feedback_score} {conv.agent_type.replace('_', ' ').title()} - {datetime.fromisoformat(conv.timestamp).strftime('%Y-%m-%d %H:%M')}"
                ):
                    st.markdown(f"**Rating**: {'P' * conv.feedback_score}")
                    st.markdown(f"**Comment**: {conv.feedback_comment}")
                    st.markdown(f"**User Message**: {conv.user_message[:200]}...")
        else:
            st.info("No feedback comments available yet")

        # Export feedback data
        st.markdown("---")
        st.markdown("#### Export Feedback Data")

        if st.button("=å Download Feedback Dataset (CSV)", use_container_width=True):
            df_export = pd.DataFrame([
                {
                    'conversation_id': c.conversation_id,
                    'timestamp': c.timestamp,
                    'agent_type': c.agent_type,
                    'user_message': c.user_message,
                    'agent_response': c.agent_response,
                    'feedback_score': c.feedback_score,
                    'feedback_comment': c.feedback_comment or '',
                    'tools_used': ', '.join(c.tools_used),
                    'latency_ms': c.latency_ms,
                    'tokens_used': c.tokens_used
                }
                for c in rated_conversations
            ])

            csv = df_export.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"bsw_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    else:
        st.info("""
        No feedback data available yet.

        Start by rating conversations in the **Rate Conversations** tab.
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 0.85rem;">
    <p>Your feedback helps improve the AI scheduling agent for all patients</p>
    <p>Thank you for contributing to better healthcare experiences!</p>
</div>
""", unsafe_allow_html=True)
