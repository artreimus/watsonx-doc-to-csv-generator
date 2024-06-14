# Document to CSV Generator

**Document to CSV Generator** is a robust application designed to facilitate the efficient transformation of document content into structured CSV files. This tool allows users to easily upload multiple documents and define specific headers for the CSV columns directly within the application. Each header can be accompanied by a detailed column description to clarify the data extraction process.

## Technology Highlights

- **Streamlit Framework**: Built on Streamlit to provide a smooth and interactive user experience, facilitating quick setup and real-time data processing.
- **Watsonx AI and Llama 3 by Meta**: Integrates Watsonx AI with Llama 3, Meta’s latest large language model, ensuring top-notch accuracy and efficiency in text analysis and data extraction.

## Key Functionalities

- **Column Customization**: Users can define column names and provide detailed descriptions for each, enhancing understanding and control over data extraction.
- **Multiple Document Upload**: The app supports uploading several documents simultaneously, allowing for bulk data processing.
- **Intelligent Data Extraction**: Leveraging advanced algorithms, the application extracts relevant data from the uploaded documents and aligns it under the designated headers in the CSV.

**Document to CSV Generator** streamlines data extraction and organization, making it an indispensable tool for data analysis and management tasks.

## Table of Contents

- [Installation](#installation)
- [Setting Up the Python Environment](#setting-up-the-python-environment)
- [Activating the Python Environment](#activating-the-python-environment)
- [Running the Streamlit App](#running-the-streamlit-app)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)


![image](https://github.com/artreimus/watsonx-doc-to-csv-generator/assets/63195930/a25aad08-c074-4e5b-a3e3-fdcaf35bc9a8)
![image](https://github.com/artreimus/watsonx-doc-to-csv-generator/assets/63195930/8920ba23-f1a2-41a4-aa25-80712e17f9dd)
![image](https://github.com/artreimus/watsonx-doc-to-csv-generator/assets/63195930/0a4bb336-9a1d-496d-b305-7edf7d4eaec3)
![image](https://github.com/artreimus/watsonx-doc-to-csv-generator/assets/63195930/aca9cd5b-53d8-4629-9a27-4d894f49af8f)


## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- virtualenv (for creating isolated Python environments)

### Steps

1. **Clone the repository:**

   ```sh
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Install virtualenv if you don't have it:**
   ```sh
   pip install virtualenv
   ```

## Setting Up the Python Environment

1. **Create a virtual environment:**

   ```sh
   virtualenv venv
   ```

2. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## Activating the Python Environment

### On Windows

    ```sh
    .\venv\Scripts\activate
    ```

### On macOS and Linux

    ```sh
    source venv/bin/activate
    ```

## Running the Streamlit App

1. **Make sure your virtual environment is activated:**

   ```sh
   source venv/bin/activate # On macOS and Linux
   .\venv\Scripts\activate # On Windows
   ```

2. **Run the Streamlit app:**
   ```sh
   streamlit run watsonx-app.py
   ```
