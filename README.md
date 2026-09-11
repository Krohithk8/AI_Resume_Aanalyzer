# AI Resume Analyzer

AI Resume Analyzer is a small command-line portfolio project that uses Anthropic Claude to review a plain-text resume. Give it a job description to assess role fit, identify missing ATS keywords, and propose fact-preserving stronger bullet points; omit the job description for a general quality review.

It is useful for job seekers who want a quick, structured second pass before applying, while keeping the final judgment with the candidate. The model is explicitly instructed to rely on the supplied resume rather than inventing achievements.

## Requirements and setup

- Python 3.10 or later
- An Anthropic API key with access to `claude-sonnet-4-5`

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-api-key-here"
```

If your computer does not already have Python 3.10+, create the virtual
environment with any current Python installation instead. VS Code is configured
to automatically use `.venv/bin/python` once the environment exists.

Never put an API key in the source code, commit it to Git, or share it in a screenshot. The key is read only from the `ANTHROPIC_API_KEY` environment variable.

## Usage

Analyze the included resume against the included backend role:

```bash
python resume_analyzer.py \
  --resume sample_data/resume.txt \
  --jd sample_data/job_description.txt
```

Run a general resume-quality evaluation without a job description:

```bash
python resume_analyzer.py --resume sample_data/resume.txt
```

Print the readable report and also save the full structured JSON response:

```bash
python resume_analyzer.py \
  --resume sample_data/resume.txt \
  --jd sample_data/job_description.txt \
  --output reports/maya-patel-backend.json
```

## Example terminal output

```text
AI RESUME ANALYZER
==========================================================
Match score: 72/100

Summary
Maya has relevant Python, Django, PostgreSQL, AWS, and testing experience for this backend role. The resume would be stronger with measured outcomes and clearer evidence of operational ownership.

Strengths
  - Three years of professional software development experience
  - Python, Django, PostgreSQL, Docker, AWS, and pytest are listed

Gaps
  - No evidence of asynchronous workflows or background jobs
  - Production monitoring and on-call responsibilities are not described

Missing ATS keywords
  - FastAPI
  - Redis
  - Celery
  - CI/CD

Bullet-point rewrites
  Original: Worked on backend features for an online learning platform used by thousands of students.
  Improved: Developed Python backend features for an online learning platform serving thousands of students.
```

Actual scores and recommendations vary with the model response and the content supplied.

## Project structure

```text
AI_Resume_Analyzer/
├── resume_analyzer.py
├── requirements.txt
├── sample_data/
│   ├── resume.txt
│   └── job_description.txt
├── README.md
└── .gitignore
```


