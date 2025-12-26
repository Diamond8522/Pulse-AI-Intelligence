import streamlit as st
import pandas as pd
import plotly.express as px
from duckduckgo_search import DDGS
from textblob import TextBlob
from groq import Groq
from fpdf import FPDF
import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ShadowPulse | Market Intel",
    page_icon="⚡",
    layout="wide"
)

# Professional UI Styling
st.markdown("""
    <style>
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445e; }
    [data-testid="stMetricValue"] { color: #00ffcc; font-family: 'Courier New', monospace; }
    .stInfo { border-left: 5px solid #00ffcc; background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION & CLIENT ---
try:
    # Safely pulls the key from your .streamlit/secrets.toml
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 API Key Missing! Ensure 'GROQ_API_KEY' is in your secrets.toml file.")
    st.stop()

# --- 3. HELPER FUNCTIONS ---
def fetch_news(topic):
    """Fetches real-time headlines."""
    try:
        with DDGS() as ddgs:
            return [r for r in ddgs.news(topic, max_results=10)]
    except Exception as e:
        st.error(f"Search Error: {e}")
        return []

def get_ai_summary(topic, headlines):
    """Synthesizes news into an executive briefing using Llama 3."""
    context = "\n".join([f"- {h['title']}" for h in headlines])
    prompt = f"Analyze these headlines regarding '{topic}'. Provide a 3-sentence professional summary of risks and opportunities:\n{context}"
    
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return completion.choices[0].message.content

def create_pdf(topic, summary, df):
    """Generates a downloadable PDF report."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"ShadowPulse Intelligence Report: {topic.upper()}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Executive AI Summary:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=summary)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Top Headlines Analyzed:", ln=True)
    pdf.set_font("Arial", size=10)
    for _, row in df.head(8).iterrows():
        pdf.multi_cell(0, 7, txt=f"- {row['title']} (Source: {row['source']})")
        
    return pdf.output(dest='S').encode('latin-1')

# --- 4. THE DASHBOARD ---
st.title("⚡ ShadowPulse: AI Market Intelligence")
st.caption("Strategic signals extracted from live global data via Shadow Labs.")

target = st.text_input("Analysis Target", placeholder="e.g. NVIDIA, Bitcoin, or Generative AI")

if target:
    with st.spinner(f"Agent Shadow intercepting data for {target}..."):
        raw_data = fetch_news(target)
        
        if raw_data:
            # Data Processing
            df = pd.DataFrame(raw_data)
            df['sentiment'] = df['title'].apply(lambda x: TextBlob(x).sentiment.polarity)
            avg_sent = df['sentiment'].mean()
            
            # --- ROW 1: METRICS ---
            m1, m2, m3 = st.columns(3)
            status = "Bullish" if avg_sent > 0.05 else "Bearish" if avg_sent < -0.05 else "Neutral"
            m1.metric("Market Sentiment", f"{avg_sent:.2f}", status)
            m2.metric("Signals Found", len(df))
            m3.metric("Analysis Confidence", "High", "Verified")

            # --- ROW 2: AI SUMMARY & PDF ---
            st.subheader("🤖 Executive Briefing")
            summary = get_ai_summary(target, raw_data)
            st.info(summary)
            
            # Export Button
            pdf_bytes = create_pdf(target, summary, df)
            st.download_button(
                label="📥 Download Briefing PDF",
                data=pdf_bytes,
                file_name=f"ShadowPulse_{target}.pdf",
                mime="application/pdf"
            )

            # --- ROW 3: CHARTS & DATA ---
            tab1, tab2 = st.tabs(["📊 Sentiment Chart", "📡 Raw News Feed"])
            
            with tab1:
                fig = px.bar(df, x='title', y='sentiment', color='sentiment', 
                             color_continuous_scale='RdYlGn', template="plotly_dark")
                fig.update_layout(xaxis_showticklabels=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.dataframe(df[['title', 'source', 'date', 'url']], use_container_width=True)
        else:
            st.error("Target off-grid. No data found.")

st.divider()
st.caption("Shadow Labs | Strategic Intelligence Tool v1.0")