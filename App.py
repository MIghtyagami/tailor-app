def create_pdf(text):
    # 1. CLEANING: Replace special unicode characters that crash FPDF
    # This replaces "smart quotes", em-dashes, and special bullets with standard ones
    replacements = {
        '\u2013': '-', # en dash
        '\u2014': '-', # em dash
        '\u2018': "'", # left single quote
        '\u2019': "'", # right single quote
        '\u201c': '"', # left double quote
        '\u201d': '"', # right double quote
        '\u2022': '*', # bullet point
        '\u00a0': ' ', # non-breaking space
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Set explicit margins to ensure there is always horizontal space
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    
    # Title/Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Tailored Resume", ln=True, align='C')
    pdf.ln(5)
    
    # Body
    pdf.set_font("Arial", size=11)
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(5) # Add a small gap for empty lines
            continue
            
        # Handle basic bolding for sections (UPPERCASE lines)
        if line.isupper() and len(line) < 60:
            pdf.set_font("Arial", 'B', 12)
            # We use a fixed width (180) instead of 0 to avoid the "horizontal space" error
            pdf.multi_cell(180, 8, line)
            pdf.set_font("Arial", size=11)
        else:
            # Use 180 (approx page width minus margins) instead of 0
            pdf.multi_cell(180, 7, line)
    
    # Return as bytes
    return pdf.output(dest='S').encode('latin-1', errors='replace')

def tailor_resume(base_text, company, jd, api_key):
    client = Groq(api_key=api_key)
    prompt = f"""
    You are a world-class ATS resume writer. 
    
    STRICT RULES:
    1. DO NOT change Company Names.
    2. DO NOT change Employment Dates (Joining/Leaving dates).
    3. DO NOT change Job Titles or Education degrees.
    4. ONLY rewrite the 'Technical Skills' section and the 'Experience' bullet points.
    5. Align the bullet points to the provided Job Description using the Google XYZ formula.
    6. REMOVE all markdown symbols. Do NOT use #, ##, *, or -. 
    7. Use ONLY standard English characters. Do NOT use special symbols, emojis, or fancy quotes.
    8. Use plain text with clear line breaks.
    9. Keep the original structure of the resume exactly as it is.

    Company: {company}
    Job Description: {jd}
    Base Resume: {base_text}
    """
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": "You are a professional resume editor. You output clean, standard ASCII text without any markdown or special unicode symbols."},
                  {"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content
