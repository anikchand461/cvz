# cvz — ATS Resume Analyzer CLI

A command-line tool that scores resumes against job roles using keyword matching, semantic similarity, and structural analysis. Supports PDF and DOCX files.

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

After installing, download the spaCy model for semantic scoring:

```bash
python -m spacy download en_core_web_md
```

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

### Suggest the best-fit role for a resume

```bash
cvz suggest-role resume.pdf
```

### Gap analysis — see what's missing for a role

```bash
cvz gap resume.pdf --role machine_learning
```

### Compare multiple resumes

```bash
cvz compare r1.pdf r2.pdf --role backend
```

### List all supported roles

```bash
cvz roles
```

---

## Scoring

Each resume is scored across three dimensions:

| Metric    | Weight | Description                                              |
| --------- | ------ | -------------------------------------------------------- |
| Keyword   | 50%    | Matches core (70%) and secondary (30%) role keywords     |
| Semantic  | 30%    | spaCy cosine similarity between resume and role keywords |
| Structure | 20%    | Presence of standard sections + resume length            |

---

## Supported Roles

Built-in roles include:

- `backend`
- `frontend`
- `full_stack`
- `machine_learning`
- `data_science`
- _(run `cvz roles` for the full list)_

Role keyword sets are defined in `src/cvscan/data/roles.json` and can be extended.

---

## Supported File Formats

- `.pdf` — via `pdfplumber`
- `.docx` — via `python-docx`

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
│       ├── main.py              # CLI commands (Typer)
│       ├── data/
│       │   └── roles.json       # Role keyword definitions
│       ├── engines/
│       │   ├── keyword_engine.py   # Keyword-based scoring
│       │   ├── spacy_engine.py     # Semantic similarity scoring
│       │   └── structure_engine.py # Resume structure scoring
│       ├── parser/
│       │   ├── pdf_parser.py    # PDF text extraction
│       │   └── docx_parser.py   # DOCX text extraction
│       └── utils/
│           ├── loader.py        # File + role data loading
│           └── cleaner.py       # Text normalization
├── pyproject.toml
└── requirements.txt
```

---

## Author

Anik Chand
