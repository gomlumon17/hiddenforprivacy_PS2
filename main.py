import streamlit as st
import sys
import os
import cv2
import numpy as np
import pytesseract
import re
import time

# Add root directory so Python can find src.cv_model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.cv_model.predict import classify_waste

# ==========================================
# WINDOWS USERS: UNCOMMENT AND UPDATE THIS
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# ==========================================

st.set_page_config(
    page_title="Eco-Label Vision",
    page_icon="♻️",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "eco_points" not in st.session_state:
    st.session_state.eco_points = 0

if "streak" not in st.session_state:
    st.session_state.streak = 0

if "items_sorted" not in st.session_state:
    st.session_state.items_sorted = 0

if "carbon_saved" not in st.session_state:
    st.session_state.carbon_saved = 0.0

if "badge" not in st.session_state:
    st.session_state.badge = "🌱 Beginner Recycler"

if "predicted_class" not in st.session_state:
    st.session_state.predicted_class = None

if "confidence" not in st.session_state:
    st.session_state.confidence = 0.0

if "points_added_for_current_item" not in st.session_state:
    st.session_state.points_added_for_current_item = False


# ---------------- REWARD SYSTEM ----------------
def update_rewards(waste_type, confidence):
    if confidence < 60:
        return 0, 0.0

    if st.session_state.points_added_for_current_item:
        return 0, 0.0

    points_map = {
        "Plastic": 10,
        "Paper": 8,
        "Metal": 12,
        "Glass": 15
    }

    carbon_map = {
        "Plastic": 0.12,
        "Paper": 0.08,
        "Metal": 0.20,
        "Glass": 0.18
    }

    gained_points = points_map.get(waste_type, 5)
    gained_carbon = carbon_map.get(waste_type, 0.05)

    st.session_state.eco_points += gained_points
    st.session_state.items_sorted += 1
    st.session_state.streak += 1
    st.session_state.carbon_saved += gained_carbon
    st.session_state.points_added_for_current_item = True

    if st.session_state.eco_points >= 200:
        st.session_state.badge = "🏆 Eco Master"
    elif st.session_state.eco_points >= 120:
        st.session_state.badge = "🥇 Green Champion"
    elif st.session_state.eco_points >= 60:
        st.session_state.badge = "♻️ Recycling Pro"
    elif st.session_state.eco_points >= 20:
        st.session_state.badge = "🌿 Eco Learner"
    else:
        st.session_state.badge = "🌱 Beginner Recycler"

    return gained_points, gained_carbon


# ---------------- OCR HELPERS ----------------
def scan_resin_code_debug(image_frame):
    try:
        h, w = image_frame.shape[:2]

        # Crop center region
        x1 = int(w * 0.2)
        y1 = int(h * 0.2)
        x2 = int(w * 0.8)
        y2 = int(h * 0.8)
        crop = image_frame[y1:y2, x1:x2]

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

        # Enlarge for OCR
        gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

        # Blur + sharpen
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        gray = cv2.filter2D(gray, -1, kernel)

        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        # OCR for single digit
        custom_config = r'--oem 3 --psm 10 -c tessedit_char_whitelist=1234567'
        text = pytesseract.image_to_string(thresh, config=custom_config)

        match = re.search(r'[1-7]', text)
        code = match.group(0) if match else None

        return code, crop, thresh, text

    except Exception as e:
        print(f"OCR Error: {e}")
        return None, None, None, ""


def get_resin_info(code):
    info = {
        "1": "PET (Highly Recyclable) - Usually water bottles and clear containers.",
        "2": "HDPE (Highly Recyclable) - Usually milk jugs and detergent bottles.",
        "3": "PVC (Hard to Recycle) - Keep out of regular recycling bins.",
        "4": "LDPE (Check Local Rules) - Plastic bags and wraps.",
        "5": "PP (Recyclable) - Yogurt cups and bottle caps.",
        "6": "PS (Hard to Recycle) - Styrofoam and disposable cups.",
        "7": "OTHER (Usually Non-Recyclable) - Mixed plastics."
    }
    return info.get(code, "Unknown resin code.")


# ---------------- DISPOSAL INSTRUCTIONS ----------------
def get_instructions(waste_type):
    instructions = {
        "Plastic": "🔵 Blue Bin - Empty liquids and leave the cap on if accepted locally.",
        "Metal": "🔵 Blue Bin - Rinse before disposal for better recycling quality.",
        "Paper": "🔵 Blue Bin - Keep it dry and flatten boxes before recycling.",
        "Glass": "⚪ Grey Bin / Glass Drop-off - Handle carefully and avoid mixing with paper/plastic."
    }
    return instructions.get(waste_type, "Unknown item. Please check manually.")


# ---------------- STYLING ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(34,197,94,0.10), transparent 25%),
        radial-gradient(circle at top right, rgba(132,204,22,0.10), transparent 22%),
        linear-gradient(180deg, #f0fdf4 0%, #ecfccb 45%, #f9fafb 100%);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.main-title {
    font-size: 3.2rem;
    font-weight: 800;
    text-align: center;
    color: #166534;
    margin-bottom: 0.1rem;
    animation: floaty 2.8s ease-in-out infinite;
}

.subtitle {
    text-align: center;
    color: #4b5563;
    font-size: 1.08rem;
    margin-bottom: 1.8rem;
}

.hero-box {
    background: rgba(255,255,255,0.75);
    border: 1px solid rgba(34,197,94,0.14);
    border-radius: 24px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 10px 30px rgba(22,101,52,0.08);
    backdrop-filter: blur(10px);
    animation: fadeUp 0.8s ease;
}

.metric-card {
    background: linear-gradient(180deg, #ffffff, #f0fdf4);
    border: 1px solid #bbf7d0;
    border-radius: 20px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 8px 22px rgba(34,197,94,0.08);
    transition: all 0.28s ease;
}

.metric-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 14px 28px rgba(34,197,94,0.14);
}

.metric-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #166534;
    margin-bottom: 2px;
}

.metric-label {
    font-size: 0.92rem;
    color: #6b7280;
}

.badge-box {
    margin-top: 1rem;
    background: linear-gradient(90deg, #dcfce7, #fef9c3);
    border: 1px solid #bbf7d0;
    border-radius: 18px;
    padding: 14px;
    text-align: center;
    font-weight: 700;
    color: #166534;
    box-shadow: 0 8px 22px rgba(0,0,0,0.05);
    animation: pulse 2.2s infinite;
}

.panel {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(34,197,94,0.14);
    border-radius: 22px;
    padding: 1.25rem;
    box-shadow: 0 10px 28px rgba(22,101,52,0.08);
    backdrop-filter: blur(10px);
    animation: fadeUp 0.7s ease;
}

.section-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #166534;
    margin-bottom: 0.6rem;
}

.small-text {
    color: #4b5563;
    font-size: 0.98rem;
}

.reward-card {
    background: linear-gradient(135deg, #dcfce7, #ecfccb);
    border: 1px solid #86efac;
    border-radius: 18px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 8px 20px rgba(34,197,94,0.10);
    animation: fadeUp 0.6s ease;
}

.reward-title {
    color: #166534;
    font-weight: 800;
    font-size: 1.25rem;
    margin-bottom: 0.4rem;
}

.reward-text {
    color: #365314;
    font-size: 1.02rem;
}

[data-testid="stCameraInput"] {
    border: 2px dashed #22c55e;
    border-radius: 18px;
    padding: 12px;
    background: #f0fdf4;
}

.stButton > button {
    width: 100%;
    border-radius: 14px;
    border: none;
    padding: 0.82rem 1rem;
    background: linear-gradient(90deg, #22c55e, #84cc16);
    color: white;
    font-weight: 700;
    transition: all 0.25s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(34,197,94,0.20);
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.75);
    border: 1px solid #dcfce7;
    padding: 0.8rem;
    border-radius: 16px;
}

[data-testid="stAlert"] {
    border-radius: 14px;
}

.footer-note {
    text-align: center;
    color: #6b7280;
    font-size: 0.92rem;
    margin-top: 1rem;
}

@keyframes floaty {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-4px); }
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(18px);
    }
    to {
        opacity: 1;
        transform: translateY(0px);
    }
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 rgba(34,197,94,0.10); }
    50% { box-shadow: 0 0 24px rgba(132,204,22,0.18); }
    100% { box-shadow: 0 0 0 rgba(34,197,94,0.10); }
}
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------
st.markdown('<div class="main-title">♻️ Eco-Label Vision</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-Powered Smart Bin Assistant for Sustainable Waste Sorting</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="hero-box">
    <div class="small-text" style="text-align:center;">
        First scan the waste item. If it is plastic, the app will ask for a second close-up image
        of the resin code for better OCR accuracy.
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")


# ---------------- DASHBOARD ----------------
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{st.session_state.eco_points}</div>
        <div class="metric-label">Eco Points</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{st.session_state.streak}</div>
        <div class="metric-label">Recycling Streak</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{st.session_state.items_sorted}</div>
        <div class="metric-label">Items Sorted</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{st.session_state.carbon_saved:.2f} kg</div>
        <div class="metric-label">Estimated Carbon Saved</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    f'<div class="badge-box">🌿 Current Badge: {st.session_state.badge}</div>',
    unsafe_allow_html=True
)

st.write("")


# ---------------- STEP 1: CLASSIFICATION ----------------
left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📷 Step 1: Scan Waste Item</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="small-text">Capture the waste item first. The system will classify it into plastic, paper, metal, or glass.</div>',
        unsafe_allow_html=True
    )
    camera_image = st.camera_input("Take a picture of the waste item", key="waste_item_camera")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🌍 Smart Sorting Workflow</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="small-text">
        <b>Step 1:</b> Identify the material using AI.<br><br>
        <b>Step 2:</b> If the detected material is plastic, capture a second close-up image of the resin code.<br><br>
        <b>Step 3:</b> The app gives material-specific disposal guidance and resin-based plastic advice.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if camera_image is not None:
    with st.spinner("Classifying waste item..."):
        time.sleep(1)
        predicted_class, confidence = classify_waste(camera_image)

    st.session_state.predicted_class = predicted_class
    st.session_state.confidence = confidence
    st.session_state.points_added_for_current_item = False

    gained_points, gained_carbon = update_rewards(predicted_class, confidence)

    st.write("")
    r1, r2 = st.columns([1.1, 0.9], gap="large")

    with r1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">✅ Classification Result</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Detected Material", predicted_class)
        with c2:
            st.metric("AI Confidence", f"{confidence:.2f}%")

        st.info(get_instructions(predicted_class))

        if confidence > 60:
            st.success("Great job! Item classified with high confidence.")
            st.balloons()
        else:
            st.warning("Confidence is lower than expected. Try a clearer photo with better lighting.")

        st.markdown('</div>', unsafe_allow_html=True)

    with r2:
        st.markdown('<div class="reward-card">', unsafe_allow_html=True)
        st.markdown('<div class="reward-title">🎉 Reward Unlocked</div>', unsafe_allow_html=True)

        if confidence > 60:
            st.markdown(
                f'<div class="reward-text">+{gained_points} Eco Points earned<br>'
                f'+{gained_carbon:.2f} kg carbon savings added<br>'
                f'<b>{predicted_class}</b> sorted successfully</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="reward-text">No reward added this time.<br>Try a clearer scan for higher confidence.</div>',
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)


# ---------------- STEP 2: OCR ONLY FOR PLASTIC ----------------
if st.session_state.predicted_class == "Plastic":
    st.write("")
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔍 Step 2: Capture Resin Code Close-Up</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="small-text">Plastic detected. Now take a second close-up image of the tiny recycling triangle / resin code for better OCR accuracy.</div>',
        unsafe_allow_html=True
    )

    resin_image = st.camera_input("Take a close-up picture of the resin code", key="resin_code_camera")

    if resin_image is not None:
        with st.spinner("Reading resin code..."):
            resin_image.seek(0)
            file_bytes = np.asarray(bytearray(resin_image.read()), dtype=np.uint8)
            opencv_image = cv2.imdecode(file_bytes, 1)

            code, crop_img, processed_img, raw_text = scan_resin_code_debug(opencv_image)

        d1, d2 = st.columns(2)
        with d1:
            if crop_img is not None:
                st.image(crop_img, caption="Cropped OCR Region", channels="BGR")
        with d2:
            if processed_img is not None:
                st.image(processed_img, caption="Processed OCR Image")

        with st.expander("Show Raw OCR Output"):
            st.write(raw_text)

        if code:
            st.success(f"Detected Resin Code: #{code}")
            st.info(get_resin_info(code))
        else:
            st.warning("Could not detect a clear resin code. Try better focus, less glare, and a closer shot.")

    st.markdown('</div>', unsafe_allow_html=True)


st.write("")
st.markdown("---")
st.markdown(
    '<div class="footer-note">Built with Streamlit, EfficientNetB0, OpenCV, and Tesseract OCR</div>',
    unsafe_allow_html=True
)