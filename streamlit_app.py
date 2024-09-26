import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure the API key for the Generative AI model
genai.configure(api_key=os.getenv("AIzaSyD-gKInDbKdlsrb4fLCQQ2aPPkFTTJQj5U"))  # Replace with your API key

# Function to get AI response based on the resume and job description
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

# Function to extract text from the uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt template for Generative AI model
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of the tech field, software engineering, data science, data analytics,
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider that the job market is very competitive, and you should provide 
the best assistance for improving the resumes. Assign the percentage matching based 
on JD and the missing keywords with high accuracy.
Resume: {text}
Description: {jd}

I want the response in one single string having the structure:
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

# --- Add Custom CSS for Professional Styling and Hover Effects with Angular Cuts ---
st.markdown("""
    <style>
    /* Overall body and app container */
    body {
        background-color: #EFF5F5; /* Soft teal background for the entire app */
    }
    .stApp {
        background-color: #FFFFFF; /* White content background */
        padding: 20px;
        border-radius: 20px;
    }

    /* Title styling */
    h1 {
        color: #0D3B66; /* Deep blue title */
        font-family: 'Arial', sans-serif;
    }

    /* Card-style container with hover effect and angular cut */
    .css-1lcbmhc {
        background-color: #FFFFFF; /* White background for the cards */
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease-in-out;
        position: relative;
        overflow: hidden;
    }

    /* Hover effect for angular cut and lighting */
    .css-1lcbmhc::after {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 0;
        height: 0;
        border-top: 100px solid #0D3B66; /* Deep blue angular cut */
        border-right: 100px solid transparent;
        transition: all 0.3s ease-in-out;
        opacity: 0.8;
    }

    .css-1lcbmhc:hover::after {
        width: 100%;
        height: 100%;
        border: none;
        background: rgba(13, 59, 102, 0.1); /* Soft blue lighting on hover */
    }

    .css-1lcbmhc:hover {
        box-shadow: 0 6px 15px rgba(13, 59, 102, 0.2); /* Shadow increases on hover */
        transform: scale(1.02); /* Slight scale-up effect */
    }

    /* Styling for Subheaders */
    h3 {
        font-family: 'Arial', sans-serif;
        color: #0D3B66;
    }

    /* Tabs styling */
    .stTabs [role="tablist"] button {
        color: #0D3B66;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }

    .stTabs [role="tablist"] button:hover {
        background-color: #EFF5F5; /* Soft teal background on hover */
    }

    /* Colors for highlighted sections */
    .stTabs [role="tabpanel"] h3 {
        color: #007BFF; /* Soft blue for headings inside tabs */
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit app UI
st.title("Talent Sphere")
st.text("Enhance Your Profiles for Talent Smart Results")

# Option to paste or upload multiple Job Descriptions
st.header("Job Descriptions")
jd_input_option = st.radio("How would you like to provide job descriptions?", ("Paste JDs", "Upload JD File"))
jds = []

if jd_input_option == "Paste JDs":
    # Multiple JD input text boxes
    jd_count = st.number_input("How many job descriptions?", min_value=1, step=1, value=1)
    for i in range(jd_count):
        jd_text = st.text_area(f"Paste Job Description {i + 1}")
        if jd_text:
            jds.append(jd_text)

elif jd_input_option == "Upload JD File":
    jd_file = st.file_uploader("Upload a text file containing Job Descriptions (one per line)", type=["txt"])
    if jd_file:
        jds = jd_file.read().decode("utf-8").splitlines()

# Upload multiple resumes
st.header("Job Application Documents")
uploaded_files = st.file_uploader("Upload Your Job Application Documents", type="pdf", accept_multiple_files=True, help="Please upload PDFs")

submit = st.button("Submit")

if submit:
    if uploaded_files and jds:
        for uploaded_file in uploaded_files:
            st.write(f"Processing resume: {uploaded_file.name}")
            
            # Extract resume text from PDF
            resume_text = input_pdf_text(uploaded_file)
            
            # Iterate through all job descriptions for the current resume
            for idx, jd in enumerate(jds):
                st.subheader(f"Results for {uploaded_file.name} (JD {idx + 1})")

                # Format the prompt for the AI model
                prompt = input_prompt.format(text=resume_text, jd=jd)
                response = get_gemini_response(prompt)

                # Parse the AI response
                try:
                    response_json = json.loads(response)
                except json.JSONDecodeError:
                    st.error("There was an error in processing the response. Please try again.")
                    continue

                jd_match = response_json.get("JD Match", "N/A")
                missing_keywords = response_json.get("MissingKeywords", [])
                profile_summary = response_json.get("Profile Summary", "")

                # Dynamic Tabs for viewing results
                with st.expander(f"Details for JD {idx + 1}", expanded=False):
                    tab1, tab2, tab3 = st.tabs(["JD Match", "Missing Keywords", "Profile Summary"])

                    with tab1:
                        st.markdown(f"<h3 style='color:green;'>JD Match: {jd_match}%</h3>", unsafe_allow_html=True)

                    with tab2:
                        if missing_keywords:
                            st.markdown("<h3 style='color:red;'>Missing Keywords</h3>", unsafe_allow_html=True)
                            st.write(", ".join(missing_keywords))
                        else:
                            st.markdown("<h3 style='color:green;'>No Missing Keywords!</h3>", unsafe_allow_html=True)

                    with tab3:
                        st.markdown("<h3 style='color:blue;'>Profile Summary</h3>", unsafe_allow_html=True)
                        st.write(profile_summary)

    else:
        st.error("Please upload both resumes and job descriptions to proceed.")

