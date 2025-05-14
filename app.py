import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(page_title="Rewire Therapist Dashboard", layout="centered")

# -----------------------------
# Simulated Patient Database
# -----------------------------
patients = {
    "RW-001": {"name": "Warren Liu", "diagnosis": "PTSD"},
    "RW-002": {"name": "Percival Ralston", "diagnosis": "ADHD"},
    "RW-003": {"name": "Taylor Singh", "diagnosis": "MDD"}
}

game_options = {
    "PTSD": ["Cognitive Reframing - ReThink", "Stress Inoculation - Wave Rider", "Guided Breathing", "Emotion Labeling - Mood Match"],
    "ADHD": ["Focus Trainer - ", "Impulse Control - Impulse Ninja", "Breath Pacer - Breathe the Beat", "Visual Attention - Colour Match"],
    "MDD": ["Optimism Booster - Mood Bloom", "Cognitive Flexibility - ReRoute", "Mood Tracking - Feel Journal ", "Evening Wind-down - MoonMode"]
}

# -----------------------------
# Page Title and Patient Selector
# -----------------------------
st.title("Rewire Therapist Dashboard")

selected_id = st.selectbox("Select a patient", options=list(patients.keys()))
selected_name = patients[selected_id]["name"]
diagnosis = patients[selected_id]["diagnosis"]
st.markdown(f"### Patient: **{selected_name}** ({selected_id})")
st.markdown(f"**Diagnosis:** {diagnosis}")

# -----------------------------
# 1. In-Clinic Session Entry
# -----------------------------
st.subheader("📋 Record In-Clinic Session")

with st.form(key="session_form"):
    sleep = st.number_input("Sleep Duration (hrs)", min_value=0.0, max_value=12.0, step=0.1, value=6.5)
    activity = st.number_input("Physical Activity (mins)", min_value=0, max_value=180, step=5, value=45)
    heart_rate = st.number_input("Resting Heart Rate (bpm)", min_value=40, max_value=110, value=78)
    hrv = st.number_input("Heart Rate Variability (HRV)", min_value=10, max_value=120, value=50)
    meds = st.radio("Took medication as prescribed?", ("Yes", "No"))
    notes = st.text_area("Therapist Notes (optional)")
    submit_button = st.form_submit_button("Run Stress Risk Assessment")

# -----------------------------
# 2. Stress Risk Assessment
# -----------------------------
if submit_button:
    score = 0
    if sleep < 6: score += 25
    if activity < 30: score += 20
    if heart_rate > 85: score += 20
    if hrv < 50: score += 20
    if meds == "No": score += 15

    risk_level = "Low" if score <= 30 else "Moderate" if score <= 60 else "High"
    color = "🟢" if risk_level == "Low" else "🟡" if risk_level == "Moderate" else "🔴"

    st.subheader(f"{color} Stress Risk Level: {risk_level}")
    st.markdown(f"Score: **{score}/100**")
    st.markdown("#### Why this score?")
    if sleep < 6:
        st.markdown("- Sleep below 6 hours may elevate stress reactivity.")
    if activity < 30:
        st.markdown("- Less than 30 mins of activity linked to poor mood regulation.")
    if heart_rate > 85:
        st.markdown("- Resting HR greater than 85bpm may indicate autonomic stress.")
    if hrv < 50:
        st.markdown("- HRV lower than 50 correlates with reduced emotional resilience.")
    if meds == "No":
        st.markdown("- Medication non-adherence may disrupt stability.")

    # -----------------------------
    # 3. EEG Snapshot with Interpretation
    # -----------------------------
    st.markdown("---")
    st.subheader("🧠 EEG Summary")
    try:
        df = pd.read_csv("rewire_clean_eeg_sample.csv")
        patient_eeg = df[df["patient_id"] == selected_id].tail(4)

        if not patient_eeg.empty:
            chart_data = pd.DataFrame({
                "Session": list(range(1, len(patient_eeg) + 1)),
                "FAA": patient_eeg["faa"].values,
                "TBR": patient_eeg["tbr"].values
            }).set_index("Session")
            st.line_chart(chart_data)

            latest_faa = patient_eeg["faa"].iloc[-1]
            latest_tbr = patient_eeg["tbr"].iloc[-1]

            st.markdown("### EEG Interpretation (Latest Session)")
            if latest_faa < -0.2 and latest_tbr > 0.6:
                st.warning("⚠️ EEG suggests **cognitive dysregulation** — recommend **reframing + focus games**.")
            elif latest_faa < -0.2:
                st.info("⬇️ Frontal asymmetry suggests **low motivation** or **mood disturbance**.")
            elif latest_tbr > 0.6:
                st.info("↑ Elevated TBR suggests **attention or focus difficulties**.")
            else:
                st.success("✅ EEG appears **within normal ranges**.")

            st.markdown("### FAA vs TBR Diagnostic Map")
            chart = alt.Chart(patient_eeg).mark_circle(size=80).encode(
                x=alt.X("faa", title="Frontal Alpha Asymmetry"),
                y=alt.Y("tbr", title="Theta/Beta Ratio"),
                tooltip=["faa", "tbr", "diagnosis"],
                color=alt.value("steelblue")
            ).interactive()
            st.altair_chart(chart, use_container_width=True)

        else:
            st.warning("No EEG data found for this patient.")

    except FileNotFoundError:
        st.error("EEG data file not found. Please ensure 'rewire_clean_eeg_sample.csv' is present.")

    # -----------------------------
    # 4. Homework Plan Builder
    # -----------------------------
    st.markdown("---")
    st.subheader("Homework Plan Builder")

    st.markdown("Select therapeutic games and weekly schedule:")
    game_choices = game_options.get(diagnosis, [])

    cognitive = st.selectbox("Cognitive Game", game_choices, index=0)
    emotion = st.selectbox("Emotion Regulation Game", game_choices, index=1)
    evening = st.selectbox("Evening Wind-down Game", game_choices, index=2)

    freq1 = st.slider("Frequency for Cognitive Game", 1, 7, 5)
    freq2 = st.slider("Frequency for Emotion Game", 1, 7, 3)
    freq3 = st.slider("Frequency for Evening Game", 1, 7, 7)

    final_notes = st.text_area("Message to Patient", "Focus on consistency and practice this week.")

    if st.button("Save new EHR data & Send Homework Plan"):
        st.success("✅ Encrypted EHR data saved & Homework Plan sent to patient via email and app.")
        st.json({
            "Patient": selected_name,
            "Diagnosis": diagnosis,
            "Risk Level": risk_level,
            "Games": {
                cognitive: f"{freq1}x/week",
                emotion: f"{freq2}x/week",
                evening: f"{freq3}x/week"
            },
            "Message": final_notes
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
# -----------------------------
# Sidebar: Evidence Base
# -----------------------------
with st.sidebar.expander("🧠 Evidence Base: Research Behind Rewire"):
    st.markdown("""
    Rewire DTx is grounded in peer-reviewed research on stress physiology, digital therapeutics, and neurocognitive rehabilitation:

    - **Heart Rate Variability (HRV) & Stress:**
      - Shaffer & Ginsberg (2017). *An Overview of HRV Metrics & Norms*. [Link](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5624990/)
      - Kim et al. (2018). *Stress Monitoring Using HRV from Wearables*. [Link](https://pubmed.ncbi.nlm.nih.gov/29713438/)

    - **Cognitive Restructuring & PTSD:**
      - Resick et al. (2002). *Cognitive Processing Therapy for PTSD*. [Link](https://psycnet.apa.org/doi/10.1037/0022-006X.70.4.867)

    - **Frontal Alpha Asymmetry & Mood:**
      - Thibodeau et al. (2006). *Meta-analysis of EEG Asymmetry & Depression*. [Link](https://pubmed.ncbi.nlm.nih.gov/16953775/)

    - **Digital Game-Based Therapies:**
      - Denisova & Nordin (2020). *Game-Based Cognitive Training for Depression and Anxiety*. [Link](https://doi.org/10.3389/fpsyt.2020.00069)

    - **Remote Monitoring & Behavioral Change:**
      - Mohr et al. (2013). *Behavioral Intervention Technologies: Evidence Base & Roadmap*. [Link](https://pubmed.ncbi.nlm.nih.gov/23590427/)

    These sources inform our clinical logic, scoring heuristics, and therapeutic interventions.
    """)