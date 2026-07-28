import pickle
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Customer Churn Intelligence", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

YES_NO = {'Yes': 1, 'No': 0}
GENDER_MAP = {'Female': 1, 'Male': 0}
DUMMY_COLS = ['InternetService', 'OnlineSecurity', 'OnlineBackup', 'MultipleLines',
              'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
              'PaymentMethod', 'Contract']

st.markdown("""
<style>
    #MainMenu, footer, [data-testid="stSidebar"] { display: none; }
    .stApp { background: #f7f8fa; color: #172033; }
    .block-container { max-width: 1280px; padding: 3.2rem 2rem 4.5rem; }
    [data-testid="stHeader"] { background: transparent; }
    .hero { margin-bottom: 2.5rem; }
    .hero-eyebrow { color: #637083; font-size: .76rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; margin-bottom: .65rem; }
    .hero h1 { color: #152033; font-size: clamp(2.25rem, 5vw, 3.7rem); line-height: 1.06; letter-spacing: -.055em; margin: 0 0 .85rem; }
    .hero p { color: #637083; font-size: 1.06rem; line-height: 1.65; max-width: 720px; margin: 0; }
    .badge-row { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.25rem; }
    .badge { background: #fff; border: 1px solid #e4e8ee; border-radius: 999px; color: #526074; font-size: .78rem; font-weight: 650; padding: .38rem .72rem; }
    .badge b { color: #19253a; }
    .section-label { color: #657186; font-size: .78rem; font-weight: 750; letter-spacing: .1em; text-transform: uppercase; margin: .6rem 0 1rem; }
    [data-testid="stVerticalBlockBorderWrapper"] { background: #fff; border: 1px solid #e7ebf0; border-radius: 18px; box-shadow: 0 4px 16px rgba(23,32,51,.035); transition: transform .18s ease, box-shadow .18s ease; }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(23,32,51,.07); }
    [data-testid="stVerticalBlockBorderWrapper"] > div { padding: .35rem .3rem .45rem; }
    .card-title { color: #18243a; font-size: 1.06rem; font-weight: 750; letter-spacing: -.02em; margin: .35rem 0 1.15rem; }
    .card-title span { background: #eef3ff; border-radius: 10px; display: inline-flex; margin-right: .55rem; padding: .36rem .46rem; }
    label, [data-testid="stWidgetLabel"] p { color: #425069 !important; font-size: .84rem !important; font-weight: 650 !important; }
    [data-baseweb="select"] > div, [data-testid="stNumberInput"] input { border-color: #e1e6ed !important; border-radius: 10px !important; background: #fcfdff !important; }
    [data-testid="stNumberInput"] input { color: #111827 !important; -webkit-text-fill-color: #111827 !important; opacity: 1 !important; }
    [data-baseweb="select"] *, [role="listbox"] *, [data-baseweb="popover"] * { color: #111827 !important; }
    [data-baseweb="popover"], [data-baseweb="popover"] [role="listbox"], [role="option"] { background-color: #ffffff !important; }
    [role="option"]:hover, [role="option"][aria-selected="true"] { background-color: #f1f5f9 !important; }
    [data-baseweb="select"] > div:focus-within, [data-testid="stNumberInput"] input:focus { border-color: #7185dd !important; box-shadow: 0 0 0 3px #7185dd20 !important; }
    [data-testid="stForm"] { border: 0; padding: 0; }
    [data-testid="stFormSubmitButton"] { margin-top: 1.65rem; }
    [data-testid="stFormSubmitButton"] button { border: 0; border-radius: 14px; min-height: 3.35rem; background: #253b80; color: white; font-size: 1rem; font-weight: 700; box-shadow: 0 8px 18px rgba(37,59,128,.2); transition: transform .18s ease, box-shadow .18s ease, background .18s ease; }
    [data-testid="stFormSubmitButton"] button:hover { background: #1c306d; transform: translateY(-2px); box-shadow: 0 12px 24px rgba(37,59,128,.27); }
    .results-heading { color: #172033; font-size: 1.55rem; font-weight: 780; letter-spacing: -.035em; margin: 3.5rem 0 1rem; }
    .kpi-card, .result-card { background: #fff; border: 1px solid #e7ebf0; border-radius: 18px; box-shadow: 0 4px 16px rgba(23,32,51,.035); }
    .kpi-card { min-height: 120px; padding: 1.1rem 1.25rem; }
    .kpi-icon { font-size: 1.05rem; margin-bottom: .48rem; }
    .kpi-value { color: #172033; font-size: 1.55rem; font-weight: 780; letter-spacing: -.04em; line-height: 1.05; }
    .kpi-caption { color: #79869a; font-size: .78rem; margin-top: .35rem; }
    .result-card { padding: 1.4rem 1.55rem; min-height: 100%; transition: box-shadow .18s ease; }
    .result-card:hover { box-shadow: 0 12px 30px rgba(23,32,51,.07); }
    .result-overline { color: #738096; font-size: .73rem; font-weight: 750; letter-spacing: .1em; text-transform: uppercase; margin-bottom: .5rem; }
    .result-title { color: #172033; font-size: 1.45rem; font-weight: 780; letter-spacing: -.04em; margin-bottom: .35rem; }
    .result-divider { border: 0; border-top: 1px solid #edf0f4; margin: 1.15rem 0; }
    .detail-label { color: #788599; font-size: .78rem; font-weight: 650; margin-bottom: .15rem; }
    .detail-value { color: #1e2a3e; font-size: 1rem; font-weight: 720; margin-bottom: .9rem; }
    .risk-badge { display: inline-block; padding: .32rem .72rem; border-radius: 999px; font-size: .76rem; font-weight: 700; letter-spacing: .02em; }
    .risk-low { background: #16a34a22; color: #16803c; } .risk-medium { background: #d9770622; color: #b85e00; } .risk-high { background: #dc262622; color: #c72424; }
    .summary-grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 1px; background: #edf0f4; border: 1px solid #edf0f4; border-radius: 13px; overflow: hidden; margin-top: .95rem; }
    .summary-item { background: #fff; min-height: 78px; padding: .85rem 1rem; } .summary-item small { display: block; color: #7c889a; font-size: .72rem; font-weight: 650; margin-bottom: .3rem; } .summary-item strong { color: #26334a; font-size: .9rem; font-weight: 700; overflow-wrap: anywhere; }
    @media (max-width: 700px) { .block-container { padding: 2rem 1rem 3rem; } .hero h1 { font-size: 2.25rem; } .summary-grid { grid-template-columns: 1fr; } }
</style>
""", unsafe_allow_html=True)


def preprocess(df):
    """Same encoding as the notebook: yes/no maps, gender map, dummies."""
    df = df.copy()
    for col in ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling']:
        if col in df.columns:
            df[col] = df[col].map(YES_NO)
    if 'gender' in df.columns:
        df['gender'] = df['gender'].map(GENDER_MAP)
    for col in DUMMY_COLS:
        if col in df.columns:
            df = pd.get_dummies(df, columns=[col], drop_first=True)
    bool_cols = df.select_dtypes(include='bool').columns
    df[bool_cols] = df[bool_cols].astype(int)
    return df


@st.cache_resource
def load_model(path="model.pkl"):
    with open(path, "rb") as f:
        obj = pickle.load(f)
    if isinstance(obj, dict):
        model = obj["model"]
        feature_cols = obj.get("feature_cols") or list(model.get_booster().feature_names)
    else:
        model = obj
        feature_cols = list(model.get_booster().feature_names)
    return model, feature_cols


def gauge(prob):
    color = "#dc2626" if prob >= 0.6 else "#d97706" if prob >= 0.3 else "#16a34a"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=prob * 100,
        number={"suffix": "%", "font": {"size": 48, "color": "#172033"}},
        gauge={"axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)", "tickfont": {"color": "#60708a", "size": 14}},
               "bar": {"color": color, "thickness": 0.38}, "bgcolor": "#e8edf3", "borderwidth": 0,
               "steps": [{"range": [0, 30], "color": "rgba(22,163,74,0.22)"}, {"range": [30, 60], "color": "rgba(217,119,6,0.22)"}, {"range": [60, 100], "color": "rgba(220,38,38,0.22)"}]},
    ))
    fig.update_layout(height=340, margin=dict(l=20, r=20, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", font={"size": 14})
    return fig


st.markdown('''<section class="hero"><div class="hero-eyebrow">Customer Analytics / Prediction</div><h1>Customer Churn Intelligence</h1><p>Predict customer churn using an optimized XGBoost machine learning model trained on telecom customer behavior.</p><div class="badge-row"><span class="badge"><b>Model:</b> XGBoost</span><span class="badge"><b>Task:</b> Binary Classification</span><span class="badge"><b>Output:</b> Churn Probability</span></div></section>''', unsafe_allow_html=True)

try:
    model, feature_cols = load_model()
except FileNotFoundError:
    st.warning("Couldn't find `model.pkl` next to this app.")
    uploaded_model = st.file_uploader("Upload model.pkl", type="pkl")
    if uploaded_model:
        obj = pickle.load(uploaded_model)
        if isinstance(obj, dict):
            model = obj["model"]
            feature_cols = obj.get("feature_cols") or list(model.get_booster().feature_names)
        else:
            model = obj
            feature_cols = list(model.get_booster().feature_names)
    else:
        st.stop()

st.markdown('<div class="section-label">Customer profile</div>', unsafe_allow_html=True)
with st.form("customer_profile"):
    form_left, form_right = st.columns(2, gap="large")
    with form_left:
        with st.container(border=True):
            st.markdown('<div class="card-title"><span>👤</span>Demographics</div>', unsafe_allow_html=True)
            senior = st.selectbox("Senior Citizen", ["No", "Yes"])
            partner = st.selectbox("Partner", ["Yes", "No"])
            dependents = st.selectbox("Dependents", ["Yes", "No"])
            tenure = st.slider("Tenure (months)", 0, 100, 12)
    with form_right:
        with st.container(border=True):
            st.markdown('<div class="card-title"><span>💳</span>Billing</div>', unsafe_allow_html=True)
            contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
            paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
            payment_method = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
            bill_cols = st.columns(2)
            monthly_charges = bill_cols[0].number_input("Monthly Charges ($)", min_value=0.0, value=70.0, step=0.5)
            total_charges = bill_cols[1].number_input("Total Charges ($)", min_value=0.0, value=800.0, step=1.0)
    st.markdown('<div style="height: 1.25rem"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="card-title"><span>📶</span>Internet &amp; Services</div>', unsafe_allow_html=True)
        s1, s2, s3 = st.columns(3, gap="medium")
        phone_service = s1.selectbox("Phone Service", ["Yes", "No"])
        multiple_lines = s2.selectbox("Multiple Lines", ["No", "Yes", "No phone service"])
        internet_service = s3.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
        online_security = s1.selectbox("Online Security", ["No", "Yes", "No internet service"])
        online_backup = s2.selectbox("Online Backup", ["No", "Yes", "No internet service"])
        device_protection = s3.selectbox("Device Protection", ["No", "Yes", "No internet service"])
        tech_support = s1.selectbox("Tech Support", ["No", "Yes", "No internet service"])
        streaming_tv = s2.selectbox("Streaming TV", ["No", "Yes", "No internet service"])
        streaming_movies = s3.selectbox("Streaming Movies", ["No", "Yes", "No internet service"])
    predict_clicked = st.form_submit_button("Predict Churn", use_container_width=True)

if predict_clicked:
    row = pd.DataFrame([{
        "SeniorCitizen": 1 if senior == "Yes" else 0, "Partner": partner, "Dependents": dependents, "tenure": tenure,
        "PhoneService": phone_service, "MultipleLines": multiple_lines, "InternetService": internet_service,
        "OnlineSecurity": online_security, "OnlineBackup": online_backup, "DeviceProtection": device_protection,
        "TechSupport": tech_support, "StreamingTV": streaming_tv, "StreamingMovies": streaming_movies,
        "Contract": contract, "PaperlessBilling": paperless_billing, "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges, "TotalCharges": total_charges,
    }])
    processed = preprocess(row).reindex(columns=feature_cols, fill_value=0)
    pred = model.predict(processed)[0]
    prob = model.predict_proba(processed)[0][1]

    if prob >= 0.6:
        risk_label, risk_class = "High Risk", "risk-high"
    elif prob >= 0.3:
        risk_label, risk_class = "Medium Risk", "risk-medium"
    else:
        risk_label, risk_class = "Low Risk", "risk-low"

    prediction_text = "Likely to Churn" if pred == 1 else "Likely to Stay"
    confidence = max(prob, 1 - prob) * 100
    recommendation = ("Offer a loyalty discount or encourage migration to a long-term contract." if pred == 1 else "Maintain engagement with proactive service check-ins and personalized retention offers.")

    st.markdown('<div class="results-heading">Prediction dashboard</div>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    k1.markdown(f'<div class="kpi-card"><div class="kpi-icon">◔</div><div class="kpi-value">{prob:.0%}</div><div class="kpi-caption">Churn probability</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><div class="kpi-icon">◈</div><div class="kpi-value">{risk_label.replace(" Risk", "")}</div><div class="kpi-caption">Risk level</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card"><div class="kpi-icon">↗</div><div class="kpi-value">{prediction_text}</div><div class="kpi-caption">Model prediction</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card"><div class="kpi-icon">▣</div><div class="kpi-value">{contract}</div><div class="kpi-caption">Contract type</div></div>', unsafe_allow_html=True)

    chart_col, summary_col = st.columns([1.15, .85], gap="large")
    with chart_col:
        st.markdown('<div class="result-card"><div class="result-overline">Probability analysis</div>', unsafe_allow_html=True)
        st.plotly_chart(gauge(prob), use_container_width=True, config={"displayModeBar": False})
        a, b, c = st.columns(3)
        a.markdown(f'<div class="detail-label">PROBABILITY</div><div class="detail-value">{prob:.1%}</div>', unsafe_allow_html=True)
        b.markdown(f'<div class="detail-label">CONFIDENCE</div><div class="detail-value">{confidence:.0f}%</div>', unsafe_allow_html=True)
        c.markdown(f'<div class="detail-label">RISK LEVEL</div><div class="detail-value"><span class="risk-badge {risk_class}">{risk_label}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with summary_col:
        icon = "⚠️" if pred == 1 else "✓"
        st.markdown(f'''<div class="result-card"><div class="result-overline">Prediction summary</div><div class="result-title">{icon} {prediction_text}</div><span class="risk-badge {risk_class}">{risk_label}</span><hr class="result-divider"><div class="detail-label">CONFIDENCE</div><div class="detail-value">{confidence:.0f}%</div><div class="detail-label">RECOMMENDATION</div><div class="detail-value" style="line-height:1.55; font-weight:600">{recommendation}</div></div>''', unsafe_allow_html=True)

    st.markdown('<div style="height:1.25rem"></div>', unsafe_allow_html=True)
    st.markdown('<div class="result-card"><div class="result-overline">Customer summary</div><div class="result-title">Profile at a glance</div><div class="summary-grid">' +
                f'<div class="summary-item"><small>TENURE</small><strong>{tenure} months</strong></div><div class="summary-item"><small>INTERNET SERVICE</small><strong>{internet_service}</strong></div><div class="summary-item"><small>CONTRACT</small><strong>{contract}</strong></div><div class="summary-item"><small>PAYMENT METHOD</small><strong>{payment_method}</strong></div><div class="summary-item"><small>MONTHLY CHARGES</small><strong>${monthly_charges:,.2f}</strong></div><div class="summary-item"><small>TOTAL CHARGES</small><strong>${total_charges:,.2f}</strong></div><div class="summary-item"><small>PAPERLESS BILLING</small><strong>{paperless_billing}</strong></div><div class="summary-item"><small>PHONE SERVICE</small><strong>{phone_service}</strong></div></div></div>', unsafe_allow_html=True)
