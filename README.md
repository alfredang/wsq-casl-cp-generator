# CASL Course Document Generator

A web application that extracts structured course information from Excel files and generates professionally formatted **Course Documents** and **Lesson Plans** in Word (.docx) format.

Built for training providers working with the CASL (Course Accreditation and Standards for Learning) framework.

## What It Does

Upload a course planning Excel workbook and instantly generate:

- **Course Document** -- A comprehensive Word document covering all course particulars, background, instructional design, assessments, and a summary with topics, methods, and durations.
- **Lesson Plan** -- A clean, schedule-based Word document with day-by-day timetables, time slots, lunch breaks, and assessment periods.

### Extracted Information

| Section | Fields |
|---------|--------|
| **Course Particulars** | Training Provider, Course Title, Course Type, About the Course, What You'll Learn, Unique Skill Name |
| **Course Background** | Targeted Sectors, Performance Gaps, Training Needs |
| **Instructional Design** | Learning Outcomes (LO1-LO7), Topics (T1-T7), Duration per Topic |
| **Methodologies** | Instruction Methods, Instructional Duration, Mode of Training |
| **Assessment** | Mode of Assessment, Assessment Duration, No. of Candidates |
| **Summary** | Total Course/Instructional/Assessment Duration |

## Tech Stack

- **Python 3.13** with **uv** for package management
- **Streamlit** -- Interactive web UI with upload, preview, and download
- **FastAPI** -- REST API backend
- **openpyxl** -- Excel file parsing
- **python-docx** -- Word document generation

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Install & Run

```bash
# Clone the repo
git clone https://github.com/alfredang/casl-generator.git
cd casl-generator

# Install dependencies
uv sync

# Run the Streamlit app
uv run streamlit run streamlit_app.py
```

Open **http://localhost:8501** in your browser.

### Alternative: FastAPI Server

```bash
uv run uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000** for the upload page, or use the API directly:

```bash
curl -X POST -F "file=@your_course.xlsx" http://localhost:8000/api/generate
```

## Project Structure

```
casl-generator/
├── streamlit_app.py           # Streamlit web UI
├── main.py                    # FastAPI entry point
├── app/
│   ├── config.py              # Excel cell reference mappings
│   ├── models.py              # Pydantic data models
│   ├── extractor.py           # Excel data extraction
│   ├── generator_docx.py      # Course Document generation
│   ├── generator_lesson_plan.py  # Lesson Plan generation
│   ├── generator_md.py        # Markdown generation
│   └── routes.py              # FastAPI API endpoints
├── static/                    # FastAPI frontend assets
├── pyproject.toml             # Project config & dependencies
└── uv.lock                    # Locked dependencies
```

## License

MIT
