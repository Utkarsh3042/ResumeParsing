import streamlit as st
from PyPDF2 import PdfReader
import re
import pickle
import os, base64, time
from education import extract_education_from_resume
from skills import extract_skills_from_resume
from streamlit_tags import st_tags

# Load models
rf_classifier_categorization = pickle.load(open('Models/rf_classifier_categorization.pkl', 'rb'))
tfidf_vectorizer_categorization = pickle.load(open('Models/tfidf_vectorizer_categorization.pkl', 'rb'))
rf_classifier_job_recommendation = pickle.load(open('Models/rf_classifier_job_recommendation.pkl', 'rb'))
tfidf_vectorizer_job_recommendation = pickle.load(open('Models/tfidf_vectorizer_job_recommendation.pkl', 'rb'))

# Clean resume
def cleanResume(txt):
    cleanText = re.sub(r'http\S+\s', ' ', txt)
    cleanText = re.sub(r'RT|cc', ' ', cleanText)
    cleanText = re.sub(r'#\S+\s', ' ', cleanText)
    cleanText = re.sub(r'@\S+', ' ', cleanText)
    cleanText = re.sub(r'[!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]', ' ', cleanText)
    cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText)
    cleanText = re.sub(r'\s+', ' ', cleanText)
    return cleanText

# Prediction and categorization
def predict_category(resume_text):
    resume_text = cleanResume(resume_text)
    resume_tfidf = tfidf_vectorizer_categorization.transform([resume_text])
    predicted_category = rf_classifier_categorization.predict(resume_tfidf)[0]
    return predicted_category

def job_recommendation(resume_text):
    resume_text = cleanResume(resume_text)
    resume_tfidf = tfidf_vectorizer_job_recommendation.transform([resume_text])
    recommended_job = rf_classifier_job_recommendation.predict(resume_tfidf)[0]
    return recommended_job

# PDF to text conversion
def pdf_to_text(file):
    reader = PdfReader(file)
    text = ''
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

# Resume parsing functions
def extract_contact_number_from_resume(text):
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    return match.group() if match else None

def extract_email_from_resume(text):
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    return match.group() if match else None

def extract_name_from_resume(text):
    pattern = r"(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)"
    match = re.search(pattern, text)
    return match.group() if match else None


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def run():
# Main Streamlit app
    st.sidebar.markdown("# Choose User")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    if choice == 'User':
        st.title("Resume Parser")
        uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
        if uploaded_file is not None:
            with st.spinner('Uploading your Resume...'):
                time.sleep(4)
            save_image_path = './Uploaded_Resumes/'+uploaded_file.name
            with open(save_image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            show_pdf(save_image_path)
            if uploaded_file:
                if uploaded_file.type == "application/pdf":
                    resume_text = pdf_to_text(uploaded_file)
                elif uploaded_file.type == "text/plain":
                    resume_text = uploaded_file.read().decode("utf-8")

            # Process the uploaded file
                predicted_category = predict_category(resume_text)
                recommended_job = job_recommendation(resume_text)
                phone = extract_contact_number_from_resume(resume_text)
                email = extract_email_from_resume(resume_text)
                name = extract_name_from_resume(resume_text)
                extracted_skills = extract_skills_from_resume(resume_text)
                print("Skills",extracted_skills)
                print(type(extracted_skills))
                extracted_education = extract_education_from_resume(resume_text)
                print("Edu:",extracted_education)
                

            # Display results
                st.divider()
                st.subheader("Extracted Information")
                st.write(f"**Name:** {name}")
                st.write(f"**Email:** {email}")
                st.write(f"**Phone Number:** {phone}")
                st.write(f"**Predicted Category:** {predicted_category}")
                #st.write(f"**Extracted Education:** {extracted_education}")
                #st.write(f"**Extracted Skills:**")
                keywords=st_tags(label="**Extracted Skills:**",text="", value=extracted_skills,suggestions=[])
                st.write(f"**Recommended Job:** {recommended_job}")

run()