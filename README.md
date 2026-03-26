# cvz — ATS Resume Analyzer CLI

A fast command-line tool that scores resumes against job roles using keyword matching, semantic similarity, and structural analysis. Supports PDF, DOCX, and TXT files.

---

## Installation

```bash
pip install cvz
```

Or install from source:

```bash
git clone <repo>
cd cvscan
pip install -e .
```

> Requires Python 3.9+

Download the spaCy model for semantic scoring (recommended):

```bash
python -m spacy download en_core_web_md
```

> If not installed, semantic scoring is automatically skipped with a warning — all other features work normally.

---

## Usage

### Analyze a resume against a role

```bash
cvz analyze resume.pdf --role backend
```

### Auto-detect the best matching role

```bash
cvz analyze resume.pdf
```

### Analyze against a custom job description

```bash
cvz analyze resume.pdf --jd "python django rest api postgresql"
```

### Export the report to JSON

```bash
cvz analyze resume.pdf --role devops --export report.json
```

### Suggest the best-fit roles for a resume

```bash
cvz suggest-role resume.pdf
cvz suggest-role resume.pdf --top 10
```

### Gap analysis — see strengths and missing skills

```bash
cvz gap resume.pdf --role machine_learning
cvz gap resume.pdf --role backend --export gap.json
```

### Compare multiple resumes

```bash
cvz compare r1.pdf r2.pdf r3.pdf
cvz compare r1.pdf r2.pdf --role frontend --export compare.json
```

### List all supported roles

```bash
cvz roles
```

### Show version

```bash
cvz --version
```

---

## Scoring

Each resume is scored across three dimensions:

| Metric    | Weight | Description                                              |
| --------- | ------ | -------------------------------------------------------- |
| Keyword   | 50%    | Matches core (70%) and secondary (30%) role keywords     |
| Semantic  | 30%    | spaCy cosine similarity between resume and role keywords |
| Structure | 20%    | Presence of standard sections + resume length            |

Score thresholds:

| Score  | Rating       |
| ------ | ------------ |
| >= 75% | Great match  |
| 50-74% | Decent match |
| < 50%  | Low match    |

---

## Supported Roles

| Role               | Role                |
| ------------------ | ------------------- |
| `backend`          | `frontend`          |
| `full_stack`       | `software_engineer` |
| `data_scientist`   | `data_analyst`      |
| `machine_learning` | `ai_engineer`       |
| `devops`           | `cloud_engineer`    |
| `android`          | `ios`               |
| `cybersecurity`    | `qa_engineer`       |
| `product_manager`  | `ui_ux_designer`    |
| `blockchain`       | `embedded_systems`  |

Run `cvz roles` for the full list. Role keyword sets are defined in `src/cvscan/data/roles.json` and can be extended.

---

## Supported File Formats

| Format  | Parser                                    |
| ------- | ----------------------------------------- |
| `.pdf`  | `pdfplumber`                              |
| `.docx` | `python-docx` (includes table extraction) |
| `.txt`  | built-in                                  |

---

## Dependencies

```
typer
rich
pdfplumber
python-docx
spacy
scikit-learn
```

---

## Project Structure

```
cvscan/
├── src/
│   └── cvscan/
│       ├── main.py                 # CLI commands (Typer)
│       ├── data/
│       │   └── roles.json          # Role keyword definitions
│       ├── engines/
│       │   ├── keyword_engine.py   # Keyword-based scoring
│       │   ├── spacy_engine.py     # Semantic similarity scoring
│       │   └── structure_engine.py # Resume structure scoring
│       ├── parser/
│       │   ├── pdf_parser.py       # PDF text extraction
│       │   └── docx_parser.py      # DOCX text extraction (incl. tables)
│       └── utils/
│           ├── loader.py           # File + role data loading
│           ├── cleaner.py          # Text normalisation
│           └── scorer.py           # Shared scoring helpers
├── pyproject.toml
└── requirements.txt
```

---

## Author

Anik Chand
