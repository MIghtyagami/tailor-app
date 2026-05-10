import streamlit as st
from PyPDF2 import PdfReader
from fpdf import FPDF
from openai import OpenAI
import json

# ==========================================
# 1. WEB APP CONFIG & THEMING
# ==========================================
st.set_page_config(page_title="OceanTailor AI v2.0", layout="wide", page_icon="🌊")

st.markdown("""
    <style>
    .stApp { background-color: #E0F7FA; }
    h1, h2, h3 { color: #006064 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { 
        background-color: #00ACC1; color: white; border-radius: 12px; 
        border: none; font-weight: bold; width: 100%; 
    }
    .stButton>button:hover { background-color: #00838F; color: white; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
        border: 2px solid #00ACC1 !important; border-radius: 10px; 
    }
    .profile-card { 
        padding: 20px; background-color: #B2EBF2; border-radius: 15px; 
        border-left: 8px solid #006064; margin-bottom: 25px; 
    }
    .metric-card {
        background-color: white; padding: 15px; border-radius: 10px;
        border: 1px solid #B2EBF2; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIC FUNCTIONS
# ==========================================
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "".join([page.extract_text() for page in reader.pages])

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Replace non-latin-1 characters to prevent crashes
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

def analyze_resume(base_text, jd, api_key):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    Analyze the following Resume against the Job Description. 
    Return ONLY a JSON object with these keys: 
    'match_score' (percentage 0-100), 
    'missing_keywords' (list of top 5 critical missing skills), 
    'improvement_tips' (2 short bullet points).
    
    JD: {jd}
    Resume: {base_text}
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125", # Using latest stable
        messages=[{"role": "system", "content": "You are an ATS scanning expert. Return JSON only."},
                  {"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

def tailor_resume(base_text, company, jd, api_key):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    You are a world-class professional resume writer. 
    Company: {company}
    Job Description: {jd}
    Base Resume: {base_text}
    
    Instructions:
    1. Rewrite the 'Experience' section using the Google XYZ formula: "Accomplished [X] as measured by [Y], by doing [Z]".
    2. Seamlessly integrate high-impact keywords from the JD.
    3. Keep contact information and education exactly as is.
    4. Use a professional, executive tone.
    5. Return ONLY the final polished resume text.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are an expert ATS resume writer."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ==========================================
# 3. PROFILE MANAGEMENT
# ==========================================
if 'profiles' not in st.session_state:
    st.session_state.profiles = {}

# ==========================================
# 4. UI LAYOUT
# ==========================================
st.title("🌊 OceanTailor AI v2.0")
st.markdown("#### *The Professional ATS-Optimized Resume Engine*")

with st.sidebar:
    st.header("👤 User Profiles")
    new_p = st.text_input("Profile Name (e.g. Project Manager)")
    if st.button("➕ Create Profile"):
        if new_p:
            st.session_state.profiles[new_p] = ""
            st.success(f"Profile '{new_p}' Created!")

    st.divider()
    profile_list = list(st.session_state.profiles.keys())
    active_profile = st.selectbox("Select Active Profile", profile_list) if profile_list else None

if active_profile:
    st.markdown(f"<div class='profile-card'><b>Current Profile:</b> {active_profile}</div>", unsafe_allow_html=True)
    
    api_key = st.text_input("🔑 Enter OpenAI API Key", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📄 Base Resume")
        up_file = st.file_uploader("Upload PDF", type="pdf")
        if up_file:
            st.session_state.profiles[active_profile] = extract_text_from_pdf(up_file)
            st.success("Resume Loaded!")

    with col2:
        st.subheader("🎯 Job Target")
        comp = st.text_input("Company Name")
        jd = st.text_area("Job Description", height=200)

    st.divider()
    
    # ACTION BUTTONS
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("🔍 Analyze Match Score"):
            if not api_key or not st.session_state.profiles[active_profile] or not jd:
                st.error("Missing API Key, Resume, or JD!")
            else:
                with st.spinner("Scanning for keywords..."):
                    try:
                        analysis = analyze_resume(st.session_state.profiles[active_profile], jd, api_key)
                        st.session_state.analysis = analysis
                    except Exception as e:
                        st.error(f"Error: {e}")

    with btn_col2:
        if st.button("🚀 Tailor My Resume"):
            if not api_key or not st.session_state.profiles[active_profile] or not jd:
                st.error("Missing API Key, Resume, or JD!")
            else:
                with st.spinner("AI is crafting your resume..."):
                    try:
                        result = tailor_resume(st.session_state.profiles[active_profile], comp, jd, api_key)
                        st.session_state.final_text = result
                        st.success("Tailoring Complete!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # DISPLAY ANALYSIS RESULTS
    if 'analysis' in st.session_state:
        st.subheader("📊 ATS Analysis")
        res = st.session_state.analysis
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f"<div class='metric-card'><h3>Match Score</h3><h2>{res['match_score']}%</h2></div>", unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"<div class='metric-card'><h3>Missing Keywords</h3><p>{', '.join(res['missing_keywords'])}</p></div>", unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"<div class='metric-card'><h3>Quick Tip</h3><p>{res['improvement_tips'][0]}</p></div>", unsafe_allow_html=True)

    # DISPLAY FINAL RESUME
    if 'final_text' in st.session_state:
        st.divider()
        st.subheader("✨ Your Tailored Resume")
        st.text_area("Preview (You can edit this before exporting)", st.session_state.final_text, height=400)
        
        fmt = st.radio("Export Format:", ["PDF", "Text"], horizontal=True)
        if fmt == "PDF":
            pdf_b = create_pdf(st.session_state.final_text)
            st.download_button("📥 Download PDF", data=pdf_b, file_name=f"Tailored_Resume_{comp}.pdf", mime="application/pdf")
        else:
            st.download_button("📥 Download Text", data=st.session_state.final_text, file_name=f"Tailored_Resume_{comp}.txt", mime="text/plain")
else:
    st.info("👈 Please create or select a profile from the sidebar to begin.")
