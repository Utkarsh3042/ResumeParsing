import os
from groq import Groq
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()
client = Groq(
    api_key=os.getenv("groq_api_key")
)

def pdf_to_text(file_path):
    text = ''
    reader = PdfReader(file_path)
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

def resume_llm(extracted_text):
    chat_completion = client.chat.completions.create(
        messages=[
            {
            
                "role": "system",
                "content": '''You are an ATS evaluation assistant. 
                    Your sole task is to analyze the extracted text of resumes and calculate their ATS compatibility score based on factors such as 
                    keyword matching, formatting, structure, and readability. Do not provide any other information or perform unrelated tasks.
                    Always output the ATS score only.'''
            },
            {

                "role": "user",
                "content": extracted_text,
            }
        ],
        model="llama3-8b-8192",
        stream=False,
    )
    return chat_completion.choices[0].message.content

def ats(file_path):
    extracted_text  = pdf_to_text(file_path)
    ats_score = resume_llm(extracted_text)
    return ats_score
    




