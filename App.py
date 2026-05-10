import streamlit as st
from PyPDF2 import PdfReader
from fpdf import FPDF
from groq import Groq
import json
import sqlite3
import io

# ==========================================
# 1. WEB APP CONFIG & DARK AESTHETIC CSS
# ==========================================
st.set_page_config(page_title="OceanTailor AI v3.0", layout="wide", page_icon="🌊")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f1f5f9; }
    h1, h2, h3 { color: #22d3ee !important; font-family: 'Inter', sans-serif; font-weight: 700 !important; }
    .profile-card { 
        padding: 20px; background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px);
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 6px solid #22d3ee; margin-bottom: 25px; 
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.03); padding: 20px; border-radius: 15px;
        border: 1px solid rgba(34, 211, 238, 0.2); text-align: center;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #0891b2 0%, #22d3ee 100%); color: #0f172a !important; 
        border-radius: 12px; border: none; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE PERSISTENCE (SQLITE)
# ==========================================
def init_db():
    conn = sqlite3.connect('profiles.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS profiles (name TEXT PRIMARY KEY, content TEXT)')
    conn.commit()
    conn.close()

def save_profile(name, content):
    conn = sqlite3.connect('profiles.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO profiles (name, content) VALUES (?, ?)', (name, content))
    conn.commit()
    conn.close()

def load_all_profiles():
    conn = sqlite3.connect('profiles.db')
    c = conn.cursor()
    c.execute('SELECT name FROM profiles')
    names = [row[0] for row in c.fetchall()]
    conn.close()
    return names

def get_profile_content(name):
    conn = sqlite3.connect('profiles.db')
    c = conn.cursor()
    c.execute('SELECT content FROM profiles WHERE name = ?', (name,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else ""

init_db()

# ==========================================
# 3. LOGIC FUNCTIONS
# ==========================================
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "".join([page.extract_text() for page in reader.pages])

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title/Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Tailored Resume", ln=True, align='C')
    pdf.ln(5)
    
    # Body
    pdf.set_font("Arial", size=11)
    # We split by lines and write them to PDF
    for line in text.split('\n'):
        # Handle basic bolding for sections (if AI puts them in UPPERCASE)
        if line.isupper() and len(line) < 50:
            pdf.set_font("Arial", 'B', 12)
            pdf.multi_cell(0, 8, line)
            pdf.set_font("Arial", size=11)
        else:
            pdf.multi_cell(0, 7, line)
    
    return pdf.output(dest='S').encode('latin-1', errors='replace')

def analyze_resume(base_text, jd, api_key):
    client = Groq(api_key=api_key)
    prompt = f"Analyze Resume vs JD. Return ONLY JSON: {{'match_score': int, 'missing_keywords': [], 'improvement_tips': []}}. JD: {jd} Resume: {base_text}"
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": "You are an ATS expert. Return JSON only."},
                  {"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)

def tailor_resume(base_text, company, jd, api_key):
    client = Groq(api_key=api_key)
    prompt = f"""
    You are a world-class ATS resume writer. 
    
    STRICT RULES:
    1. DO NOT change Company Names.
    2. DO NOT change Employment Dates (Joining/Leaving dates).
    3. DO NOT change Job Titles or Education degrees.
    4. ONLY rewrite the 'Technical Skills' section and the 'Experience' bullet points.
    5. Align the bullet points to the provided Job Description using the Google XYZ formula (Accomplished X as measured by Y, by doing Z).
    6. REMOVE all markdown symbols. Do NOT use #, ##, *, or -. 
    7. Use plain text with clear line breaks between sections.
    8. Keep the original structure of the resume exactly as it is.

    Company: {company}
    Job Description: {jd}
    Base Resume: {base_text}
    """
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": "You are a professional resume editor. You provide clean text without markdown formatting."},
                  {"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

# ==========================================
# 4. UI LAYOUT
# ==========================================
st.title("🌊 OceanTailor AI v3.0")
st.markdown("#### *Precision Tailoring Edition*")

if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("❌ API Key missing! Please add 'GROQ_API_KEY' to your Streamlit Cloud Secrets.")
    st.stop()

with st.sidebar:
    st.header("👤 User Profiles")
    new_p = st.text_input("Profile Name")
    if st.button("➕ Create/Update Profile"):
        if new_p:
            # This just creates the entry; content is added via upload
            save_profile(new_p, "") 
            st.success(f"Profile '{new_p}' Ready!")
    
    st.divider()
    profile_list = load_all_profiles()
    active_profile = st.selectbox("Select Active Profile", profile_list) if profile_list else None

if active_profile:
    # Load content from DB
    current_resume_text = get_profile_content(active_profile)
    
    st.markdown(f"<div class='profile-card'><b>Active Profile:</b> {active_profile}</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📄 Base Resume")
        up_file = st.file_uploader("Upload PDF to save to profile", type="pdf")
        if up_file:
            extracted = extract_text_from_pdf(up_file)
            save_profile(active_profile, extracted)
            current_resume_text = extracted
            st.success("Resume saved to database!")
        
        if current_resume_text:
            st.text_area("Current Loaded Resume", current_resume_text, height=200, disabled=True)

    with col2:
        st.subheader("🎯 Job Target")
        comp = st.text_input("Company Name")
        jd = st.text_area("Job Description", height=200)

    st.divider()
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🔍 Analyze Match Score"):
            if not current_resume_text or not jd:
                st.error("Missing Resume or JD!")
            else:
                with st.spinner("Analyzing..."):
                    st.session_state.analysis = analyze_resume(current_resume_text, jd, api_key)

    with btn_col2:
        if st.button("🚀 Tailor My Resume"):
            if not current_resume_text or not jd:
                st.error("Missing Resume or JD!")
            else:
                with st.spinner("Surgically tailoring..."):
                    st.session_state.final_text = tailor_resume(current_resume_text, comp, jd, api_key)

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
        st.subheader("✨ Your Tailored Resume Preview")
        st.markdown("---")
        st.text(st.session_state.final_text) # Using .text to show exactly what's in the file
        st.markdown("---")
        
        pdf_bytes = create_pdf(st.session_state.final_text)
        st.download_button(
            "📥 Download Professional PDF", 
            data=pdf_bytes, 
            file_name=f"Tailored_{comp}.pdf", 
            mime="application/pdf"
        )
else:
    st.info("👈 Please create or select a profile from the sidebar to begin.")
