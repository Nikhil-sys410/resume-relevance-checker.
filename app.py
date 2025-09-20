import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

# 🔑 Configure Gemini API
genai.configure(api_key="AIzaSyAiIxiLn1tV9ULV43UkjRLIZ6UsriWzcvY")

st.title("📄 AI Resume Relevance Checker")
st.write("Upload your resume and paste a job description. The AI will check the match!")

# Upload Resume
resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_description = st.text_area("Paste Job Description Here", height=200)

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function: Keyword-based matching
def keyword_match_score(resume_text, job_text):
    resume_lower = resume_text.lower()
    jd_lower = job_text.lower()

    # Split into words (remove duplicates)
    jd_words = set(jd_lower.split())
    resume_words = set(resume_lower.split())

    # Find overlap
    matched = jd_words.intersection(resume_words)
    score = (len(matched) / len(jd_words)) * 100 if len(jd_words) > 0 else 0

    return round(score, 2), list(matched), list(jd_words - matched)

if st.button("Check Relevance"):
    if resume_file and job_description.strip():
        # Extract Resume Text
        resume_text = extract_text_from_pdf(resume_file)

        # Hard check with keywords
        score, matched, missing = keyword_match_score(resume_text, job_description)

        # Force rules: If score < 20% → treat as "Not Relevant"
        if score < 20:
            st.markdown("### ❌ Results")
            st.write(f"**Match Percentage:** {score}%")
            st.write("This resume does not match the job description.")
            st.write("**Missing Skills:**", ", ".join(missing))
        else:
            # Otherwise, let Gemini polish the explanation
            prompt = f"""
            Compare this resume with the job description.
            Resume: {resume_text}
            Job Description: {job_description}

            Use the keyword match score = {score}% as base.
            Give output in Markdown with:
            - Match Percentage
            - Strengths (skills from resume that match JD)
            - Missing Skills
            - Short Suggestion to improve resume
            """

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            st.markdown("### ✅ Results")
            st.markdown(response.text)

    else:
        st.warning("⚠️ Please upload a resume and paste job description.")