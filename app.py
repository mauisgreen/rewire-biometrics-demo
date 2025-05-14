import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# --- App Configuration ---
st.set_page_config(page_title="Rewire Clinical Tools", layout="wide")

# --- Navigation ---
page = st.sidebar.radio("Choose a view:", [
    "Biometric Stress Checker",
    "Patient List",
    "Patient Profile",
    "Homework Plan Builder"
])

# ------------------------------
# 1. Biometric Stress Checker
# ------------------------------
if page == "Biometric Stress Checker":
    st.title("Rewire Biometric Stress Risk Checker Demo")
    st.markdown("Simulated wearable inputs (last 24h)")

    sleep = st.slider("Sleep Duration (hrs)", 0.0, 12.0, 6.5)
    activity = st.slider("Activity Level (mins)", 0, 120, 45)
    heart_rate = st.slider("Resting Heart Rate (bpm)", 40, 110, 78)
    hrv = st.slider("Heart Rate Variability (HRV)", 10, 120, 50)
    meds = st.radio("Took medication as prescribed?", ("Yes", "No"))

    score = 0
    if sleep < 6: score += 25
    if activity < 30: score += 20
    if heart_rate > 85: score += 20
    if hrv < 50: score += 20
    if meds == "No": score += 15

    risk_level = "Low" if score <= 30 else "Moderate" if score <= 60 else "High"
    color = "🟢" if risk_level == "Low" else "🟡" if risk_level == "Moderate" else "🔴"

    if st.button("Assess Stress Risk"):
        st.subheader(f"{color} Stress Risk: {risk_level}")
        st.markdown(f"Score: **{score}/100**")
        st.info("This is a simulated model. For clinical use, always consult a professional.")

        explanations = []
        if sleep < 6:
            explanations.append("Low sleep duration may increase cortisol and emotional reactivity.")
        if activity < 30:
            explanations.append("Low activity is associated with increased anxiety and rumination.")
        if heart_rate > 85:
            explanations.append("Elevated heart rate is a known marker of acute stress.")
        if hrv < 50:
            explanations.append("Low heart rate variability may reflect reduced emotional regulation.")
        if meds == "No":
            explanations.append("Missed medication may disrupt baseline stability.")

        if explanations:
            st.markdown("### Why this score?")
            for item in explanations:
                st.markdown(f"- {item}")
        else:
            st.success("All biometric indicators are within healthy ranges.")

        with st.expander("How was this score calculated?"):
            st.markdown("### Based on Research")
            st.markdown("""
            - [Van Reeth et al. (2000) – Sleep and Stress](https://pubmed.ncbi.nlm.nih.gov/11148897/)
            - [Kim et al. (2018) – HRV and Stress Monitoring](https://pubmed.ncbi.nlm.nih.gov/29713438/)
            - [Gerber et al. (2014) – Exercise as a Buffer for Stress](https://pubmed.ncbi.nlm.nih.gov/25136547/)
            - [Shaffer & Ginsberg (2017) – HRV Clinical Guidelines](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5624990/)
            """)

            st.markdown("### Key Predictive Factors")
            st.markdown("""
            - Sleep < 6 hrs → +25
            - Activity < 30 mins → +20
            - HR > 85 bpm → +20
            - HRV < 50 → +20
            - Missed meds → +15
            """)

        st.markdown("### Suggested Rewire Plan (Next 30 Days)")
        if risk_level == "High":
            st.markdown("""
            - **Cognitive Reframing (Daily)**
            - **Stress Inoculation Game (5x/week)**
            - **Emotion Labeling (3x/week)**
            - **Wind-Down Protocol (Nightly)**
            """)
        elif risk_level == "Moderate":
            st.markdown("""
            - **Cognitive Flexibility Game (3x/week)**
            - **Emotion Check-In (2x/week)**
            - **Mindful Response Trainer (Nightly)**
            """)
        else:
            st.markdown("""
            - **Resilience Booster (2x/week)**
            - **Evening Calm Game (Optional)**
            - **Streak Tracker**
            """)

# -----------------------------
# 2. Therapist: Patient List
# -----------------------------
elif page == "Patient List":
    st.title("Therapist Dashboard: Patient Overview")
    st.dataframe({
        "Patient ID": ["RW-001", "RW-002", "RW-003"],
        "Last Session": ["2025-05-09", "2025-05-08", "2025-05-07"],
        "EEG Trend": ["Stable", "Worsening", "Improving"],
        "Compliance": ["80%", "50%", "95%"]
    })

# -----------------------------
# 3. Therapist: Patient Profile
# -----------------------------
elif page == "Patient Profile":
    st.title("Patient Profile: RW-001")
    st.subheader("EEG Summary")

    try:
        df = pd.read_csv("rewire_clean_eeg_sample.csv")

        if "faa" in df.columns and "tbr" in df.columns:
            patient_eeg = df.head(4)  # Simulate last 4 sessions
            eeg_chart_data = pd.DataFrame({
                "Session": list(range(1, len(patient_eeg) + 1)),
                "FAA": patient_eeg["faa"].values,
                "TBR": patient_eeg["tbr"].values
            }).set_index("Session")

            st.line_chart(eeg_chart_data)
        else:
            st.warning("FAA and TBR columns not found in EEG dataset.")

    except FileNotFoundError:
        st.error("EEG sample file not found. Please make sure 'rewire_clean_eeg_sample.csv' is in the same folder.")

    st.subheader("Biometric Trends (Last 30 Days)")
    st.line_chart({
        "HRV": [60, 58, 55, 52, 50],
        "Resting HR": [72, 75, 78, 80, 82]
    })

    st.subheader("Homework Compliance")
    st.metric("Game Completion Rate", "72%", "-10% from last month")

# -----------------------------
# 4. Therapist: Plan Builder
# -----------------------------
elif page == "Homework Plan Builder":
    st.title("AI-Suggested Homework Plan for RW-001")

    st.markdown("#### Suggested Games")
    cognitive = st.text_input("Cognitive Game", "Cognitive Reframing")
    emotion = st.text_input("Emotion Game", "Emotion Labeling")
    breathing = st.text_input("Evening Game", "Guided Breathing")

    st.markdown("#### Schedule")
    freq1 = st.slider("Cognitive Game Frequency", 1, 7, 5)
    freq2 = st.slider("Emotion Game Frequency", 1, 7, 3)
    freq3 = st.slider("Evening Game Frequency", 1, 7, 7)

    st.markdown("#### Notes to Patient")
    note = st.text_area("Include any notes or encouragement:", "Focus on consistent use before bed.")

    if st.button("Send to Patient"):
        st.success("Homework plan sent to patient app and email.")
        st.write({
            "Plan": {
                cognitive: f"{freq1}x/week",
                emotion: f"{freq2}x/week",
                breathing: f"{freq3}x/week"
            },
            "Note": note
        })

# -----------------------------
# Footer + Compliance
# -----------------------------
st.markdown("---")
st.markdown("Questions or concerns? Contact **maureen@rewiredtx.com** or visit [rewiredtx.com](https://www.rewiredtx.com)")
st.info("This tool is for demonstration purposes only and not yet approved for clinical use.")

st.markdown("#### Regulatory Notice")
st.markdown("""
This prototype is designed in alignment with **FDA Class II medical device** guidelines under the **Software as a Medical Device (SaMD)** framework.

It supports future submission through the **510(k)** pathway using an FDA-cleared predicate (NeuroFormance™), and adheres to:
- IMDRF risk-based classification model  
- HIPAA-compliant data privacy and handling  
- Design History File (DHF) documentation standards  
- AI/ML safety and clinical oversight best practices  
""")

st.caption("Version 0.4 · Last updated: May 13, 2025")