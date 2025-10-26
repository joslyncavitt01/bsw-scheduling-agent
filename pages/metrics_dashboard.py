"""
BSW Scheduling Agent - Metrics Dashboard
Real-time visualization of agent performance, tool usage, and conversation quality.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import json

from evaluation.metrics import get_metrics_tracker

# Page configuration
st.set_page_config(
    page_title="Metrics Dashboard - BSW Scheduling Agent",
    page_icon="=Ê",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #00a4e4;
        margin-bottom: 1rem;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00447c;
        margin: 0;
    }

    .metric-label {
        font-size: 0.95rem;
        color: #6c757d;
        margin-top: 0.5rem;
    }

    .metric-change {
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }

    .metric-positive {
        color: #28a745;
    }

    .metric-negative {
        color: #dc3545;
    }

    .section-header {
        background: linear-gradient(135deg, #00447c 0%, #00a4e4 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 2rem 0 1rem 0;
    }

    .section-header h3 {
        margin: 0;
        color: white;
    }

    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("=Ê Real-Time Metrics Dashboard")
st.markdown("Monitor agent performance, tool usage, and conversation quality")

# Get metrics tracker
tracker = get_metrics_tracker()

# Sidebar filters
with st.sidebar:
    st.markdown("### Filters")

    # Time window filter
    time_windows = {
        "Last Hour": 1,
        "Last 6 Hours": 6,
        "Last 24 Hours": 24,
        "Last 7 Days": 168,
        "All Time": None
    }

    selected_window = st.selectbox(
        "Time Window",
        options=list(time_windows.keys()),
        index=2  # Default to Last 24 Hours
    )

    time_window_hours = time_windows[selected_window]

    # Agent filter
    agent_options = ["All Agents"] + list(tracker.agent_metrics.keys())
    selected_agent = st.selectbox(
        "Agent Type",
        options=agent_options
    )

    agent_filter = None if selected_agent == "All Agents" else selected_agent

    st.markdown("---")

    # Refresh button
    if st.button("= Refresh Data", use_container_width=True):
        st.rerun()

    # Export data
    st.markdown("---")
    st.markdown("### Export Data")

    if st.button("=å Export Metrics JSON", use_container_width=True):
        metrics_data = tracker.export_to_dict()
        st.download_button(
            label="Download JSON",
            data=json.dumps(metrics_data, indent=2),
            file_name=f"bsw_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    # Reset metrics (with confirmation)
    st.markdown("---")
    st.markdown("### Danger Zone")
    if st.button("=Ñ Reset All Metrics", use_container_width=True):
        if st.checkbox("I confirm I want to reset all metrics"):
            tracker.reset_metrics()
            st.success("Metrics reset successfully")
            st.rerun()

# Overview metrics
st.markdown("""
<div class="section-header">
    <h3>=È Overview</h3>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# Total conversations
total_conversations = len([c for c in tracker.conversations
                          if (time_window_hours is None or
                              (datetime.now() - datetime.fromisoformat(c.timestamp)).total_seconds() / 3600 <= time_window_hours)
                          and (agent_filter is None or c.agent_type == agent_filter)])

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">{}</div>
        <div class="metric-label">Total Conversations</div>
    </div>
    """.format(total_conversations), unsafe_allow_html=True)

# Success rate
success_rate = tracker.get_success_rate(agent_filter, time_window_hours)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">{:.1%}</div>
        <div class="metric-label">Success Rate</div>
        <div class="metric-change metric-positive">
            {} successful
        </div>
    </div>
    """.format(
        success_rate,
        sum(1 for c in tracker._filter_conversations(agent_filter, time_window_hours) if c.success)
    ), unsafe_allow_html=True)

# Average latency
conversations = tracker._filter_conversations(agent_filter, time_window_hours)
avg_latency = sum(c.latency_ms for c in conversations) / len(conversations) if conversations else 0

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">{:.0f}ms</div>
        <div class="metric-label">Avg Response Time</div>
    </div>
    """.format(avg_latency), unsafe_allow_html=True)

# Total tokens
token_stats = tracker.get_token_consumption(agent_filter)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">{:,}</div>
        <div class="metric-label">Total Tokens Used</div>
        <div class="metric-change">
            Avg: {:,.0f} per conversation
        </div>
    </div>
    """.format(
        token_stats['total_tokens'],
        token_stats['average_tokens']
    ), unsafe_allow_html=True)

# Charts section
st.markdown("""
<div class="section-header">
    <h3>=Ê Performance Charts</h3>
</div>
""", unsafe_allow_html=True)

# Row 1: Success rate over time and Tool usage
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### Task Success Rate Over Time")

    if conversations:
        # Create time-series data
        df_success = pd.DataFrame([{
            'timestamp': datetime.fromisoformat(c.timestamp),
            'success': 1 if c.success else 0
        } for c in conversations])

        df_success = df_success.sort_values('timestamp')

        # Calculate rolling success rate
        df_success['cumulative_success_rate'] = df_success['success'].expanding().mean()

        fig_success = go.Figure()

        fig_success.add_trace(go.Scatter(
            x=df_success['timestamp'],
            y=df_success['cumulative_success_rate'] * 100,
            mode='lines+markers',
            name='Success Rate',
            line=dict(color='#00a4e4', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 164, 228, 0.1)'
        ))

        fig_success.update_layout(
            yaxis_title="Success Rate (%)",
            xaxis_title="Time",
            hovermode='x unified',
            height=350,
            showlegend=False
        )

        st.plotly_chart(fig_success, use_container_width=True)
    else:
        st.info("No data available for selected filters")

with chart_col2:
    st.markdown("#### Tool Usage Frequency")

    tool_stats = tracker.get_tool_usage_stats(agent_filter)

    if tool_stats:
        df_tools = pd.DataFrame([
            {'tool': tool, 'count': count}
            for tool, count in sorted(tool_stats.items(), key=lambda x: x[1], reverse=True)
        ])

        fig_tools = go.Figure(go.Bar(
            x=df_tools['count'],
            y=df_tools['tool'],
            orientation='h',
            marker=dict(
                color='#00447c',
                line=dict(color='#00a4e4', width=2)
            ),
            text=df_tools['count'],
            textposition='outside'
        ))

        fig_tools.update_layout(
            xaxis_title="Usage Count",
            yaxis_title="Tool Name",
            height=350,
            showlegend=False
        )

        st.plotly_chart(fig_tools, use_container_width=True)
    else:
        st.info("No tool usage data available")

# Row 2: Response latency and Token consumption
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.markdown("#### Response Latency Distribution")

    if conversations:
        latencies = [c.latency_ms for c in conversations]

        fig_latency = go.Figure(go.Histogram(
            x=latencies,
            nbinsx=20,
            marker=dict(
                color='#00a4e4',
                line=dict(color='#00447c', width=1)
            ),
            name='Latency'
        ))

        fig_latency.add_vline(
            x=avg_latency,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Avg: {avg_latency:.0f}ms"
        )

        fig_latency.update_layout(
            xaxis_title="Latency (ms)",
            yaxis_title="Frequency",
            height=350,
            showlegend=False
        )

        st.plotly_chart(fig_latency, use_container_width=True)
    else:
        st.info("No latency data available")

with chart_col4:
    st.markdown("#### Token Consumption Over Time")

    if conversations:
        df_tokens = pd.DataFrame([{
            'timestamp': datetime.fromisoformat(c.timestamp),
            'tokens': c.tokens_used
        } for c in conversations])

        df_tokens = df_tokens.sort_values('timestamp')

        fig_tokens = go.Figure()

        fig_tokens.add_trace(go.Scatter(
            x=df_tokens['timestamp'],
            y=df_tokens['tokens'],
            mode='lines+markers',
            name='Tokens',
            line=dict(color='#28a745', width=2),
            marker=dict(size=8)
        ))

        # Add average line
        fig_tokens.add_hline(
            y=token_stats['average_tokens'],
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Avg: {token_stats['average_tokens']:.0f}"
        )

        fig_tokens.update_layout(
            yaxis_title="Tokens Used",
            xaxis_title="Time",
            height=350,
            showlegend=False
        )

        st.plotly_chart(fig_tokens, use_container_width=True)
    else:
        st.info("No token data available")

# Per-agent performance comparison
st.markdown("""
<div class="section-header">
    <h3>> Per-Agent Performance Comparison</h3>
</div>
""", unsafe_allow_html=True)

agent_performance = tracker.get_agent_performance_comparison()

if agent_performance:
    # Create comparison table
    df_agents = pd.DataFrame([
        {
            'Agent': agent.replace('_', ' ').title(),
            'Total Conversations': stats['total_conversations'],
            'Success Rate': f"{stats['success_rate']:.1%}",
            'Avg Latency (ms)': f"{stats['average_latency_ms']:.0f}",
            'Total Tokens': f"{stats['total_tokens']:,}",
            'Avg Feedback': f"{stats['average_feedback_score']:.1f}" if stats['average_feedback_score'] else "N/A"
        }
        for agent, stats in agent_performance.items()
    ])

    st.dataframe(df_agents, use_container_width=True, hide_index=True)

    # Agent comparison charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Success Rate by Agent")

        agent_names = [agent.replace('_', ' ').title() for agent in agent_performance.keys()]
        success_rates = [stats['success_rate'] * 100 for stats in agent_performance.values()]

        fig_agent_success = go.Figure(go.Bar(
            x=agent_names,
            y=success_rates,
            marker=dict(
                color=success_rates,
                colorscale='RdYlGn',
                showscale=False,
                cmin=0,
                cmax=100
            ),
            text=[f"{rate:.1f}%" for rate in success_rates],
            textposition='outside'
        ))

        fig_agent_success.update_layout(
            yaxis_title="Success Rate (%)",
            yaxis=dict(range=[0, 110]),
            height=300,
            showlegend=False
        )

        st.plotly_chart(fig_agent_success, use_container_width=True)

    with col2:
        st.markdown("#### Token Usage by Agent")

        token_counts = [stats['total_tokens'] for stats in agent_performance.values()]

        fig_agent_tokens = go.Figure(go.Bar(
            x=agent_names,
            y=token_counts,
            marker=dict(color='#007bff'),
            text=[f"{tokens:,}" for tokens in token_counts],
            textposition='outside'
        ))

        fig_agent_tokens.update_layout(
            yaxis_title="Total Tokens",
            height=300,
            showlegend=False
        )

        st.plotly_chart(fig_agent_tokens, use_container_width=True)

else:
    st.info("No agent performance data available yet")

# Recent conversations
st.markdown("""
<div class="section-header">
    <h3>=¬ Recent Conversations</h3>
</div>
""", unsafe_allow_html=True)

recent_convs = tracker.get_recent_conversations(limit=10, agent_type=agent_filter)

if recent_convs:
    for conv in recent_convs:
        with st.expander(
            f"{'' if conv.success else 'L'} {conv.agent_type.replace('_', ' ').title()} - {datetime.fromisoformat(conv.timestamp).strftime('%Y-%m-%d %H:%M:%S')}"
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**User**: {conv.user_message[:200]}...")
                st.markdown(f"**Agent**: {conv.agent_response[:200]}...")

            with col2:
                st.markdown(f"**Latency**: {conv.latency_ms:.0f}ms")
                st.markdown(f"**Tokens**: {conv.tokens_used}")
                st.markdown(f"**Tools Used**: {len(conv.tools_used)}")

                if conv.tools_used:
                    st.markdown("**Functions**:")
                    for tool in conv.tools_used:
                        st.markdown(f"- `{tool}`")

                if conv.feedback_score:
                    st.markdown(f"**Feedback**: {'P' * conv.feedback_score}")
else:
    st.info("No recent conversations available")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 0.85rem;">
    <p>Metrics Dashboard - Real-time monitoring of BSW AI Scheduling Agent performance</p>
</div>
""", unsafe_allow_html=True)
