import pickle
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Customer Churn Predictor", page_icon="🔄", layout="centered")

YES_NO = {'Yes': 1, 'No': 0}
GENDER_MAP = {'Female': 1, 'Male': 0}
DUMMY_COLS = ['InternetService', 'OnlineSecurity', 'OnlineBackup', 'MultipleLines',
              'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
              'PaymentMethod', 'Contract']


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

    # Support either {"model":..., "feature_cols":...} or a bare model object
    if isinstance(obj, dict):
        model = obj["model"]
        feature_cols = obj.get("feature_cols") or list(model.get_booster().feature_names)
    else:
        model = obj
        feature_cols = list(model.get_booster().feature_names)
    return model, feature_cols


st.title("🔄 Customer Churn Predictor")
st.caption("Loads a pre-trained model from model.pkl")

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

st.divider()
st.subheader("Enter customer details")

col1, col2 = st.columns(2)
with col1:
    senior = st.selectbox("Senior Citizen", ["No", "Yes"])
    partner = st.selectbox("Partner", ["Yes", "No"])
    dependents = st.selectbox("Dependents", ["Yes", "No"])
    tenure = st.number_input("Tenure (months)", min_value=0, max_value=100, value=12)
    phone_service = st.selectbox("Phone Service", ["Yes", "No"])
    multiple_lines = st.selectbox("Multiple Lines", ["No", "Yes", "No phone service"])
    internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
    online_security = st.selectbox("Online Security", ["No", "Yes", "No internet service"])
    online_backup = st.selectbox("Online Backup", ["No", "Yes", "No internet service"])
with col2:
    device_protection = st.selectbox("Device Protection", ["No", "Yes", "No internet service"])
    tech_support = st.selectbox("Tech Support", ["No", "Yes", "No internet service"])
    streaming_tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"])
    streaming_movies = st.selectbox("Streaming Movies", ["No", "Yes", "No internet service"])
    contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
    paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
    payment_method = st.selectbox("Payment Method", [
        "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
    ])
    monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, value=70.0, step=0.5)
    total_charges = st.number_input("Total Charges ($)", min_value=0.0, value=800.0, step=1.0)

if st.button("Predict Churn", type="primary"):
    row = pd.DataFrame([{
        "SeniorCitizen": 1 if senior == "Yes" else 0,
        "Partner": partner, "Dependents": dependents, "tenure": tenure,
        "PhoneService": phone_service, "MultipleLines": multiple_lines,
        "InternetService": internet_service, "OnlineSecurity": online_security,
        "OnlineBackup": online_backup, "DeviceProtection": device_protection,
        "TechSupport": tech_support, "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies, "Contract": contract,
        "PaperlessBilling": paperless_billing, "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges, "TotalCharges": total_charges,
    }])
    processed = preprocess(row).reindex(columns=feature_cols, fill_value=0)
    pred = model.predict(processed)[0]
    prob = model.predict_proba(processed)[0][1]

    if pred == 1:
        st.error(f"⚠️ Likely to churn — probability {prob:.1%}")
    else:
        st.success(f"✅ Likely to stay — churn probability {prob:.1%}")
    st.progress(min(int(prob * 100), 100))