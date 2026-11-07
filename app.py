import os
from pathlib import Path
from datetime import date, timedelta

from PIL import Image

import pandas as pd
import streamlit as st
from google import genai

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
        model = genai.Client(api_key=api_key)
    except Exception as exc:
        st.warning(f"Gemini setup failed: {exc}")

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
    {"Trip ID": "DEMO-1002", "Site": "GLOBAL VILLAGE", "Review Category": "Wrong plate", "Status": "Pending", "Review Time (min)": 3, "Created": today - timedelta(days=0), "Priority": "High"},
    {"Trip ID": "DEMO-1003", "Site": "JVC", "Review Category": "Large amount", "Status": "Flagged", "Review Time (min)": 2, "Created": today - timedelta(days=0), "Priority": "High"},
    {"Trip ID": "DEMO-1004", "Site": "WAFI MALL", "Review Category": "Validation attempt", "Status": "Approved", "Review Time (min)": 3, "Created": today - timedelta(days=1), "Priority": "Normal"},
    {"Trip ID": "DEMO-1005", "Site": "WTC", "Review Category": "Location tenancy", "Status": "Pending", "Review Time (min)": 1, "Created": today - timedelta(days=1), "Priority": "Medium"},
    {"Trip ID": "DEMO-1006", "Site": "JVC", "Review Category": "Non-UAE plate", "Status": "Approved", "Review Time (min)": 2, "Created": today - timedelta(days=1), "Priority": "Normal"},
    {"Trip ID": "DEMO-1007", "Site": "GLOBAL VILLAGE", "Review Category": "Plate review", "Status": "Approved", "Review Time (min)": 2, "Created": today - timedelta(days=2), "Priority": "Normal"},
    {"Trip ID": "DEMO-1008", "Site": "WTC", "Review Category": "Wrong plate", "Status": "Pending", "Review Time (min)": 1, "Created": today - timedelta(days=2), "Priority": "High"},
    {"Trip ID": "DEMO-1009", "Site": "JVC", "Review Category": "Large amount", "Status": "Flagged", "Review Time (min)": 2, "Created": today - timedelta(days=3), "Priority": "High"},
    {"Trip ID": "DEMO-1010", "Site": "WTC", "Review Category": "Plate review", "Status": "Approved", "Review Time (min)": 2, "Created": today - timedelta(days=3), "Priority": "Normal"},
    {"Trip ID": "DEMO-1011", "Site": "WAFI MALL", "Review Category": "Validation attempt", "Status": "Pending", "Review Time (min)": 1, "Created": today - timedelta(days=4), "Priority": "Medium"},
    {"Trip ID": "DEMO-1012", "Site": "GLOBAL VILLAGE", "Review Category": "Non-UAE plate", "Status": "Approved", "Review Time (min)": 2, "Created": today - timedelta(days=4), "Priority": "Normal"},
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
        ["Overview", "AI Assistant", "Trip Reviews", "Number Plate OCR"],
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
                        response = model.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                        )
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
# NUMBER PLATE OCR (DEMO / HUMAN-VERIFIED)
# ---------------------------------------------------------
elif page == "Number Plate OCR":
    st.markdown('<div class="eyebrow">COMPUTER VISION</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">UAE Number Plate Reader</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Prototype: detect a plate with an optional trained YOLO model, then read the characters. Verify every result manually.</div>',
        unsafe_allow_html=True,
    )
    st.info(
        "Demo only. This page does not connect to Parkonic production systems or Salik, "
        "and it never submits or approves a trip. Use only images you are authorised to process."
    )

    uploaded_file = st.file_uploader(
        "Upload a vehicle or number-plate image",
        type=["jpg", "jpeg", "png", "webp"],
        help="Use a permitted test image. Avoid uploading personal or confidential data.",
    )

    if uploaded_file is not None:
        try:
            original_image = Image.open(uploaded_file).convert("RGB")
            st.image(original_image, caption="Uploaded test image", use_container_width=True)
            image_for_reading = original_image
            detection_status = "Not run"
            model_path = Path(__file__).parent / "models" / "best.pt"

            # Optional trained detector: place your fine-tuned YOLO weights at models/best.pt.
            if model_path.exists():
                try:
                    from ultralytics import YOLO
                    detector = YOLO(str(model_path))
                    detector.names[6] = "RAK"
                    detector.names[8] = "UAQ"
                    prediction = detector.predict(source=original_image, conf=0.25, verbose=False)
                    boxes = prediction[0].boxes
                    if boxes is not None and len(boxes) > 0:
                        # Use the highest-confidence detected plate and crop it for recognition.
                        best_index = int(boxes.conf.argmax().item())
                        x1, y1, x2, y2 = [int(v) for v in boxes.xyxy[best_index].tolist()]
                        x1 = max(0, x1); y1 = max(0, y1)
                        x2 = min(original_image.width, x2); y2 = min(original_image.height, y2)
                        if x2 > x1 and y2 > y1:
                            image_for_reading = original_image
                            detection_status = "Plate detected by your trained YOLO model"
                            st.image(image_for_reading, caption="Detected plate crop", width=420)
                        else:
                            detection_status = "Detector returned an invalid crop; using the full image"
                    else:
                        detection_status = "No plate detected; using the full image for a best-effort read"
                except ImportError:
                    detection_status = "YOLO weights found, but ultralytics is not installed; using full image"
                except Exception as detector_error:
                    detection_status = f"Detector could not run ({type(detector_error).__name__}); using full image"
            else:
                detection_status = "No trained detector found at models/best.pt; Gemini will inspect the full image"

            st.caption(f"Detection status: {detection_status}")

            if st.button("Read number plate", type="primary", use_container_width=False):
                if not model:
                    st.error("Gemini is not configured. Add GOOGLE_API_KEY to Streamlit Cloud Secrets or .streamlit/secrets.toml.")
                else:
                    prompt = """You are reading a UAE vehicle number-plate image for a prototype. Inspect the whole uploaded image and the plate carefully.

Return exactly these five lines:
PLATE_TEXT: the visible plate letters/numbers, preserving the order and spacing where possible, or NOT_CLEAR
EMIRATE: one of Dubai, Abu Dhabi, Sharjah, Ajman, Umm Al Quwain, Ras Al Khaimah, Fujairah, OTHER/FOREIGN, or NOT_IDENTIFIABLE
PLATE_CODE_OR_STYLE: the visible letter/number code, emirate name, symbol, or plate-style clue that supports the emirate result, or NOT_VISIBLE
READABILITY: CLEAR, PARTLY CLEAR, or NOT CLEAR
NOTES: briefly explain any blur, glare, crop, ambiguity, or why the emirate cannot be identified

Important rules:
- Try to identify the emirate separately from reading the plate number.
- Base the emirate only on visible text, symbols, or a recognisable plate format. Do not guess the emirate from the plate number alone.
- If the plate's emirate cannot be supported by visible evidence, write EMIRATE: NOT_IDENTIFIABLE and explain why.
- Do not invent missing characters or codes. Use NOT_CLEAR for unreadable plate text.
- This is a best-effort visual reading, not official verification. Do not infer owner identity or other personal details."""
                    with st.spinner("Reading the plate..."):
                        try:
                            response = model.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[prompt, image_for_reading]
                            )
                            result_text = response.text.strip() if response and response.text else "PLATE_TEXT: NOT_CLEAR\nEMIRATE: NOT_IDENTIFIABLE\nPLATE_CODE_OR_STYLE: NOT_VISIBLE\nREADABILITY: NOT CLEAR\nNOTES: No readable response was returned."
                            st.session_state.plate_ocr_result = result_text
                            st.session_state.plate_ocr_detection = detection_status
                        except Exception as exc:
                            st.error(f"Plate reading failed: {type(exc).__name__}. Check your API configuration and try a clearer test image.")

            if st.session_state.get("plate_ocr_result"):
                st.markdown("### Recognition result")
                st.code(st.session_state.plate_ocr_result, language="text")
                st.warning("AI output may be wrong. Compare every character against the source image before using this result.")
                verified = st.checkbox("I manually compared this result with the image", key="plate_result_verified")
                if verified:
                    st.success("Marked as manually checked in this session only. Nothing has been approved or submitted.")
                st.caption("This prototype asks Gemini to read the plate text and identify the emirate from visible evidence. If models/best.pt is present, YOLO detects/crops the plate first. Emirate identification can be uncertain when the plate code or style is not visible; verify the result manually.")
        except Exception:
            st.error("The uploaded file could not be opened as an image. Try a valid JPG, PNG, or WEBP file.")


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.caption("PARKONIC AI ASSISTANT · Prototype interface · Synthetic data only · Not connected to production systems")
