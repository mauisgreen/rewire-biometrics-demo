import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from PIL import Image

# -------------- CONFIG --------------
st.set_page_config(page_title="Rewire Therapist Dashboard", layout="centered")

# ---------- Rewire brand palette ----------
REWIRE_PRIMARY   = "#001E5A"   # dark navy
REWIRE_ACCENT    = "#3E5EE4"   # hover / accent blue
REWIRE_BG        = "#F5F7FA"   # light grey
REWIRE_CARD_BG   = "#FFFFFF"

st.markdown(
f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

st.markdown(
    """
    <style>
      /* Opt out of Chrome’s forced dark mode and always render our light background */
      :root {
        /* tell browsers we only support light scheme */
        color-scheme: light;
      }
      @media (prefers-color-scheme: dark) {
        body, .main {
          background-color: #F5F7FA !important;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)
<style>
/* ---------- global ----------- */
body, .main {{
    background-color:{REWIRE_BG};
    font-family: "Inter", sans-serif;     /* ← now Inter */
}}

/* ---------- cards / containers ----------- */
.block-container {{
    padding-top: 3rem;
}}
div[data-testid="stForm"] {{
    background:{REWIRE_CARD_BG};
    padding:1.2rem 1.5rem;
    border-radius:12px;
    box-shadow:0 2px 6px rgba(0,0,0,0.08);
}}

/* ---------- headers ----------- */
h2, h3, h4 {{
    color:{REWIRE_PRIMARY};
    font-family: "Inter", sans-serif;     /* ← Inter here too */
    font-weight:600;
}}

/* ---------- sliders ----------- */
div[data-baseweb="slider"] div[role="slider"] {{
    background:{REWIRE_PRIMARY};
    background: #001E5A;
}}

/* ---------- buttons ----------- */
div.stButton > button:first-child {{
    background:{REWIRE_PRIMARY};
    color:#fff;
    border:none;
    border-radius:8px;
    font-family: "Inter", sans-serif;
}}
div.stButton > button:first-child:hover {{
    background:{REWIRE_ACCENT};
}}

.stAlert-success {{
    background:#E0F8F4;
    border-left:6px solid {REWIRE_PRIMARY};
    color:#0f7768;
}}

.stToast {{
    background:{REWIRE_PRIMARY}!important;
    color:#fff!important;
}}
</style>
""",
unsafe_allow_html=True)

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
# ---------- Rewire logo + title on one row ----------
logo = Image.open("rewire_dtx_logo.jpg")
col_logo, col_title = st.columns([1, 8])   # 1 : 8 width ratio (tweak as needed)
with col_logo:
    st.image(logo, width=60)               # logo size
with col_title:
    st.markdown("## Rewire Therapist Dashboard")   # H2 keeps height balanced
pid = st.selectbox("Select Patient", list(patients.keys()))
pname  = patients[pid]["name"]
pdiag  = patients[pid]["diagnosis"]
st.markdown(f"### {pname} ({pid})   |   **Diagnosis:** {pdiag}")
# ---- reset homework visibility when the therapist switches patients ----
if st.session_state.get("last_pid") != pid:
    st.session_state["assessment_done"] = False      # hide homework until new assessment
    st.session_state[f"plan_submitted_{pid}"] = False      # reset homework-sent flag for this patient
    st.session_state["last_pid"] = pid
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

if bio_df is None or bio_df.empty or eeg_df is None or eeg_df.empty:
    st.info("Click **🔄 Sync Latest Data** to load the newest biometrics and EEG.")
else:
    # ---------- BIOMETRIC SNAPSHOT ----------
    latest_bio = bio_df[bio_df["patient_id"] == pid].iloc[-1]
    st.markdown("#### Latest Biometric Snapshot")
    col1, col2 = st.columns(2)
    col1.metric("Resting HR",   f"{latest_bio['resting_hr']} bpm")
    col2.metric("HRV",          f"{latest_bio['hrv']} ms")

    # ---------- BIOMETRIC TRENDS ----------
    st.markdown("#### 📊 30-Day Biometric Trends")
    trend_cols = ["resting_hr", "hrv"]
    bio_trend = (bio_df[bio_df["patient_id"] == pid]
                 .sort_values("date")    # assume your CSV has a 'date' column
                 .tail(30)[trend_cols]
                 .reset_index(drop=True))
    st.line_chart(bio_trend)

    # Simple textual cue
    delta_hrv = int(bio_trend["hrv"].iloc[-1] - bio_trend["hrv"].iloc[0])

    if delta_hrv > 5:
        hrv_sentence = f"HRV improved by {delta_hrv} ms 💙 over the last {len(bio_trend)} days."
    elif delta_hrv < -5:
        hrv_sentence = f"HRV declined by {abs(delta_hrv)} ms 🔻 over the last {len(bio_trend)} days."
    else:
        hrv_sentence = f"HRV remained within ±5 ms ⚪️ (change: {delta_hrv} ms) during the last {len(bio_trend)} days."

    st.caption(hrv_sentence)
    # Resting HR trend
    delta_hr = int(bio_trend["resting_hr"].iloc[-1] - bio_trend["resting_hr"].iloc[0])
    if delta_hr > 5:
        hr_sentence = f"Resting HR rose by {delta_hr} bpm 🔻 in the last {len(bio_trend)} days."
    elif delta_hr < -5:
        hr_sentence = f"Resting HR dropped by {abs(delta_hr)} bpm 💙 over {len(bio_trend)} days."
    else:
        hr_sentence = f"Resting HR stayed within ±5 bpm ⚪️ (change: {delta_hr} bpm)."

    st.caption(hr_sentence)

    # ---------- EEG TREND + EXPLANATION ----------
    st.markdown("#### 🧠 EEG Trend (FAA & TBR, last 4 sessions)")
    pt_eeg = eeg_df[eeg_df["patient_id"] == pid].tail(4)

    if pt_eeg.empty:
        st.info("No EEG records for this patient yet.")
    else:
        # Normalise so FAA / TBR share the scale
        z = (pt_eeg[["faa","tbr"]] - pt_eeg[["faa","tbr"]].mean()) / pt_eeg[["faa","tbr"]].std()
        z.index = range(1, len(z)+1)
        st.line_chart(z)

        # Plain-language interpretation of the *latest* reading
        faa = pt_eeg["faa"].iloc[-1]; tbr = pt_eeg["tbr"].iloc[-1]
        if faa < -0.2 and tbr > 0.6:
            interp = "⚠️ pattern suggests cognitive dysregulation (low mood + focus issues)."
        elif faa < -0.2:
            interp = "⬇️ asymmetry points to low motivation / mood disturbance."
        elif tbr > 0.6:
            interp = "↑ high TBR indicates focus/attention difficulty."
        else:
            interp = "✅ EEG within expected clinical range."

        st.caption(f"Latest EEG reading: {interp}")

# -------------- 3. IN-CLINIC SESSION INPUT --------------
st.markdown("---")
st.subheader("📋 In-Clinic Session Notes")
with st.form("session_form"):
    meds_taken = st.radio("Medication adherence reported?", ("Yes", "No", "NA"))
    therapist_note = st.text_area("Observations / triggers during session")
    run_btn = st.form_submit_button("Run Risk Assessment")

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
    st.session_state[f"risk_level_{pid}"] = level
    st.subheader(f"{icon} Stress Risk: **{level}**   · Score {score}/100")
    # ---- mark that this patient has a completed assessment ----
    st.session_state["assessment_done"] = True
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
            colour = "seagreen" if delta < -0.3 else "orangered" if delta > 0.3 else "lightgrey"

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
if st.session_state.get("assessment_done"):
    # pull back the risk level you stored earlier (or default to "Low")
    level_key = f"risk_level_{pid}"
    level     = st.session_state.get(level_key, "Low")

    st.markdown("---")
    st.subheader("Homework Plan Builder")
    st.info(
        f"Plan suggested from latest EEG & biometrics "
        f"(diagnosis **{pdiag}**, risk **{level}**). You can edit anything."
    )

    # init per‐patient defaults exactly once
    defaults_key = f"{pid}_defaults"
    if defaults_key not in st.session_state:
        if level == "High":
            games  = ["Cognitive Reframing","Emotion Labeling","Guided Breathing"]
            freqs  = [7,5,7]
        elif level == "Moderate":
            games  = ["Cognitive Flexibility","Emotion Check-In","Guided Breathing"]
            freqs  = [4,3,7]
        else:
            games  = ["Resilience Booster","Emotion Check-In","Evening Calm"]
            freqs  = [2,2,5]
        if pdiag == "PTSD":
            games[1], freqs[1] = "Stress Inoculation", 4
        st.session_state[defaults_key] = {"games":games,"freqs":freqs,"note":"Focus on consistency this week."}

    defaults = st.session_state[defaults_key]
    choices  = game_options[pdiag]

    # one form with three selects + sliders + text area
    with st.form(key=f"plan_form_{pid}", clear_on_submit=False):
        idx1 = choices.index(defaults["games"][0]) if defaults["games"][0] in choices else 0
        idx2 = choices.index(defaults["games"][1]) if defaults["games"][1] in choices else 0
        idx3 = choices.index(defaults["games"][2]) if defaults["games"][2] in choices else 0

        g1 = st.selectbox("Cognitive Game",           choices, index=idx1, key=f"g1_{pid}")
        g2 = st.selectbox("Emotion Regulation Game",   choices, index=idx2, key=f"g2_{pid}")
        g3 = st.selectbox("Evening Wind-down Game",    choices, index=idx3, key=f"g3_{pid}")

        f1 = st.slider(f"{g1} per week", 1, 7, defaults["freqs"][0])
        f2 = st.slider(f"{g2} per week", 1, 7, defaults["freqs"][1])
        f3 = st.slider(f"{g3} per week", 1, 7, defaults["freqs"][2])

        note = st.text_area("Message to patient", value=defaults["note"])

        sent = st.form_submit_button("💾 Save & Send Plan")
        if sent:
            st.session_state[defaults_key] = {"games":[g1,g2,g3],"freqs":[f1,f2,f3],"note":note}
            st.session_state[f"plan_submitted_{pid}"] = True
            st.success("✅ Homework plan sent to patient app and email.")

    # after‐submit confirmation
    flag = f"plan_submitted_{pid}"
    if st.session_state.get(flag):
        st.markdown("### Plan Sent to Patient and Saved in EHR")
        plan = st.session_state[defaults_key]
        for game, freq in zip(plan["games"], plan["freqs"]):
            st.markdown(f"- **{game}**: {freq}×/wk")
        st.markdown(f"**Note:** {plan['note']}")
        st.toast("Report sent and saved ✔️", icon="✅")            
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
# -----------------------------
# Sidebar: Regulatory Notice
# -----------------------------
with st.sidebar.expander("Regulatory Notice"):
    st.markdown("""
    **Intended Classification**: FDA **Class II** Software as a Medical Device (SaMD)  
    **Planned Pathway**: 510(k) using NeuroFormance™ as predicate  
    **Key Frameworks**  
        - IMDRF risk-based classification  
        - HIPAA / PHIPA data-privacy compliance  
        - Design History File (DHF) & post-market surveillance  
        - AI/ML transparency & human-in-the-loop oversight  
    """)
    # -----------------------------
    # Sidebar: Contact Rewire
    # -----------------------------
    with st.sidebar.expander("Contact Rewire"):
        st.markdown("""
        **Email**  
        [info@rewiredtx.com](mailto:info@rewiredtx.com)

        **Office**  
        #208 – 698 Seymour St  
        Vancouver, BC  
        Canada
        """)
# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("Questions or concerns? Contact **maureen@rewiredtx.com** or visit [rewiredtx.com](https://www.rewiredtx.com)")
st.info("This tool is for demonstration purposes only and not yet approved for clinical use.")

st.caption("Version 0.4 · Last updated: May 13, 2025")

