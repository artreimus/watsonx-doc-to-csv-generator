import streamlit as st
import fitz  # PyMuPDF
from docx import Document
import io
from io import StringIO
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes, DecodingMethods
import pandas as pd
import csv
import re
from dotenv import load_dotenv
import os

load_dotenv()

# URL of the hosted LLMs is hardcoded because at this time all LLMs share the same endpoint
url =  os.environ.get('WATSON_URL')
# Replace with your watsonx project id (look up in the project Manage tab)
watsonx_project_id =  os.environ.get('WATSON_PROJECT_ID')
# Replace with your IBM Cloud key
api_key = os.environ.get('WATSON_API_KEY')

model_type = "ibm/granite-13b-chat-v2"
max_tokens = 4000
min_tokens = 1
decoding = DecodingMethods.GREEDY
temperature = 0.1

def get_model(model_type,max_tokens,min_tokens,decoding,temperature):#, repetition_penalty):

    generate_params = {
        GenParams.MAX_NEW_TOKENS: max_tokens,
        GenParams.MIN_NEW_TOKENS: min_tokens,
        GenParams.DECODING_METHOD: decoding,
        GenParams.TEMPERATURE: temperature,
    }

    model = Model(
        model_id=model_type,
        params=generate_params,
        credentials={
            "apikey": api_key,
            "url": url
        },
        project_id=watsonx_project_id
        )

    return model

# Get the watsonx model
model = get_model(model_type, max_tokens, min_tokens, decoding, temperature)

# Display the IBM logo centered
col1, col2, col3 = st.columns([4, 1, 4])
with col1:
    st.write("")
with col2:
    st.image("app/ibm-logo.png", width=100)
with col3:
    st.write("")

# Initialize the application
st.title("RFP Compliance Table Generator")

# Initialize session state variables if they don't exist
if 'input_pairs' not in st.session_state:
    st.session_state['input_pairs'] = []
if 'is_generating' not in st.session_state:
    st.session_state['is_generating'] = False
# Initialize or update session state to store document texts
if 'document_texts' not in st.session_state:
    st.session_state['document_texts'] = []
# Initialize or update session state to store responses
if 'ai_response' not in st.session_state:
    st.session_state['ai_response'] = ""

# Function to add a new input pair
def add_input_pair():
    st.session_state['input_pairs'].append({"column_name": "", "column_description": ""})
    
# Function to remove an input pair
def remove_input_pair(index):
    if index < len(st.session_state['input_pairs']):
        st.session_state['input_pairs'].pop(index)

# Button to add new input pair
if st.button('Add Column Pair'):
    add_input_pair()

# Display all input pairs with a remove button for each
for i, pair in enumerate(st.session_state['input_pairs']):
    col1, col2, col3 = st.columns([3, 3, 1])
    with col1:
        st.session_state['input_pairs'][i]['column_name'] = st.text_input("Column Name", value=pair['column_name'], key=f"name-{i}")
    with col2:
        st.session_state['input_pairs'][i]['column_description'] = st.text_input("Column Description", value=pair['column_description'], key=f"desc-{i}")
    with col3:
        if st.button('Remove', key=f"remove-{i}"):
            remove_input_pair(i)

# File uploader allows multiple files
uploaded_files = st.file_uploader("Upload PDF or DOCX files", type=['pdf', 'docx'], accept_multiple_files=True, disabled=st.session_state['is_generating'])


# Function to extract text from PDF
def extract_text_from_pdf(file_stream):
    text = ""
    with fitz.open(stream=file_stream, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file_stream):
    text = ""
    doc = Document(file_stream)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Store texts from documents
document_texts = []

# Process each uploaded file and store texts in session state
if uploaded_files:
    st.session_state['document_texts'] = []  # Reset or initialize the document_texts list
    for uploaded_file in uploaded_files:
        # Check the file extension and process accordingly
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
            st.session_state['document_texts'].append(text)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(io.BytesIO(uploaded_file.read()))
            st.session_state['document_texts'].append(text)

# Display the extracted text
for i, text in enumerate(st.session_state['document_texts']):
    st.subheader(f"Text from Document {i+1}")
    st.text_area(label=f"Text from file {uploaded_files[i].name}", value=text, height=300, key=f"file-{i}-{uploaded_files[i].name}")
    
def create_prompt(column_data, document_texts):
    # Format the columns for the prompt
    columns_formatted = ", ".join([f"{pair['column_name']} (Description: {pair['column_description']})" for pair in column_data])
    
    # Combine all document texts, adding a divider between documents
    documents_combined = "\n---\n".join(document_texts)  # Using '---' as a divider
    
    prompt = f'''
    Here is the instruction the you will always follow:
    You are now an expert in processing RFP compliance documents related to a specific contract, extracts necessary information, and generates a Compliance Report in CSV format.

    Inputs: A large text or digital document containing all sections of an RFP compliance requirement, and the columns for the CSV file.

    Output Format: Generate a CSV file that exclusively contains the extracted data. Each section of text should be wrapped in double quotes (" ") and separated by commas (,). Ensure that the data is precisely organized under the 
    appropriate columns as specified in the provided column headings. Each entry must correspond to its respective aspect of the RFP compliance requirements. Output strictly the CSV formatted data 
    without any additional text or formatting to ensure the file is ready for direct saving and subsequent use as a CSV file.
    
    Document Analysis: Thoroughly review the RFP document to understand all compliance requirements outlined within. Each requirement should be analyzed to ascertain its specificity and expectations.
    Data Extraction: For each identified SLA requirement in the RFP, extract the paragraph number and the exact text detailing the requirement.
    Compliance Determination: Evaluate the proposal's response to each requirement:
    If the response strictly adheres to the requirements as stated, mark 'Y' for compliance.
    If the response deviates or does not fulfill the requirement, mark 'N' for non-compliance.
    Compilation of Data: Populate the CSV file systematically. Ensure each entry corresponds accurately to the respective requirement from the RFP document.
    Error Checking: Implement validation checks to ensure that no relevant data is omitted and all entries are accurately reflected in the CSV.
    Final Output: Provide the CSV file for download or further review, ensuring it is formatted correctly and contains all necessary data for compliance assessment.

    Additional Considerations:
    You should handle variations in document formats and extract data from both text and tables within the RFP. Ensure that youa are capable of recognizing and adjusting to updates or changes in RFP structures or compliance requirements in future documents.

    ################################

    User: Please help me process the following columns and RFP document

    Columns: {columns_formatted}

    Document: {documents_combined}

    ###############################

    Answer: 
    '''
    return prompt


# st.write("Current Input Pairs:", st.session_state['input_pairs'])

def save_response_as_csv():
    """Saves the AI response as a text file with a .csv extension and provides a download link."""
    if 'ai_response' in st.session_state and st.session_state['ai_response']:
        response_buffer = StringIO()
        csv_writer = csv.writer(response_buffer, quoting=csv.QUOTE_ALL)

        # Split the response into rows where each row is separated by a space outside of quotes
        pattern = r'"\s+"'
        rows = re.split(pattern, st.session_state['ai_response'])
        
        for row in rows:
            # Clean up each row by trimming leading and trailing whitespace and quotes
            row = row.strip()
            if row.startswith('"'):
                row = row[1:]  # Remove starting quote if present
            if row.endswith('"'):
                row = row[:-1]  # Remove ending quote if present
            # Split the row into columns on '","' which are within quotes
            columns = [column.strip() for column in row.split('","')]
            # Write the cleaned and split columns as one row to the CSV
            csv_writer.writerow(columns)

        response_buffer.seek(0)  # Rewind the buffer to the beginning
        st.download_button(label="Download AI Response as CSV",
                           data=response_buffer.getvalue(),
                           file_name='ai_response.csv',
                           mime='text/csv')

def start_generation():
    st.session_state['is_generating'] = True
    try:
        # Assemble the prompt from all document texts
        column_data = st.session_state['input_pairs']
        document_texts = st.session_state.get('document_texts', [])
        prompt = create_prompt(column_data, document_texts)
        
        generated_response = model.generate(prompt)
        response = generated_response['results'][0]['generated_text']
        # response = "Simulated AI Response based on the document text."

        st.session_state['ai_response'] = response  # Store the response in session state
        # st.write(response)
        # save_response_as_csv(response)

    finally: 
        st.session_state['is_generating'] = False

# Generative AI Integration
with st.spinner('Generating response...'):
    if st.button('Generate', disabled=st.session_state['is_generating']):
        start_generation()
        # Prompt engineering would happen here, combining user inputs and document texts
        # Example code commented out as the model would need correct setup and parameters
        # model_response = model.generate(generated_prompt)
        # st.write(model_response)

# This ensures the download button is always visible if there is an AI response
if 'ai_response' in st.session_state and st.session_state['ai_response']:
    save_response_as_csv()
    st.write(st.session_state['ai_response'])