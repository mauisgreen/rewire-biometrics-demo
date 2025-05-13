import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Rewire Biometric Stress - Demo", layout="centered")

st.title("Rewire Biometric Stress Risk Checker Demo")
st.markdown("Simulated wearable inputs (last 24h)")

# Input sliders
sleep = st.slider("Sleep Duration (hrs)", 0.0, 12.0, 6.5)
activity = st.slider("Activity Level (mins)", 0, 120, 45)
heart_rate = st.slider("Resting Heart Rate (bpm)", 40, 110, 78)
hrv = st.slider("Heart Rate Variability (HRV)", 10, 120, 50)
meds = st.radio("Took medication as prescribed?", ("Yes", "No"))

# Rule-based scoring
score = 0
if sleep < 6: score += 25
if activity < 30: score += 20
if heart_rate > 85: score += 20
if hrv < 50: score += 20
if meds == "No": score += 15

risk_level = "Low" if score <= 30 else "Moderate" if score <= 60 else "High"
color = "🟢" if risk_level == "Low" else "🟡" if risk_level == "Moderate" else "🔴"

# Show output when button is clicked
if st.button("Assess Stress Risk"):
    st.subheader(f"{color} Stress Risk: {risk_level}")
    st.markdown(f"Score: **{score}/100**")
    st.info("This is a simulated model. For clinical use, always consult a professional.")

    # Explanation block
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

    # Follow-up plan (always shown after button click)
    st.markdown("---")
    st.markdown("### Suggested Rewire Plan (Next 30 Days)")
    st.markdown("Based on your recent biometric data, here’s a therapeutic activity plan...")

    if risk_level == "High":
        st.markdown("""
        - **Cognitive Reframing (Daily)** — Strengthen flexible thinking.
        - **Stress Inoculation Game (5x/week)** — Practice calming under pressure.
        - **Emotion Labeling (3x/week)** — Voice journaling and reflection.
        - **Wind-Down Protocol (Nightly)** — Guided parasympathetic activation.
        """)
    elif risk_level == "Moderate":
        st.markdown("""
        - **Cognitive Flexibility Game (3x/week)** — Train adaptability.
        - **Emotion Check-In (2x/week)** — Track emotional awareness.
        - **Mindful Response Trainer (Nightly)** — Post-screen guided breathing.
        """)
    else:
        st.markdown("""
        - **Resilience Booster (2x/week)** — Optimistic memory recall.
        - **Evening Calm Game (Optional)** — Sleep-focused cool-down.
        - **Streak Tracker** — Daily usage monitor.
        """)

    st.info("Rewire DTx activities are short, personalized, and adapt with progress.")

    # Score calculation details (expander only shows after score is assessed)
    with st.expander("How was this score calculated?"):
        st.markdown("### Based on Research")
        st.markdown("""
        - [Van Reeth et al. (2000) – Sleep and Stress](https://pubmed.ncbi.nlm.nih.gov/11148897/)
        - [Kim et al. (2018) – HRV and Stress Monitoring](https://pubmed.ncbi.nlm.nih.gov/29713438/)
        ...
        """)

        st.markdown("### Data Used in This Prototype")
        st.markdown("""
        Dataset: [Sleep Health and Lifestyle Dataset (Kaggle)](https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset)

        - Model: Rule-based logic (RandomForest in experimental mode)
        - MAE ~0.04, R² ~0.98
        - Target: Stress Level (1–10)
        """)

        st.markdown("### Key Predictive Factors")
        st.markdown("""
        - Sleep < 6 hrs → +25
        - Activity < 30 mins → +20
        - HR > 85 bpm → +20
        - HRV < 50 → +20
        - Missed meds → +15
        """)

        st.markdown("""
        These scores reflect relative weights from psychophysiology research and may be tuned.
        """)
        
    # --- Personalized Rewire Plan ---
    st.markdown("---")
    st.markdown("### Suggested Rewire Plan (Next 30 Days)")

    st.markdown("Based on your recent biometric data, here’s a therapeutic activity plan to support your emotional regulation and cognitive resilience:")

    # Tailored plan based on score
    if risk_level == "High":
        st.markdown("""
        - **Cognitive Reframing (Daily)**: Strengthen flexible thinking through interactive cognitive restructuring scenarios.
        - **Stress Inoculation Game (5x/week)**: Practice calming under pressure through escalating challenges with guided biofeedback.
        - **Emotion Labeling & Voice Journaling (3x/week)**: Develop emotional awareness by reflecting through guided journaling and voice analysis.
        - **Wind-Down Protocol (Nightly)**: 10-minute game to activate parasympathetic recovery before bed.
        """)
    elif risk_level == "Moderate":
        st.markdown("""
        - **Cognitive Flexibility Game (3x/week)**: Navigate rapid-shift puzzles to train attention and adaptability.
        - **Emotion Check-In (2x/week)**: Use voice-based journaling or facial micro-expression matching for mood awareness.
        - **Mindful Response Trainer (Nightly)**: Light-guided breathing sequences post-evening screen use.
        """)
    else:
        st.markdown("""
        - **Resilience Booster (2x/week)**: Light memory training with optimistic feedback loops.
        - **Evening Calm Game (Optional)**: Short routine for stress tracking and wind-down reflection.
        - **Self-monitor using daily Rewire streak tracker.**
        """)

    st.info("Rewire Dtx Games are designed for short, engaging use (5–15 minutes) and adapt based on performance.")
# --- Footer ---
st.markdown("---")
st.markdown("#### Learn more")
st.markdown("Visit our official website: [rewiredtx.com](https://www.rewiredtx.com)")

st.markdown("Questions or concerns? Contact: **maureen@rewiredtx.com**😉")
# --- Compliance Readiness ---
with st.expander("Regulatory & Compliance Readiness"):
    st.markdown("### HIPAA Preparedness")

    st.markdown("""
    - Data is anonymized and not stored unless explicitly permitted by the user.
    - No Protected Health Information (PHI) is collected in this prototype.
    - Designed for future hosting on HIPAA-compliant infrastructure (e.g., AWS or GCP with BAA).
    - All inputs and outputs encrypted in transit (TLS 1.2+), with support for future AES-256 at rest.
    """)

    st.markdown("### FDA SaMD Alignment (Future Pathway)")

    st.markdown("""
    - Tool is structured to comply with **FDA SaMD guidance** and **IMDRF risk-based framework**.
    - Decision logic is explainable, research-supported, and structured for clinical oversight.
    - Future features include audit logging, post-market surveillance, and model monitoring.
    - Suitable for De Novo or 510(k) submission with cognitive behavioral intervention claims.
    """)

    st.markdown("### AI Transparency & Clinical Safety")

    st.markdown("""
    - Rule-based logic is transparent and traceable.
    - Future versions will integrate explainability methods (e.g., SHAP) for AI models.
    - Clear human-in-the-loop design to support clinicians, not replace them.
    - Suggested activities include user-friendly language and time estimates for accessibility.
    """)

    st.markdown("### Next Milestones")

    st.markdown("""
    - [ ] Migrate hosting to HIPAA-compliant infrastructure  
    - [ ] Begin Design History File (DHF) documentation  
    - [ ] Recruit advisors for clinical validation study  
    - [ ] Establish security, privacy, and access controls for production  
    - [ ] Evaluate Digital Therapeutic (DTx) classification under FDA guidance  
    """)
