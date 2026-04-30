"""
SentraX IDS – Streamlit Dashboard
===================================
Premium UI for real-time intrusion detection with explainable AI.

Run:  streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

from model import SentraXModel, run_pipeline

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SentraX IDS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS (dark theme, glassmorphism)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1321 40%, #121a2e 100%);
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1729 0%, #131d35 100%);
        border-right: 1px solid rgba(99, 179, 237, 0.15);
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e2e8f0;
    }

    /* ── Glass Cards ── */
    .glass-card {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(99, 179, 237, 0.12);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    /* ── Header ── */
    .sentrax-header {
        text-align: center;
        padding: 40px 20px 30px;
        margin-bottom: 10px;
    }
    .sentrax-header h1 {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #63b3ed, #7c3aed, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    .sentrax-header p {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 400;
    }

    /* ── Metric cards ── */
    .metric-row {
        display: flex;
        gap: 16px;
        margin-bottom: 24px;
    }
    .metric-card {
        flex: 1;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(99, 179, 237, 0.1);
        border-radius: 14px;
        padding: 22px 24px;
        text-align: center;
    }
    .metric-card .label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #64748b;
        margin-bottom: 8px;
    }
    .metric-card .value {
        font-size: 1.7rem;
        font-weight: 700;
    }
    .metric-card .value.normal  { color: #34d399; }
    .metric-card .value.attack  { color: #f87171; }
    .metric-card .value.conf    { color: #63b3ed; }

    /* ── Alert banner ── */
    .alert-banner {
        border-radius: 14px;
        padding: 20px 28px;
        text-align: center;
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 24px;
        letter-spacing: 0.3px;
    }
    .alert-normal {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(52, 211, 153, 0.35);
        color: #34d399;
    }
    .alert-attack {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(248, 113, 113, 0.35);
        color: #f87171;
        animation: pulse-attack 2s ease-in-out infinite;
    }
    @keyframes pulse-attack {
        0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        50%      { box-shadow: 0 0 24px 4px rgba(239, 68, 68, 0.15); }
    }

    /* ── Section titles ── */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 12px;
        padding-left: 2px;
    }

    /* ── Feature table ── */
    .feat-table {
        width: 100%;
        border-collapse: collapse;
    }
    .feat-table th {
        text-align: left;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #64748b;
        padding: 8px 12px;
        border-bottom: 1px solid rgba(99, 179, 237, 0.08);
    }
    .feat-table td {
        padding: 10px 12px;
        font-size: 0.88rem;
        color: #cbd5e1;
        border-bottom: 1px solid rgba(99, 179, 237, 0.04);
    }
    .feat-table tr:hover td {
        background: rgba(99, 179, 237, 0.04);
    }

    /* ── Streamlit overrides ── */
    .stNumberInput label, .stSelectbox label {
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stNumberInput"] input {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(99, 179, 237, 0.2) !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.35) !important;
    }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD MODEL (cached)
# ─────────────────────────────────────────────
@st.cache_resource
def load_model():
    return SentraXModel().load()


try:
    sentrax = load_model()
except FileNotFoundError:
    st.error("⚠️ Model not found. Please run `python train.py` first.")
    st.stop()


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="sentrax-header">
    <h1>🛡️ SentraX IDS</h1>
    <p>Explainable AI-Powered Intrusion Detection System</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR — INPUT PANEL
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔧 Network Traffic Input")
    st.markdown("---")

    # Feature configs: (label, min, max, default, step, help)
    # Note: Using 0.0-1.0 range as the real dataset is already normalized
    FEATURE_CONFIG = {
        "duration":           ("Duration (scaled)",       0.0,  1.0,  0.1,  0.01, "Connection duration (scaled)"),
        "src_bytes":          ("Source Bytes (scaled)",   0.0,  1.0,  0.2,  0.01, "Bytes from source (scaled)"),
        "dst_bytes":          ("Dest Bytes (scaled)",     0.0,  1.0,  0.2,  0.01, "Bytes from destination (scaled)"),
        "num_failed_logins":  ("Failed Logins (scaled)",  0.0,  1.0,  0.0,  0.01, "Failed login attempts (scaled)"),
        "num_file_creations": ("Files Created (scaled)",  0.0,  1.0,  0.0,  0.01, "Files created (scaled)"),
        "num_shells":         ("Shell Commands (scaled)", 0.0,  1.0,  0.0,  0.01, "Shell commands (scaled)"),
        "is_guest_login":     ("Guest Login (scaled)",    0.0,  1.0,  0.0,  0.01, "Guest login flag (scaled)"),
        "count":              ("Connection Count (scaled)", 0.0, 1.0, 0.1, 0.01, "Connections to same host (scaled)"),
        "srv_count":          ("Service Count (scaled)",  0.0,  1.0,  0.1,  0.01, "Connections to same service (scaled)"),
        "dst_host_count":     ("Dest Host Count (scaled)", 0.0, 1.0, 0.5, 0.01, "Connections to dest host (scaled)"),
    }

    raw_input = {}
    for feat_key, (label, mn, mx, default, step, help_text) in FEATURE_CONFIG.items():
        raw_input[feat_key] = st.number_input(
            label, min_value=mn, max_value=mx, value=default,
            step=step, help=help_text, key=feat_key
        )

    st.markdown("---")

    # Preset buttons
    st.markdown("#### ⚡ Quick Presets")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        load_normal = st.button("🟢 Normal", use_container_width=True)
    with col_p2:
        load_attack = st.button("🔴 Attack", use_container_width=True)

    if load_normal:
        st.session_state["duration"]           = 0.14
        st.session_state["src_bytes"]          = 0.05
        st.session_state["dst_bytes"]          = 0.29
        st.session_state["num_failed_logins"]  = 0.51
        st.session_state["num_file_creations"] = 0.76
        st.session_state["num_shells"]         = 0.35
        st.session_state["is_guest_login"]     = 0.87
        st.session_state["count"]              = 0.13
        st.session_state["srv_count"]          = 0.32
        st.session_state["dst_host_count"]     = 0.92
        st.rerun()

    if load_attack:
        st.session_state["duration"]           = 0.66
        st.session_state["src_bytes"]          = 0.15
        st.session_state["dst_bytes"]          = 0.44
        st.session_state["num_failed_logins"]  = 0.39
        st.session_state["num_file_creations"] = 0.86
        st.session_state["num_shells"]         = 0.28
        st.session_state["is_guest_login"]     = 0.73
        st.session_state["count"]              = 0.90
        st.session_state["srv_count"]          = 0.81
        st.session_state["dst_host_count"]     = 0.25
        st.rerun()

    st.markdown("---")
    detect = st.button("🔍  Detect Intrusion", use_container_width=True)


# ─────────────────────────────────────────────
# MAIN AREA – RESULTS & MONITORING
# ─────────────────────────────────────────────

# Initialize session state for the live feed if it doesn't exist
if "live_feed" not in st.session_state:
    st.session_state.live_feed = [
        {"time": "16:40:12", "event": "System Heartbeat", "status": "SECURE", "ip": "192.168.1.1"},
        {"time": "16:41:05", "event": "Port Scan Detected", "status": "ATTACK", "ip": "45.33.78.12"},
        {"time": "16:42:30", "event": "SSH Login Attempt", "status": "SECURE", "ip": "10.0.0.15"},
    ]

# Layout for the dashboard
tab1, tab2 = st.tabs(["🔍 Analysis Engine", "📡 Live Monitor"])

with tab1:
    if detect:
        with st.spinner("Analyzing network traffic..."):
            result = run_pipeline(raw_input, sentrax)

        label      = result["label"]
        confidence = result["confidence"]
        probas     = result["probas"]
        shap_df    = result["shap_df"]
        is_attack  = label == "Attack"

        # Update live feed with new prediction
        import datetime
        new_entry = {
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "event": f"Manual Inspection: {label}",
            "status": "ATTACK" if is_attack else "SECURE",
            "ip": "Local/User"
        }
        st.session_state.live_feed.insert(0, new_entry)
        st.session_state.live_feed = st.session_state.live_feed[:10] # Keep last 10

        # ── Alert Banner ──
        if is_attack:
            st.toast("🚨 CRITICAL: Intrusion Detected!", icon="🔥")
            st.markdown(
                '<div class="alert-banner alert-attack">'
                '🚨 THREAT DETECTED — Intrusion signature identified'
                '</div>', unsafe_allow_html=True
            )
        else:
            st.toast("✅ Analysis Complete: Traffic is Secure", icon="🛡️")
            st.markdown(
                '<div class="alert-banner alert-normal">'
                '✅ ALL CLEAR — Traffic appears normal'
                '</div>', unsafe_allow_html=True
            )

        # ── Metric Cards ──
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="label">Verdict</div>
                <div class="value {'attack' if is_attack else 'normal'}">{label}</div>
            </div>
            <div class="metric-card">
                <div class="label">Confidence</div>
                <div class="value conf">{confidence:.1%}</div>
            </div>
            <div class="metric-card">
                <div class="label">P(Normal)</div>
                <div class="value normal">{probas[0]:.1%}</div>
            </div>
            <div class="metric-card">
                <div class="label">P(Attack)</div>
                <div class="value attack">{probas[1]:.1%}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ... (rest of the charts remain the same, adding them inside tab1)
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🔬 SHAP Feature Impact</div>', unsafe_allow_html=True)
            df_sorted = shap_df.sort_values("Abs SHAP", ascending=True)
            colors = ["#f87171" if v > 0 else "#34d399" for v in df_sorted["SHAP Value"]]
            fig_shap = go.Figure(go.Bar(x=df_sorted["SHAP Value"], y=df_sorted["Feature"], orientation="h", marker=dict(color=colors, line=dict(width=0), cornerradius=4)))
            fig_shap.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", family="Inter", size=12), xaxis=dict(title="SHAP Value", gridcolor="rgba(99,179,237,0.06)", zerolinecolor="rgba(99,179,237,0.15)"), yaxis=dict(gridcolor="rgba(0,0,0,0)"), margin=dict(l=10, r=10, t=10, b=40), height=400)
            st.plotly_chart(fig_shap, use_container_width=True, key="shap_chart")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📊 Global Feature Importance</div>', unsafe_allow_html=True)
            df_global = shap_df.sort_values("Global Importance %", ascending=True)
            fig_global = go.Figure(go.Bar(x=df_global["Global Importance %"], y=df_global["Feature"], orientation="h", marker=dict(color=px.colors.sequential.Plasma_r[:len(df_global)], line=dict(width=0), cornerradius=4)))
            fig_global.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", family="Inter", size=12), xaxis=dict(title="Importance (%)", gridcolor="rgba(99,179,237,0.06)"), yaxis=dict(gridcolor="rgba(0,0,0,0)"), margin=dict(l=10, r=10, t=10, b=40), height=400)
            st.plotly_chart(fig_global, use_container_width=True, key="global_chart")
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:60px 40px;">
            <div style="font-size:3.5rem; margin-bottom:16px;">🛡️</div>
            <div style="font-size:1.3rem; font-weight:600; color:#e2e8f0; margin-bottom:10px;">Ready to Analyze</div>
            <div style="color:#64748b; font-size:0.95rem; max-width:500px; margin:0 auto; line-height:1.7;">
                Configure network traffic parameters in the sidebar and click <strong style="color:#a78bfa;">Detect Intrusion</strong>.
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📡 Real-Time Traffic Feed</div>', unsafe_allow_html=True)
    
    # Custom CSS for the feed
    st.markdown("""
    <style>
    .feed-entry {
        display: flex;
        justify-content: space-between;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        background: rgba(255,255,255,0.03);
        border-left: 4px solid #63b3ed;
    }
    .feed-entry.attack { border-left-color: #f87171; background: rgba(248,113,113,0.05); }
    .feed-entry.secure { border-left-color: #34d399; background: rgba(52,211,153,0.05); }
    .feed-time { color: #64748b; font-family: monospace; font-size: 0.85rem; }
    .feed-event { color: #e2e8f0; font-weight: 500; }
    .feed-status { font-weight: 700; font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; }
    .status-attack { background: #f87171; color: #1e1b4b; }
    .status-secure { background: #34d399; color: #064e3b; }
    </style>
    """, unsafe_allow_html=True)

    for entry in st.session_state.live_feed:
        status_class = "attack" if entry["status"] == "ATTACK" else "secure"
        st.markdown(f"""
        <div class="feed-entry {status_class}">
            <div>
                <span class="feed-time">[{entry['time']}]</span>
                <span class="feed-event" style="margin-left:12px;">{entry['event']}</span>
                <div style="font-size:0.75rem; color:#64748b; margin-top:4px;">Source IP: {entry['ip']}</div>
            </div>
            <div style="display:flex; align-items:center;">
                <span class="feed-status status-{status_class}">{entry['status']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Anomaly Visualization
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📉 Network Traffic Anomalies (Simulated)</div>', unsafe_allow_html=True)
    
    import random
    chart_data = pd.DataFrame({
        'time': range(20),
        'traffic': [random.randint(100, 300) for _ in range(20)]
    })
    # Add a spike
    chart_data.loc[15, 'traffic'] = 850
    
    fig_line = px.line(chart_data, x='time', y='traffic', template="plotly_dark")
    fig_line.update_traces(line_color='#63b3ed', line_width=3)
    fig_line.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(99,179,237,0.05)"),
        height=300,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

