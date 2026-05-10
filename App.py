import streamlit as st
from PyPDF2 import PdfReader
from fpdf import FPDF
from openai import OpenAI
import json

# ==========================================
# 1. WEB APP CONFIG & DARK AESTHETIC CSS
# ==========================================
st.set_page_config(page_title="OceanTailor AI v2.1", layout="wide", page_icon="🌊")

st.markdown("""
    <style>
    /* Main Background */
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
        color: #f1f5f9;
    }

    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .main-container {
        animation: fadeInUp 0.8s ease-out;
    }

    /* Headers */
    h1, h2, h3 { 
        color: #22d3ee !important; 
        font-family: 'Inter', sans-serif; 
        font-weight: 700 !important;
        text-shadow: 0px 0px 10px rgba(34, 211, 238, 0.3);
    }

    /* Custom Glassmorphism Cards */
    .profile-card { 
        padding: 25px; 
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(10px);
        border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 6px solid #22d3ee; 
        margin-bottom: 25px; 
        animation: fadeInUp 1s ease-out;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.03); 
        padding: 20px; 
        border-radius: 15px;
        border: 1px solid rgba(34, 211, 238, 0.2); 
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 10px 20px rgba(34, 211, 238, 0.1);
        border: 1px solid #22d3ee;
    }

    /* Buttons */
    .stButton>button { 
        background: linear-gradient(90deg, #0891b2 0%, #22d3ee 100%); 
        color: #0f172a !important; 
        border-radius: 12px; 
        border: none; 
        font-weight: bold; 
        width: 100%; 
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover { 
        transform: scale(1.02);
        box-shadow: 0px 0px 15px rgba(34, 211, 238, 0.6);
        color: #0f172a !important;
    }

    /* Input Fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
        background-color: rgba(15, 23, 42, 0.6) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(34, 211, 238, 0.3) !important; 
        border-radius: 12px !important; 
    }
    .stTextInput>div>div>input:focus {
        border-color: #22d3ee !important;
        box-shadow: 0 0 0 2px rgba(34, 211, 238, 0.2) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(34, 211, 238, 0.1);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    <div class="main-container"></div>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIC FUNCTIONS (Same as v2.0)
# ==========================================
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "".join([page.extract_text() for page in reader.pages])

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

def analyze_resume(base_text, jd, api_key):
    client = OpenAI(api_key=api_key)
    prompt = f"Analyze Resume against JD. Return ONLY JSON: {{'match_score': int, 'missing_keywords': [], 'improvement_tips': []}}. JD: {jd} Resume: {base_text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "system", "content": "You are an ATS expert. Return JSON only."},
                  {"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

def tailor_resume(base_text, company, jd, api_key):
    client = OpenAI(api_key=api_key)
    prompt = f"Company: {company}\nJD: {jd}\nResume: {base_text}\n\nRewrite experience using Google XYZ formula. Return ONLY the final resume text."
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
st.title("🌊 OceanTailor AI v2.1")
st.markdown("#### *Midnight Edition: Professional ATS Engine*")

with st.sidebar:
    st.header("👤 User Profiles")
    new_p = st.text_input("Profile Name")
    if st.button("➕ Create Profile"):
        if new_p:
            st.session_state.profiles[new_p] = ""
            st.success(f"Profile '{new_p}' Created!")

    st.divider()
    profile_list = list(st.session_state.profiles.keys())
    active_profile = st.selectbox("Select Active Profile", profile_list) if profile_list else None

if active_profile:
    st.markdown(f"<div class='profile-card'><b>Active Profile:</b> {active_profile}</div>", unsafe_allow_html=True)
    
    api_key = st.text_input("🔑 OpenAI API Key", type="password")
    
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
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🔍 Analyze Match Score"):
            if not api_key or not st.session_state.profiles[active_profile] or not jd:
                st.error("Missing API Key, Resume, or JD!")
            else:
                with st.spinner("Analyzing..."):
                    st.session_state.analysis = analyze_resume(st.session_state.profiles[active_profile], jd, api_key)

    with btn_col2:
        if st.button("🚀 Tailor My Resume"):
            if not api_key or not st.session_state.profiles[active_profile] or not jd:
                st.error("Missing API Key, Resume, or JD!")
            else:
                with st.spinner("Crafting..."):
                    st.session_state.final_text = tailor_resume(st.session_state.profiles[active_profile], comp, jd, api_key)

    if 'analysis' in st.session_state:
        st.subheader("📊 ATS Analysis")
        res = st.session_state.analysis
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f"<div class='metric-card'><h3>Match Score</h3><h2 style='color:#22d3ee'>{res['match_score']}%</h2></div>", unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"<div class='metric-card'><h3>Missing Keywords</h3><p>{', '.join(res['missing_keywords'])}</p></div>", unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"<div class='metric-card'><h3>Quick Tip</h3><p>{res['improvement_tips'][0]}</p></div>", unsafe_allow_html=True)

    if 'final_text' in st.session_state:
        st.divider()
        st.subheader("✨ Your Tailored Resume")
        st.text_area("Preview", st.session_state.final_text, height=400)
        
        fmt = st.radio("Export Format:", ["PDF", "Text"], horizontal=True)
        if fmt == "PDF":
            pdf_b = create_pdf(st.session_state.final_text)
            st.download_button("📥 Download PDF", data=pdf_b, file_name=f"Tailored_{comp}.pdf", mime="application/pdf")
        else:
            st.download_button("📥 Download Text", data=st.session_state.final_text, file_name=f"Tailored_{comp}.txt", mime="text/plain")
else:
    st.info("👈 Please create or select a profile from the sidebar to begin.")
