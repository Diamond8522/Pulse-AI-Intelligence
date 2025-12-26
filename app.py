def create_pdf(topic, summary, df):
    """Generates a downloadable PDF report with character cleaning."""
    pdf = FPDF()
    pdf.add_page()
    
    # Helper to clean text for Latin-1 compatibility
    def clean_text(text):
        if not text: return ""
        # Replaces complex characters with simple equivalents or removes them
        return text.encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=clean_text(f"ShadowPulse Intelligence: {topic.upper()}"), ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Executive AI Summary:", ln=True)
    
    pdf.set_font("Arial", size=11)
    # Cleaning the summary before writing
    pdf.multi_cell(0, 8, txt=clean_text(summary))
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Top Headlines Analyzed:", ln=True)
    
    pdf.set_font("Arial", size=10)
    for _, row in df.head(8).iterrows():
        # Cleaning headlines too
        headline = clean_text(f"- {row['title']} (Source: {row['source']})")
        pdf.multi_cell(0, 7, txt=headline)
        
    return pdf.output(dest='S').encode('latin-1')
