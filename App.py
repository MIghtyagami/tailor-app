import streamlit as st
from PyPDF2 import PdfReader
from fpdf import FPDF
import openai

# ==========================================
# 1. WEB APP CONFIG & THEMING
# ==========================================
st.set_page_config(page_title="OceanTailor AI", layout="wide", page_icon="🌊")

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
    pdf.multi_cell(0, 10, txt=text)
    return pdf.output(dest='S').encode('latin-1', errors='ignore')

def tailor_resume(base_text, company, jd, api_key):
    openai.api_key = api_key
    prompt = f"Company: {company}\nJob Description: {jd}\nBase Resume: {base_text}\n\nRewrite this resume to align with the JD. Keep contact/edu, optimize experience/skills. Return ONLY the final resume text."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are an expert ATS resume writer."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ==========================================
# 3. PROFILE MANAGEMENT (Web Session)
# ==========================================
if 'profiles' not in st.session_state:
    st.session_state.profiles = {}

# ==========================================
# 4. UI LAYOUT
# ==========================================
st.title("🌊 OceanTailor: AI Resume Pro")

with st.sidebar:
    st.header("👤 User Profiles")
    new_p = st.text_input("Profile Name (e.g. Web Dev)")
    if st.button("➕ Create Profile"):
        if new_p:
            st.session_state.profiles[new_p] = ""
            st.success("Profile Created!")

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

    if 'final_text' in st.session_state:
        st.divider()
        st.subheader("✨ Your Tailored Resume")
        st.text_area("Preview", st.session_state.final_text, height=300)
        
        fmt = st.radio("Export Format:", ["PDF", "Text"])
        if fmt == "PDF":
            pdf_b = create_pdf(st.session_state.final_text)
            st.download_button("📥 Download PDF", data=pdf_b, file_name=f"Resume_{comp}.pdf", mime="application/pdf")
        else:
            st.download_button("📥 Download Text", data=st.session_state.final_text, file_name=f"Resume_{comp}.txt", mime="text/plain")
else:
    st.info("👈 Please create or select a profile from the sidebar to begin.")