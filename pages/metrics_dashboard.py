"""
Metrics Dashboard - Analytics and performance monitoring for BSW Scheduling Agent.

This page provides comprehensive analytics including:
- Conversation success rates and quality scores
- Tool usage statistics
- Performance metrics (latency, tokens)
- Per-agent comparison
- Time-filtered views
- Export capabilities
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import random

# Page configuration
st.set_page_config(
    page_title="Metrics Dashboard - BSW Scheduling Agent",
    page_icon="",
    layout="wide"
)

# Helper functions for mock data
def generate_mock_metrics(time_filter: str = "all") -> Dict[str, Any]:
    """
    Generate realistic mock metrics data.

    In production, this would pull from actual metrics tracker.
    For demo purposes, we generate representative data.
    """

    # Determine number of data points based on time filter
    time_ranges = {
        "1h": 6,
        "6h": 12,
        "24h": 24,
        "7d": 7,
        "all": 30
    }

    num_points = time_ranges.get(time_filter, 30)

    # Generate time series data
    now = datetime.now()
    timestamps = []

    if time_filter == "1h":
        timestamps = [now - timedelta(minutes=i*10) for i in range(num_points)]
    elif time_filter == "6h":
        timestamps = [now - timedelta(minutes=i*30) for i in range(num_points)]
    elif time_filter == "24h":
        timestamps = [now - timedelta(hours=i) for i in range(num_points)]
    elif time_filter == "7d":
        timestamps = [now - timedelta(days=i) for i in range(num_points)]
    else:
        timestamps = [now - timedelta(days=i) for i in range(num_points)]

    timestamps.reverse()

    # Generate success rates over time (trending upward)
    success_rates = []
    base_rate = 0.70
    for i in range(num_points):
        trend = (i / num_points) * 0.15  # Improvement over time
        noise = random.uniform(-0.05, 0.05)
        rate = min(0.95, base_rate + trend + noise)
        success_rates.append(round(rate, 3))

    # Generate tool usage data
    tools = [
        "search_appointment_slots",
        "verify_insurance",
        "check_provider_availability",
        "book_appointment",
        "check_referral_status",
        "get_patient_info",
        "get_clinical_protocol"
    ]

    tool_usage = {
        tool: random.randint(15, 85) for tool in tools
    }

    # Sort by usage
    tool_usage = dict(sorted(tool_usage.items(), key=lambda x: x[1], reverse=True))

    # Latency distribution
    latencies = [round(random.gauss(2.5, 0.8), 2) for _ in range(50)]
    latencies = [max(0.5, min(6.0, l)) for l in latencies]  # Clamp values

    # Per-agent metrics
    agents = {
        "Router Agent": {
            "invocations": random.randint(80, 120),
            "success_rate": round(random.uniform(0.88, 0.95), 3),
            "avg_latency": round(random.uniform(1.2, 2.0), 2),
            "avg_tokens": random.randint(200, 400)
        },
        "Orthopedic Specialist": {
            "invocations": random.randint(30, 50),
            "success_rate": round(random.uniform(0.82, 0.92), 3),
            "avg_latency": round(random.uniform(2.5, 3.5), 2),
            "avg_tokens": random.randint(600, 900)
        },
        "Cardiology Specialist": {
            "invocations": random.randint(25, 45),
            "success_rate": round(random.uniform(0.80, 0.90), 3),
            "avg_latency": round(random.uniform(2.3, 3.2), 2),
            "avg_tokens": random.randint(550, 850)
        },
        "Primary Care Specialist": {
            "invocations": random.randint(35, 55),
            "success_rate": round(random.uniform(0.85, 0.93), 3),
            "avg_latency": round(random.uniform(2.0, 2.8), 2),
            "avg_tokens": random.randint(400, 700)
        }
    }

    total_conversations = sum(agent["invocations"] for agent in agents.values())
    total_tokens = sum(agent["invocations"] * agent["avg_tokens"] for agent in agents.values())
    overall_success_rate = sum(
        agent["invocations"] * agent["success_rate"] for agent in agents.values()
    ) / total_conversations
    avg_latency = sum(
        agent["invocations"] * agent["avg_latency"] for agent in agents.values()
    ) / total_conversations

    return {
        "summary": {
            "total_conversations": total_conversations,
            "success_rate": round(overall_success_rate, 3),
            "avg_latency": round(avg_latency, 2),
            "total_tokens": total_tokens,
            "estimated_cost": round(total_tokens / 1_000_000 * 0.15, 4)
        },
        "time_series": {
            "timestamps": [t.isoformat() for t in timestamps],
            "success_rates": success_rates
        },
        "tool_usage": tool_usage,
        "latencies": latencies,
        "agent_performance": agents
    }

# Page header
st.markdown("""
<div style="background: linear-gradient(135deg, #00447c 0%, #00a4e4 100%);
            padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;"> Metrics Dashboard</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
        Real-time analytics and performance monitoring
    </p>
</div>
""", unsafe_allow_html=True)

# Time filter selector
st.markdown("### Time Range")
col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 2])

with col1:
    time_1h = st.button("Last 1 Hour", use_container_width=True)
with col2:
    time_6h = st.button("Last 6 Hours", use_container_width=True)
with col3:
    time_24h = st.button("Last 24 Hours", use_container_width=True)
with col4:
    time_7d = st.button("Last 7 Days", use_container_width=True)
with col5:
    time_all = st.button("All Time", use_container_width=True)

# Determine selected time filter
if time_1h:
    time_filter = "1h"
elif time_6h:
    time_filter = "6h"
elif time_24h:
    time_filter = "24h"
elif time_7d:
    time_filter = "7d"
elif time_all:
    time_filter = "all"
else:
    time_filter = "24h"  # Default

st.info(f" Showing metrics for: **{time_filter.upper()}**")

# Generate metrics
metrics = generate_mock_metrics(time_filter)

st.markdown("---")

# Overview cards
st.markdown("### Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Conversations",
        value=metrics["summary"]["total_conversations"],
        delta=f"+{random.randint(5, 15)} from last period"
    )

with col2:
    st.metric(
        label="Success Rate",
        value=f"{metrics['summary']['success_rate'] * 100:.1f}%",
        delta=f"+{random.uniform(1.5, 3.5):.1f}%"
    )

with col3:
    st.metric(
        label="Avg Latency",
        value=f"{metrics['summary']['avg_latency']:.2f}s",
        delta=f"-{random.uniform(0.1, 0.3):.2f}s",
        delta_color="inverse"
    )

with col4:
    st.metric(
        label="Total Tokens",
        value=f"{metrics['summary']['total_tokens']:,}",
        delta=f"+{random.randint(5000, 15000):,}"
    )

st.markdown("---")

# Success rate over time chart
st.markdown("### Success Rate Trend")

fig_success = go.Figure()

fig_success.add_trace(go.Scatter(
    x=metrics["time_series"]["timestamps"],
    y=[rate * 100 for rate in metrics["time_series"]["success_rates"]],
    mode='lines+markers',
    name='Success Rate',
    line=dict(color='#00a4e4', width=3),
    marker=dict(size=8, color='#00447c'),
    fill='tozeroy',
    fillcolor='rgba(0, 164, 228, 0.1)'
))

fig_success.update_layout(
    xaxis_title="Time",
    yaxis_title="Success Rate (%)",
    yaxis_range=[0, 100],
    hovermode='x unified',
    height=400,
    template="plotly_white"
)

st.plotly_chart(fig_success, use_container_width=True)

st.markdown("---")

# Tool usage and latency charts side by side
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Tool Usage Frequency")

    tool_names = list(metrics["tool_usage"].keys())
    tool_counts = list(metrics["tool_usage"].values())

    # Shorten tool names for display
    tool_names_short = [name.replace('_', ' ').title() for name in tool_names]

    fig_tools = go.Figure(data=[
        go.Bar(
            x=tool_counts,
            y=tool_names_short,
            orientation='h',
            marker=dict(
                color=tool_counts,
                colorscale='Blues',
                showscale=False
            ),
            text=tool_counts,
            textposition='auto',
        )
    ])

    fig_tools.update_layout(
        xaxis_title="Number of Calls",
        yaxis_title="",
        height=500,
        template="plotly_white",
        margin=dict(l=200)
    )

    st.plotly_chart(fig_tools, use_container_width=True)

with col2:
    st.markdown("### Response Latency Distribution")

    fig_latency = go.Figure(data=[
        go.Histogram(
            x=metrics["latencies"],
            nbinsx=20,
            marker=dict(
                color='#00a4e4',
                line=dict(color='#00447c', width=1)
            ),
            name='Latency'
        )
    ])

    fig_latency.update_layout(
        xaxis_title="Response Time (seconds)",
        yaxis_title="Frequency",
        height=500,
        template="plotly_white",
        showlegend=False
    )

    # Add median line
    median_latency = sorted(metrics["latencies"])[len(metrics["latencies"]) // 2]
    fig_latency.add_vline(
        x=median_latency,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Median: {median_latency:.2f}s",
        annotation_position="top"
    )

    st.plotly_chart(fig_latency, use_container_width=True)

st.markdown("---")

# Per-agent performance comparison
st.markdown("### Per-Agent Performance Comparison")

agent_names = list(metrics["agent_performance"].keys())
agent_data = metrics["agent_performance"]

# Create comparison table
st.markdown("#### Performance Table")

import pandas as pd

df_agents = pd.DataFrame({
    "Agent": agent_names,
    "Invocations": [agent_data[a]["invocations"] for a in agent_names],
    "Success Rate": [f"{agent_data[a]['success_rate'] * 100:.1f}%" for a in agent_names],
    "Avg Latency (s)": [f"{agent_data[a]['avg_latency']:.2f}" for a in agent_names],
    "Avg Tokens": [f"{agent_data[a]['avg_tokens']:,}" for a in agent_names],
    "Total Tokens": [
        f"{agent_data[a]['invocations'] * agent_data[a]['avg_tokens']:,}"
        for a in agent_names
    ]
})

st.dataframe(df_agents, use_container_width=True, hide_index=True)

# Agent comparison charts
st.markdown("#### Visual Comparison")

col1, col2 = st.columns(2)

with col1:
    # Success rate comparison
    fig_agent_success = go.Figure(data=[
        go.Bar(
            x=agent_names,
            y=[agent_data[a]["success_rate"] * 100 for a in agent_names],
            marker=dict(color=['#00447c', '#00a4e4', '#00cc88', '#ffb81c']),
            text=[f"{agent_data[a]['success_rate'] * 100:.1f}%" for a in agent_names],
            textposition='auto'
        )
    ])

    fig_agent_success.update_layout(
        title="Success Rate by Agent",
        xaxis_title="Agent",
        yaxis_title="Success Rate (%)",
        yaxis_range=[0, 100],
        height=400,
        template="plotly_white",
        showlegend=False
    )

    st.plotly_chart(fig_agent_success, use_container_width=True)

with col2:
    # Latency comparison
    fig_agent_latency = go.Figure(data=[
        go.Bar(
            x=agent_names,
            y=[agent_data[a]["avg_latency"] for a in agent_names],
            marker=dict(color=['#00447c', '#00a4e4', '#00cc88', '#ffb81c']),
            text=[f"{agent_data[a]['avg_latency']:.2f}s" for a in agent_names],
            textposition='auto'
        )
    ])

    fig_agent_latency.update_layout(
        title="Average Latency by Agent",
        xaxis_title="Agent",
        yaxis_title="Latency (seconds)",
        height=400,
        template="plotly_white",
        showlegend=False
    )

    st.plotly_chart(fig_agent_latency, use_container_width=True)

st.markdown("---")

# Export section
st.markdown("### Export Data")

col1, col2, col3 = st.columns([2, 2, 6])

with col1:
    if st.button(" Export JSON", use_container_width=True):
        # Create export data
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "time_filter": time_filter,
            "metrics": metrics
        }

        # Convert to JSON
        json_str = json.dumps(export_data, indent=2)

        # Provide download
        st.download_button(
            label="Download Metrics JSON",
            data=json_str,
            file_name=f"bsw_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

with col2:
    if st.button(" Export CSV", use_container_width=True):
        # Export agent performance as CSV
        csv_str = df_agents.to_csv(index=False)

        st.download_button(
            label="Download Agent Comparison CSV",
            data=csv_str,
            file_name=f"bsw_agent_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Additional insights
st.markdown("---")

st.markdown("### Key Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **Most Used Tool**

    `{list(metrics['tool_usage'].keys())[0]}`

    Used {list(metrics['tool_usage'].values())[0]} times
    """)

with col2:
    best_agent = max(
        agent_names,
        key=lambda a: agent_data[a]["success_rate"]
    )

    st.success(f"""
    **Top Performing Agent**

    {best_agent}

    {agent_data[best_agent]["success_rate"] * 100:.1f}% success rate
    """)

with col3:
    fastest_agent = min(
        agent_names,
        key=lambda a: agent_data[a]["avg_latency"]
    )

    st.info(f"""
    **Fastest Agent**

    {fastest_agent}

    {agent_data[fastest_agent]["avg_latency"]:.2f}s avg latency
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
    <p>BSW Health AI Scheduling Agent - Metrics Dashboard</p>
    <p style="font-size: 0.8rem;">
        Dashboard displays mock/demo data. In production, this would connect to real metrics tracking system.
    </p>
</div>
""", unsafe_allow_html=True)
