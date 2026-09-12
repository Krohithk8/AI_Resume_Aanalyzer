"""Streamlit interface for the AI Resume Analyzer."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from resume_analyzer import analyze_resume, read_text_file

load_dotenv()
st.set_page_config(page_title="AI Resume Analyzer", page_icon="✦", layout="wide")

st.markdown("""
<style>
  .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #17151d !important; }
  header[data-testid="stHeader"], [data-testid="stBottom"], [data-testid="stBottomBlockContainer"] { background: #17151d !important; }
  [data-testid="stSidebar"] { background: #201d29 !important; border-right: 1px solid #393246; }
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #f7f2ff !important; }
  [data-testid="stSidebar"] p { color: #cfc3dc !important; }
  .block-container { max-width: 1120px; padding-top: 2.4rem; padding-bottom: 3rem; }
  .hero-title { color: #f7f2ff !important; font-size: clamp(2.2rem, 5vw, 4rem); letter-spacing: -.05em; margin: 0; }
  .hero-copy { color: #c8bed7 !important; font-size: 1.1rem; max-width: 44rem; margin: .85rem 0 2rem; }
  .info-card { background: linear-gradient(135deg, #2a2440, #242039); border: 1px solid #5d4b82; border-radius: 16px; padding: 1.2rem 1.4rem; color: #ebe3f7; margin: .5rem 0 1.2rem; box-shadow: 0 14px 30px rgba(0, 0, 0, .2); }
  .info-card strong { color: #c4b5fd; display: block; margin-bottom: .25rem; }
  [data-testid="stFileUploader"] { background: #292535 !important; border: 1px dashed #78669c; border-radius: 12px; padding: .5rem; }
  [data-testid="stFileUploader"] section { background: #292535 !important; border-color: #78669c !important; }
  [data-testid="stFileUploader"] * { color: #f2ecfa !important; }
  [data-testid="stFileUploader"] button, [data-testid="stFileUploader"] button * { background: #f7f2ff !important; color: #211b2b !important; }
  .stButton > button { background: #7c3aed !important; border-color: #a78bfa !important; color: #fff !important; border-radius: 9px; font-weight: 650; min-height: 2.65rem; box-shadow: 0 8px 18px rgba(124, 58, 237, .25); }
  .stButton > button * { color: #fff !important; }
  [data-testid="stTextArea"] textarea { background: #292535 !important; color: #f7f2ff !important; border-color: #67547e !important; border-radius: 10px; }
  [data-testid="stTextArea"] textarea::placeholder { color: #c5b9d2 !important; }
  [data-testid="stExpander"] { background: #24202d; border-color: #51435e; border-radius: 10px; }
</style>
<h1 class="hero-title">AI Resume Analyzer</h1>
<p class="hero-copy">Compare a resume with a job description, identify ATS gaps, and get fact-preserving bullet-point improvements.</p>
""", unsafe_allow_html=True)


def extract_upload(uploaded_file: st.runtime.uploaded_file_manager.UploadedFile) -> str:
    """Extract text from the supported uploaded file types."""
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".txt":
        return uploaded_file.getvalue().decode("utf-8", errors="replace").strip()
    if suffix == ".pdf":
        import fitz
        with fitz.open(stream=uploaded_file.getvalue(), filetype="pdf") as pdf:
            return "\n".join(page.get_text() for page in pdf).strip()
    if suffix == ".docx":
        from docx import Document
        with tempfile.NamedTemporaryFile(suffix=".docx") as temp_file:
            temp_file.write(uploaded_file.getvalue()); temp_file.flush()
            return "\n".join(p.text for p in Document(temp_file.name).paragraphs).strip()
    raise ValueError("Use a TXT, PDF, or DOCX file.")


with st.sidebar:
    st.header("✦ Upload documents")
    st.caption("Your files are sent to Claude only when you click Analyze.")
    resume_file = st.file_uploader("Resume", type=["txt", "pdf", "docx"])
    job_file = st.file_uploader("Job description (optional)", type=["txt", "pdf", "docx"])

if not os.getenv("ANTHROPIC_API_KEY"):
    st.warning("Add your Anthropic API key to `.env` before running an analysis.")

if not resume_file:
    st.markdown("""
    <div class="info-card">
      <strong>Start with your resume</strong>
      Upload a TXT, PDF, or DOCX resume in the sidebar. Add a job description to receive a role-specific match score and ATS keyword analysis.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<div class='info-card'><strong>Ready to analyze</strong>Your resume is selected. Add an optional job description, then run the analysis.</div>", unsafe_allow_html=True)

if st.button("Analyze resume", type="primary", disabled=not resume_file):
    try:
        resume_text = extract_upload(resume_file)
        job_text = extract_upload(job_file) if job_file else None
        if not resume_text:
            raise ValueError("No readable text was found in the resume.")
        with st.spinner("Reviewing the resume against the role…"):
            report = analyze_resume(resume_text, job_text, os.environ["ANTHROPIC_API_KEY"])
        score = report["match_score"]
        left, right = st.columns([1, 3])
        left.metric("Match score", f"{score}/100")
        right.subheader("Recruiter summary")
        right.write(report["summary"])
        first, second = st.columns(2)
        with first:
            st.subheader("Strengths")
            for item in report["strengths"] or ["No specific strengths identified."]:
                st.write(f"• {item}")
            st.subheader("Missing ATS keywords")
            for item in report["missing_keywords"] or ["None identified."]:
                st.write(f"• {item}")
        with second:
            st.subheader("Gaps to address")
            for item in report["gaps"] or ["No major gaps identified."]:
                st.write(f"• {item}")
            st.subheader("Red flags")
            for item in report["red_flags"] or ["None identified."]:
                st.write(f"• {item}")
        with st.expander("Suggested bullet rewrites"):
            for rewrite in report["bullet_rewrites"] or []:
                st.markdown(f"**Original:** {rewrite['original']}")
                st.markdown(f"**Improved:** {rewrite['improved']}")
    except Exception as error:
        st.error(f"Could not analyze the resume: {error}")
