import os
from datetime import date, timedelta

import pandas as pd
import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="PARKONIC AI ASSISTANT",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# GEMINI SETUP
# ---------------------------------------------------------
try:
    api_key = st.secrets.get("GOOGLE_API_KEY")
except Exception:
    api_key = None
api_key = api_key or os.getenv("GOOGLE_API_KEY")

model = None
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception:
        model = None

# ---------------------------------------------------------
# ---------------------------------------------------------
# LOAD CSS FROM SEPARATE FILE
# ---------------------------------------------------------
css_path = os.path.join(os.path.dirname(__file__), "style.css")
try:
    with open(css_path, "r", encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("style.css was not found. Keep it in the same folder as app.py.")

today = date.today()
demo_data = [
    {"Trip ID": "DEMO-1001", "Site": "WAFI MALL", "Review Category": "Plate review", "Status": "Approved", "Review Time (min)": 3, "Created": today - timedelta(days=0), "Priority": "Normal"},
    {"Trip ID": "DEMO-1002", "Site": "GLOBAL VILLAGE", "Review Category": "Wrong plate", "Status": "Pending", "Review Time (min)": 14, "Created": today - timedelta(days=0), "Priority": "High"},
    {"Trip ID": "DEMO-1003", "Site": "JVC", "Review Category": "Large amount", "Status": "Flagged", "Review Time (min)": 21, "Created": today - timedelta(days=0), "Priority": "High"},
    {"Trip ID": "DEMO-1004", "Site": "WAFI MALL", "Review Category": "Validation attempt", "Status": "Approved", "Review Time (min)": 4, "Created": today - timedelta(days=1), "Priority": "Normal"},
    {"Trip ID": "DEMO-1005", "Site": "WTC", "Review Category": "Location tenancy", "Status": "Pending", "Review Time (min)": 17, "Created": today - timedelta(days=1), "Priority": "Medium"},
    {"Trip ID": "DEMO-1006", "Site": "JVC", "Review Category": "Non-UAE plate", "Status": "Approved", "Review Time (min)": 5, "Created": today - timedelta(days=1), "Priority": "Normal"},
    {"Trip ID": "DEMO-1007", "Site": "GLOBAL VILLAGE", "Review Category": "Plate review", "Status": "Approved", "Review Time (min)": 2, "Created": today - timedelta(days=2), "Priority": "Normal"},
    {"Trip ID": "DEMO-1008", "Site": "WTC", "Review Category": "Wrong plate", "Status": "Pending", "Review Time (min)": 19, "Created": today - timedelta(days=2), "Priority": "High"},
    {"Trip ID": "DEMO-1009", "Site": "JVC", "Review Category": "Large amount", "Status": "Flagged", "Review Time (min)": 25, "Created": today - timedelta(days=3), "Priority": "High"},
    {"Trip ID": "DEMO-1010", "Site": "WTC", "Review Category": "Plate review", "Status": "Approved", "Review Time (min)": 3, "Created": today - timedelta(days=3), "Priority": "Normal"},
    {"Trip ID": "DEMO-1011", "Site": "WAFI MALL", "Review Category": "Validation attempt", "Status": "Pending", "Review Time (min)": 11, "Created": today - timedelta(days=4), "Priority": "Medium"},
    {"Trip ID": "DEMO-1012", "Site": "GLOBAL VILLAGE", "Review Category": "Non-UAE plate", "Status": "Approved", "Review Time (min)": 6, "Created": today - timedelta(days=4), "Priority": "Normal"},
]
df = pd.DataFrame(demo_data)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "Overview"

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-wrap">
            <span class="brand-mark">P</span>
            <span class="brand-name">PARKONIC</span>
            <div class="brand-caption">AI Operations Workspace</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("**WORKSPACE**")
    page = st.radio(
        "Navigation",
        ["Overview", "AI Assistant", "Trip Reviews"],
        label_visibility="collapsed",
        key="nav_page",
    )
    st.markdown("---")
    st.markdown("**SYSTEM STATUS**")
    if model:
        st.success("Gemini connection configured")
    else:
        st.warning("Gemini API key not configured")
    st.markdown("---")
    if st.button("＋ New chat", use_container_width=True):
        st.session_state.messages = []
        st.toast("Chat history cleared. Choose AI Assistant from the navigation to start chatting.")
        st.rerun()
    if st.button("Clear chat history", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Use selected sidebar page
page = st.session_state.nav_page

# Common demo banner
st.markdown(
    '<div class="demo-banner">⚠️ <b>DEMO ENVIRONMENT</b> — All trip records and metrics shown here are synthetic examples..</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# OVERVIEW DASHBOARD
# ---------------------------------------------------------
if page == "Overview":
    st.markdown('<div class="eyebrow">OPERATIONS OVERVIEW</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Parking review dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">A sample view of trip-review workload, quality signals, and case status.</div>', unsafe_allow_html=True)

    total = len(df)
    approved = int((df["Status"] == "Approved").sum())
    pending = int((df["Status"] == "Pending").sum())
    flagged = int((df["Status"] == "Flagged").sum())
    avg_review = round(float(df["Review Time (min)"].mean()), 1)
    approval_rate = round(approved / total * 100)

    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (c1, "SAMPLE TRIPS", f"{total:,}", "Synthetic demo records"),
        (c2, "APPROVED", f"{approved:,}", f"{approval_rate}% of sample trips"),
        (c3, "PENDING REVIEW", f"{pending:,}", "Needs a reviewer in this demo"),
        (c4, "FLAGGED CASES", f"{flagged:,}", f"Avg. review time: {avg_review} min"),
    ]
    for col, label, value, foot in metrics:
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-foot">{foot}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown('<div class="section-heading">Trip status distribution</div>', unsafe_allow_html=True)
        status_counts = df["Status"].value_counts().reindex(["Approved", "Pending", "Flagged"], fill_value=0)
        st.bar_chart(status_counts, color="#00A6A6", height=270)
    with right:
        st.markdown('<div class="section-heading">Review cases by category</div>', unsafe_allow_html=True)
        category_counts = df["Review Category"].value_counts().sort_values(ascending=True)
        st.bar_chart(category_counts, color="#183650", height=270)

    st.write("")
    st.markdown('<div class="section-heading">Recent sample cases</div>', unsafe_allow_html=True)
    recent = df[["Trip ID", "Site", "Review Category", "Status", "Priority"]].head(6)
    st.dataframe(recent, use_container_width=True, hide_index=True)
    st.caption("Metrics and records above are illustrative only; they do not represent actual operating performance.")

# ---------------------------------------------------------
# AI ASSISTANT
elif page == "AI Assistant":
    st.markdown('<div class="eyebrow">AI SUPPORT</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">PARKONIC AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Ask questions about parking support workflows, review categories, and general troubleshooting.</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="panel">
            <b style="color:#10243A;font-size:16px;">How can I help you today?</b>
            <p style="color:#6B7C8F;font-size:13px;margin-bottom:0;">
            Use the suggested prompts below to explore this demo. Do not enter customer personal data, real plate numbers, or confidential company information.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    q1, q2, q3 = st.columns(3)
    if q1.button("Explain wrong-plate reviews", use_container_width=True):
        st.session_state.pending_prompt = "Explain a safe, general workflow for reviewing a possible wrong number-plate OCR result."
    if q2.button("Prioritise pending trips", use_container_width=True):
        st.session_state.pending_prompt = "Suggest a general method to prioritise pending parking trips when a submission deadline is approaching."
    if q3.button("Reduce manual review", use_container_width=True):
        st.session_state.pending_prompt = "Suggest practical ways to reduce manual parking-trip review while keeping uncertain cases with human reviewers."

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    typed_prompt = st.chat_input("Ask a question about parking support...")
    pending_prompt = st.session_state.pop("pending_prompt", None)
    user_input = typed_prompt or pending_prompt

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Preparing a response..."):
                if not model:
                    reply = (
                        "Gemini is not configured. Add GOOGLE_API_KEY to "
                        "`.streamlit/secrets.toml` or your environment variables, then restart the app."
                    )
                else:
                    history = "\n".join(
                        f"{m['role'].upper()}: {m['content']}"
                        for m in st.session_state.messages[-12:]
                    )
                    prompt = f"""
You are PARKONIC AI Assistant, a helpful demo assistant for general parking operations support.
Be clear, practical, concise, and beginner-friendly.
Do not claim access to live Parkonic systems, customer records, cameras, or Salik.
Do not invent company policies or approve real trips. For uncertain, financial, plate-recognition,
or compliance cases, recommend authorised human review.
Use only the conversation below as context; the app uses synthetic demo data.

Conversation:
{history}

Assistant:
"""
                    try:
                        response = model.generate_content(prompt)
                        reply = response.text or "I couldn't generate a response. Please try again."
                    except Exception as exc:
                        reply = f"Gemini request failed: {exc}"

                st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# ---------------------------------------------------------
# TRIP REVIEWS
# ---------------------------------------------------------
elif page == "Trip Reviews":
    st.markdown('<div class="eyebrow">CASE MANAGEMENT</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Trip review queue</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Filter and inspect synthetic examples of parking review cases.</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        statuses = st.multiselect("Status", sorted(df["Status"].unique()), default=sorted(df["Status"].unique()))
    with f2:
        categories = st.multiselect("Review category", sorted(df["Review Category"].unique()), default=sorted(df["Review Category"].unique()))
    with f3:
        sites = st.multiselect("Site", sorted(df["Site"].unique()), default=sorted(df["Site"].unique()))

    filtered = df[
        df["Status"].isin(statuses)
        & df["Review Category"].isin(categories)
        & df["Site"].isin(sites)
    ].copy()

    st.markdown(f"**{len(filtered)}** sample cases match your filters.")
    st.dataframe(
        filtered[["Trip ID", "Created", "Site", "Review Category", "Status", "Priority", "Review Time (min)"]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown('<div class="section-heading">Review a sample case</div>', unsafe_allow_html=True)
    if not filtered.empty:
        selected_id = st.selectbox("Choose a demo trip ID", filtered["Trip ID"].tolist())
        selected = filtered[filtered["Trip ID"] == selected_id].iloc[0]
        a, b = st.columns([1, 2])
        with a:
            st.markdown(
                f"""
                <div class="panel">
                    <div class="metric-label">DEMO TRIP ID</div>
                    <div style="font-size:21px;font-weight:800;color:#10243A;">{selected['Trip ID']}</div>
                    <p style="color:#6B7C8F;margin:12px 0 4px;">Site: <b>{selected['Site']}</b></p>
                    <p style="color:#6B7C8F;margin:4px 0;">Status: <b>{selected['Status']}</b></p>
                    <p style="color:#6B7C8F;margin:4px 0;">Priority: <b>{selected['Priority']}</b></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with b:
            st.info(
                f"Category: **{selected['Review Category']}** · "
                f"Illustrative review time: **{selected['Review Time (min)']} minutes**"
            )
            st.warning("Demo only: this screen does not approve, reject, or submit any real trip.")
            st.text_area(
                "Reviewer notes (demo)",
                key=f"notes_{selected_id}",
                placeholder="Enter a sample note for this demonstration...",
            )
    else:
        st.info("No sample cases match the selected filters. Adjust the filters to see records.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.caption("PARKONIC AI ASSISTANT · Prototype interface · Synthetic data only · Not connected to production systems")
