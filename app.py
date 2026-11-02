"""BPD research calculator deployment reconstructed from reported Table S5.

The archived full-precision parameter export and original app are unavailable.
This app uses the reported rounded standardized coefficients and preprocessing
parameters. It does not load patient data or fit any model.
"""

import json
import math
from pathlib import Path

import streamlit as st


HERE = Path(__file__).resolve().parent
SPEC = json.loads((HERE / "model_parameters.json").read_text(encoding="utf-8"))
# Counts describe availability patterns in the historical 1,958-record model.
PATTERN_COUNTS = {
    "0000000": 383, "0000010": 1, "0000101": 868, "0001101": 4,
    "0010000": 2, "0010011": 364, "0010111": 335, "0100101": 1,
}


def predict(values):
    logit = SPEC["intercept"]
    for term in SPEC["terms"]:
        observed = values[term["original_feature"]]
        if term["type"] == "Clinical value":
            value = term["median"] if observed is None else observed
        else:
            value = float(observed is None)
        logit += term["coefficient"] * (value - term["mean"]) / term["scale"]
    if logit >= 0:
        return 1 / (1 + math.exp(-logit))
    exp_logit = math.exp(logit)
    return exp_logit / (1 + exp_logit)


def reset_example():
    defaults = {
        "birthweight_g": 1800,
        "ga_category": 1,
        "maternal_age": 28,
        "hdp": "No (0)",
        "prom": "No (0)",
        "gdm": "No (0)",
        "apgar5": 8,
        "maternal_age_missing": False,
        "apgar5_missing": False,
    }
    st.session_state.update(defaults)


st.set_page_config(page_title="BPD research calculator", page_icon="🧮", layout="wide")
st.markdown(
    """<style>
    .stApp {background:#ffffff; color:#233642;}
    .block-container {max-width:1260px; padding-top:2.2rem; padding-bottom:1.5rem;}
    header[data-testid="stHeader"] {background:transparent;}
    #MainMenu, footer, [data-testid="stToolbar"] {visibility:hidden;}
    .eyebrow {font-size:11px; letter-spacing:2px; color:#69838c; font-weight:700;}
    .app-title {font:700 40px Georgia,serif; color:#233642; margin:8px 0 10px;}
    .subtitle {font-size:14px; color:#73858e; margin-bottom:15px;}
    .scope {background:#faf8e9; color:#7d7041; padding:12px 15px; font-size:14px;
      border-radius:5px; margin-bottom:24px;}
    .section-title {font-size:24px; font-weight:700; margin:0 0 16px; color:#233642;}
    .output-label {font-size:14px; color:#73858e; margin:10px 0 3px;}
    .probability {font-size:47px; line-height:1.2; color:#3f646f; margin-bottom:20px;}
    .score-group {font-size:27px; color:#3f646f; line-height:1.3; margin-bottom:18px;}
    .score-note {background:#eef5fa; color:#466277; padding:15px; border-radius:6px;
      font-size:14px; margin-top:19px;}
    </style>""",
    unsafe_allow_html=True,
)
st.markdown('<div class="eyebrow">RESEARCH SOFTWARE / PUBLIC-DATA-DERIVED MODEL</div>', unsafe_allow_html=True)
st.markdown('<div class="app-title">BPD research calculator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Dataset-recorded BPD-related binary outcome · Seven clinical inputs</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="scope">Research use only. Clinical utility and endpoint equivalence have not been established.</div>',
    unsafe_allow_html=True,
)

left, right = st.columns([1.16, 1], gap="large")
with left:
    st.markdown('<div class="section-title">01 / Model inputs</div>', unsafe_allow_html=True)
    st.button("Load synthetic example", on_click=reset_example, help="Example inputs, not a patient record.")
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        bw = st.number_input("Birth weight (g)", min_value=300, max_value=2499, value=1800, step=10, key="birthweight_g")
    with c2:
        ga_labels = [
            "1: <28 weeks", "2: 28+0–31+6 weeks", "3: 32+0–33+6 weeks",
            "4: 34+0–36+6 weeks", "Not available",
        ]
        ga_index = st.selectbox("Gestational-age group", options=range(5), index=1, format_func=lambda i: ga_labels[i], key="ga_category")
    with c1:
        age = st.number_input("Maternal age (years)", min_value=10, max_value=65, value=28, step=1, key="maternal_age")
    with c2:
        hdp = st.selectbox("HDP", ["No (0)", "Yes (1)", "Not available"], key="hdp", help="Hypertensive disorder of pregnancy")
    with c1:
        prom = st.selectbox("PROM", ["No (0)", "Yes (1)", "Not available"], key="prom", help="Premature rupture of membranes")
    with c2:
        gdm = st.selectbox("GDM", ["No (0)", "Yes (1)", "Not available"], key="gdm", help="Gestational diabetes mellitus")
    with c1:
        apgar = st.number_input("5-minute Apgar score", min_value=0, max_value=10, value=8, step=1, key="apgar5")
    with st.expander("Unavailable numeric inputs"):
        age_missing = st.checkbox("Maternal age not available", key="maternal_age_missing")
        apgar_missing = st.checkbox("5-minute Apgar score not available", key="apgar5_missing")
    st.caption("Gestational-age groups follow the reported week bands. Available values are used before imputation.")

binary = lambda label: None if label == "Not available" else float(label == "Yes (1)")
values = {
    "birthweight_g": bw,
    "ga_category": None if ga_index == 4 else ga_index + 1,
    "maternal_age": None if age_missing else age,
    "hdp": binary(hdp), "prom": binary(prom), "gdm": binary(gdm),
    "apgar5": None if apgar_missing else apgar,
}
probability = predict(values)
lower, upper = SPEC["score_tertiles"]
group = "Lower" if probability <= lower else "Intermediate" if probability <= upper else "Higher"
missing = sum(value is None for value in values.values())

with right:
    st.markdown('<div class="section-title">02 / Research output</div>', unsafe_allow_html=True)
    pattern = "".join("1" if value is None else "0" for value in values.values())
    if PATTERN_COUNTS.get(pattern, 0) == 0:
        st.warning(
            "This combination of missing inputs did not occur in model development. "
            "The output below is an extrapolation of the research function and is not a validated individual risk."
        )
    st.markdown('<div class="output-label">Model probability</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="probability">{probability:.1%}</div>', unsafe_allow_html=True)
    st.markdown('<div class="output-label">Exploratory score stratum</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="score-group">{group} score group</div>', unsafe_allow_html=True)
    st.caption(f"Missing inputs: {missing} / 7 · Automatic updates")
    st.markdown("**Public-development score tertiles**")
    st.caption(f"Lower ≤ {lower:.6f}")
    st.caption(f"Intermediate > {lower:.6f} to ≤ {upper:.6f}")
    st.caption(f"Higher > {upper:.6f}")
    st.markdown(
        '<div class="score-note">Score groups describe the public-development prediction distribution. '
        'They are not clinical action thresholds. No individual prediction interval is available.</div>',
        unsafe_allow_html=True,
    )

with st.expander("Model provenance and missing-data handling"):
    st.write(
        "This research app was reconstructed from the rounded standardized coefficients and preprocessing "
        "parameters in Supplementary Table S5. The original application and full-precision parameter "
        "export were not recovered. A public-data refit reproduced the reported coefficients; "
        "its outputs agreed with this rounded function within 1.1e-10 across 64 synthetic availability patterns. "
        "This interface retains the historical specification; corrected models are separate research versions."
    )
    st.write(
        "A missing input invokes its reported public-development median and the corresponding "
        "missingness indicator. Model coefficients are applied directly; no fitting or recalibration occurs."
    )
    st.write(
        "The reported model was developed using 1,958 public records and evaluated on 3,031 external "
        "records with birth weight below 2,500 g. This interface does not load or save patient records."
    )
    st.caption("Source: Supplementary Table S5, reported parameter specification")
st.caption("Reported Table S5 parameter specification · Research use only")
