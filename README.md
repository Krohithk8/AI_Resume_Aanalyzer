# AI Resume Analyzer

AI Resume Analyzer is an AI-powered resume analysis application built with **Python, Streamlit, and Anthropic Claude**. It helps job seekers evaluate their resumes against a specific job description and identify areas for improvement.

The application provides a **web-based Streamlit interface** where users can upload their resume in **PDF, DOCX, or TXT format**, optionally provide a job description, and receive an AI-generated analysis.

The project focuses on providing practical feedback while ensuring that suggested improvements remain **fact-based and grounded in the information provided in the resume**.

## Features

- 📄 Upload resumes in **PDF, DOCX, or TXT** format
- 💼 Optionally provide a **job description**
- 🤖 AI-powered resume analysis using **Anthropic Claude**
- 📊 Generate a **role-fit / match score**
- 🔍 Identify **missing ATS keywords**
- ✅ Highlight resume strengths
- ⚠️ Identify gaps relevant to the target role
- ✍️ Generate improved resume bullet points while **preserving the original facts**
- 🌐 User-friendly **Streamlit web interface**
- 🔐 API keys are stored using environment variables and are not included in the source code

## How It Works

1. Upload your resume through the Streamlit application.
2. Optionally enter the job description for the position you are applying for.
3. Click **Analyze Resume**.
4. The application sends the provided information to Anthropic Claude.
5. Claude analyzes the resume and generates:
   - Resume summary
   - Role-fit score
   - Strengths
   - Gaps
   - Missing ATS keywords
   - Fact-preserving bullet-point improvements
6. The results are displayed directly in the Streamlit interface.

> The AI is instructed to use only the information provided in the resume and avoid inventing achievements, skills, or experience.

## Technologies Used

- **Python 3.10+**
- **Streamlit** – Web application interface
- **Anthropic Claude** – AI-powered resume analysis
- **PyPDF** – PDF resume processing
- **python-docx** – DOCX resume processing
- **python-dotenv** – Environment variable management

## Requirements

- Python **3.10 or later**
- Anthropic API key with access to **Claude Sonnet 4.5**

## Installation and Setup

Clone the repository:

```bash
git clone https://github.com/Krohithk8/AI_Resume_Aanalyzer.git
cd AI_Resume_Aanalyzer
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate the virtual environment.

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configure the Anthropic API Key

You can set the API key as an environment variable.

### macOS / Linux

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Alternatively, create a `.env` file from the provided example:

```bash
cp .env.example .env
```

Then add your API key:

```text
ANTHROPIC_API_KEY=your-api-key-here
```

### ⚠️ Security

**Never commit your API key to GitHub.**

Do not place the API key directly inside Python source code, screenshots, or the README. The application reads the key from the `ANTHROPIC_API_KEY` environment variable.

Make sure `.env` is included in `.gitignore`.

## Running the Streamlit Application

Start the application with:

```bash
streamlit run app.py
```

Streamlit will provide a local URL, usually:

```text
http://localhost:8501
```

Open the URL in your browser, upload your resume, optionally add a job description, and click **Analyze Resume**.



## Project Structure

```text
AI_Resume_Analyzer/
├── resume_analyzer.py
├── app.py
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
```

