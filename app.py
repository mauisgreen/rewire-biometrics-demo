import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# -------------- CONFIG --------------
st.set_page_config(page_title="Rewire Therapist Dashboard", layout="centered")

# -------------- PATIENT & GAME DB --------------
patients = {
    "RW-001": {"name": "Alex Rivera",  "diagnosis": "PTSD"},
    "RW-002": {"name": "Jamie Chen",   "diagnosis": "ADHD"},
    "RW-003": {"name": "Taylor Singh", "diagnosis": "MDD"},
}
game_options = {
    "PTSD": ["Cognitive Reframing", "Stress Inoculation", "Guided Breathing", "Emotion Labeling"],
    "ADHD": ["Focus Trainer", "Impulse Control Game", "Breath Pacer", "Visual Attention"],
    "MDD":  ["Optimism Booster", "Cognitive Flexibility", "Mood Tracking", "Evening Wind-down"],
}

# -------------- PAGE HEADER --------------
st.title("🧠 Rewire Therapist Dashboard")
pid = st.selectbox("Select Patient", list(patients.keys()))
pname  = patients[pid]["name"]
pdiag  = patients[pid]["diagnosis"]
st.markdown(f"### {pname} ({pid})   |   **Diagnosis:** {pdiag}")

# -------------- 1. SYNC LATEST DATA --------------
if st.button("🔄 Sync Latest Data"):
    # ───── Load biometric & EEG CSVs (replace with S3 / API fetch later) ─────
    try:
        bio_df = pd.read_csv("latest_biometric.csv")      # HR, HRV, sleep… (auto-uploaded)
        eeg_df = pd.read_csv("rewire_clean_eeg_sample.csv")
        st.success("Latest biometric and EEG data synced.")
        st.session_state["bio_df"] = bio_df
        st.session_state["eeg_df"] = eeg_df
    except FileNotFoundError:
        st.error("Auto-upload files not found. Ensure `latest_biometric.csv` & EEG file exist.")

# ------------ 2. SHOW READ-ONLY METRICS -------------
bio_df = st.session_state.get("bio_df")
eeg_df = st.session_state.get("eeg_df")

if bio_df is not None and not bio_df.empty:
    latest_bio = bio_df[bio_df["patient_id"] == pid].iloc[-1]
    st.markdown("#### 📈 Latest Biometric Snapshot")
    col1, col2 = st.columns(2)
    col1.metric("Resting HR",   f"{latest_bio['resting_hr']} bpm")
    col2.metric("HRV",          f"{latest_bio['hrv']} ms")
else:
    st.info("Sync to view biometric data.")

if eeg_df is not None and not eeg_df.empty:
    pt_eeg = eeg_df[eeg_df["patient_id"] == pid].tail(4)
    if not pt_eeg.empty:
        st.markdown("#### 🧠 EEG Trend (FAA & TBR)")
        trend = pt_eeg[["faa", "tbr"]].reset_index(drop=True)
        trend.index = trend.index + 1
        st.line_chart(trend)
else:
    st.info("Sync to view EEG trend.")

# -------------- 3. IN-CLINIC SESSION INPUT --------------
st.markdown("---")
st.subheader("📋 In-Clinic Session Notes")
with st.form("session_form"):
    meds_taken = st.radio("Medication adherence reported?", ("Yes", "No", "NA"))
    therapist_note = st.text_area("Observations / triggers during session")
    run_btn = st.form_submit_button("Run Assessment")

# -------------- 4. RISK ASSESSMENT --------------
if run_btn and bio_df is not None:
    latest = latest_bio  # combine auto metrics with therapist field
    score = 0
    if latest["sleep"] < 6:        score += 25
    if latest["activity"] < 30:    score += 20
    if latest["resting_hr"] > 85:  score += 20
    if latest["hrv"] < 50:         score += 20
    if meds_taken == "No":         score += 15
    level = ("Low","Moderate","High")[(score>30)+(score>60)]
    icon  = ("🟢","🟡","🔴")[(score>30)+(score>60)]
    st.subheader(f"{icon} Stress Risk: **{level}**   · Score {score}/100")

    # ---------------- EEG section ----------------
    st.markdown("#### 🧠 Neuro-score Progress")

    try:
        df = pd.read_csv("rewire_clean_eeg_sample.csv")
        pt_eeg = df[df["patient_id"] == pid].tail(4)

        if pt_eeg.empty:
            st.info("No EEG records for this patient.")
        else:
            # ----- z-score normalisation -----
            z = (pt_eeg[["faa", "tbr"]] - pt_eeg[["faa", "tbr"]].mean()) / pt_eeg[["faa", "tbr"]].std()
            pt_eeg["neuro_score"] = z.mean(axis=1)   # average of the two z-scores

            latest_ns   = pt_eeg["neuro_score"].iloc[-1]
            baseline_ns = pt_eeg["neuro_score"].iloc[0]
            delta       = latest_ns - baseline_ns

            # Bar colour: better = blue, worse = red, same = grey
            colour = "royalblue" if delta < -0.3 else "orangered" if delta > 0.3 else "lightgrey"

            st.metric(label="Change vs. baseline",
                    value=f"{delta:+.2f} SD",
                    delta=None)

            # Bar chart (single row)
            import altair as alt
            bar_df = pd.DataFrame({"label": ["Progress"], "value": [delta]})

            bar = alt.Chart(bar_df).mark_bar(size=40, color=colour).encode(
                x=alt.X("value:Q", scale=alt.Scale(domain=[-2, 2]), title="Better  ◀︎                  ▶︎  Worse"),
                y=alt.Y("label:N", title="")
            )
            st.altair_chart(bar, use_container_width=True)

            # Optional brain overlay image if you have PNG called brain_overlay.png
            # from PIL import Image
            # brain = Image.open("brain_overlay.png")
            # st.image(brain, caption="Blue = improvement, Red = over-activation", use_column_width=True)

    except FileNotFoundError:
        st.error("EEG file missing. Place 'rewire_clean_eeg_sample.csv' next to app.py")

    # -----------------------------
    # 6. Homework Plan Builder
    # -----------------------------
    st.markdown("---")
    st.subheader("Homework Plan Builder")

    st.markdown("Select therapeutic games and weekly schedule:")

    # 1st dropdown
    all_choices = game_options[pdiag][:]
    g1 = st.selectbox("Cognitive Game", all_choices, key="g1")

    # 2nd dropdown (remove g1)
    choices_lvl2 = [g for g in all_choices if g != g1]
    g2 = st.selectbox("Emotion Regulation Game", choices_lvl2, key="g2")

    # 3rd dropdown (remove g1 & g2)
    choices_lvl3 = [g for g in all_choices if g not in (g1, g2)]
    g3 = st.selectbox("Evening Wind-down Game", choices_lvl3, key="g3")

    # Frequencies
    f1 = st.slider(f"{g1} per week", 1, 7, 5, key="f1")
    f2 = st.slider(f"{g2} per week", 1, 7, 3, key="f2")
    f3 = st.slider(f"{g3} per week", 1, 7, 7, key="f3")

    # Therapist message
    msg = st.text_area("Message to patient", "Focus on consistency and practice this week.")

    # Save / send
    if st.button("💾 Save & Send Plan"):
        # TODO: real API / DB call here
        st.success("✅ Homework sent successfully!")
        # st.balloons()  # uncomment for celebration
        st.json({
            "Patient": pname,
            "Diagnosis": pdiag,
            "Risk":    risk_level,
            "Games":   {g1: f"{f1}×/wk", g2: f"{f2}×/wk", g3: f"{f3}×/wk"},
            "Message": msg
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
with st.sidebar.expander("Research Behind Rewire"):
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

    These sources inform our clinical logic, scoring heuristics, and therapeutic interventions. If you have any questions about the evidence base or methodology, please reach out to our clinical team at **clinical@rewiredtx.com**.
    """)