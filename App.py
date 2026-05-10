import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from docx.shared import Pt
import google.generativeai as genai
import json
import io

# ==========================================
# 1. WEB APP CONFIG & DARK AESTHETIC CSS
# ==========================================
st.set_page_config(page_title="OceanTailor AI v2.2", layout="wide", page_icon="🌊")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f1f5f9; }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    .main-container { animation: fadeInUp 0.8s ease-out; }
    h1, h2, h3 { color: #22d3ee !important; font-family: 'Inter', sans-serif; font-weight: 700 !important; }
    .profile-card { 
        padding: 25px; background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px);
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 6px solid #22d3ee; margin-bottom: 25px; 
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.03); padding: 20px; border-radius: 15px;
        border: 1px solid rgba(34, 211, 238, 0.2); text-align: center; transition: all 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-5px); border: 1px solid #22d3ee; box-shadow: 0px 10px 20px rgba(34, 211, 238, 0.1); }
    .stButton>button { 
        background: linear-gradient(90deg, #0891b2 0%, #22d3ee 100%); color: #0f172a !important; 
        border-radius: 12px; border: none; font-weight: bold; width: 100%; transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0px 0px 15px rgba(34, 211, 238, 0.6); }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
        background-color: rgba(15, 23, 42, 0.6) !important; color: #f1f5f9 !important;
        border: 1px solid rgba(34, 211, 238, 0.3) !important; border-radius: 12px !important; 
    }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    </style>
    <div class="main-container"></div>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIC FUNCTIONS (GEMINI VERSION)
# ==========================================
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "".join([page.extract_text() for page in reader.pages])

def create_docx(text):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)
    doc.add_paragraph(text)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def analyze_resume(base_text, jd, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Analyze this Resume against this JD. Return ONLY a JSON object: {{'match_score': int, 'missing_keywords': [], 'improvement_tips': []}}. JD: {jd} Resume: {base_text}"
    response = model.generate_content(prompt)
    # Clean JSON response from Gemini (removes ```json blocks)
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)

def tailor_resume(base_text, company, jd, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    You are an expert ATS resume writer.
    Company: {company}
    JD: {jd}
    Base Resume: {base_text}
    
    TASK: Rewrite the resume to be highly optimized for this JD.
    CRITICAL: Maintain the EXACT same sections and structure as the base resume. 
    Do not add new sections. Only rewrite the bullet points using the Google XYZ formula 
    (Accomplished X as measured by Y, by doing Z) and integrate keywords from the JD.
    Return ONLY the final resume text.
    """
    response = model.generate_content(prompt)
    return response.text

# ==========================================
# 3. PROFILE MANAGEMENT
# ==========================================
if 'profiles' not in st.session_state:
    st.session_state.profiles = {}

# ==========================================
# 4. UI LAYOUT
# ==========================================
st.title("🌊 OceanTailor AI v2.2")
st.markdown("#### *Midnight Free Edition: Powered by Google Gemini*")

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
    
    api_key = st.text_input("🔑 Enter Google Gemini API Key", type="password")
    st.caption("Get a free key at: aistudio.google.com")
    
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
                    try:
                        st.session_state.analysis = analyze_resume(st.session_state.profiles[active_profile], jd, api_key)
                    except Exception as e:
                        st.error(f"Error: {e}")

    with btn_col2:
        if st.button("🚀 Tailor My Resume"):
            if not api_key or not st.session_state.profiles[active_profile] or not jd:
                st.error("Missing API Key, Resume, or JD!")
            else:
                with st.spinner("Crafting..."):
                    try:
                        st.session_state.final_text = tailor_resume(st.session_state.profiles[active_profile], comp, jd, api_key)
                    except Exception as e:
                        st.error(f"Error: {e}")

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
        st.subheader("✨ Your Tailored Resume Content")
        st.info("💡 **Pro Tip:** Copy the text below and paste it into your original resume template to keep your exact design!")
        st.text_area("Preview", st.session_state.final_text, height=400)
        
        # Word Export
        docx_b = create_docx(st.session_state.final_text)
        st.download_button("📥 Download as Word (.docx)", data=docx_b, file_name=f"Tailored_{comp}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
else:
    st.info("👈 Please create or select a profile from the sidebar to begin.")
