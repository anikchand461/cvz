# Contributing to cvz

First off — thanks for taking the time to contribute! Every bug report, feature idea, and pull request makes `cvz` better for everyone. 🙌

---

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Adding or Editing Roles](#adding-or-editing-roles)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Code Style](#code-style)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create a branch** for your change
4. **Make your changes**, test them
5. **Open a Pull Request**

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

## Ways to Contribute

You don't have to write code to contribute. Here's what's always welcome:

- 🐛 **Bug reports** — something broken? Open an issue
- 💡 **Feature requests** — have an idea? Let's discuss it
- 📝 **New roles** — add keywords for roles that aren't covered yet
- 🌍 **Better keyword sets** — improve existing role definitions in `roles.json`
- 📖 **Documentation** — fix typos, improve clarity, add examples
- ✅ **Tests** — more coverage is always better
- 🔧 **Bug fixes** — pick up an open issue and fix it

---

## Development Setup

### Prerequisites

- Python 3.9+
- Git

### Install from source

```bash
git clone https://github.com/anikchand461/cvz
cd cvz
pip install -e .
```

### Install the spaCy model (for semantic scoring)

```bash
python -m spacy download en_core_web_md
```

### Verify everything works

```bash
cvz --version
cvz analyze <your_resume.pdf> --role backend
```

---

## Making Changes

### 1. Create a branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-you-are-fixing
```

### 2. Make your changes

Keep changes focused. One feature or fix per PR makes review much easier.

### 3. Test manually

```bash
cvz analyze resume.pdf --role backend
cvz suggest-role resume.pdf
cvz gap resume.pdf --role machine_learning
```

Make sure nothing that worked before is broken.

### 4. Commit with a clear message

```bash
git commit -m "feat: add rust role to roles.json"
git commit -m "fix: handle empty PDF text extraction gracefully"
git commit -m "docs: improve gap command usage example"
```

---

## Adding or Editing Roles

This is one of the easiest and most impactful ways to contribute. Role definitions live in:

```
src/cvscan/data/roles.json
```

### Structure of a role entry

```json
"your_role": {
  "core": [
    "keyword1", "keyword2", "keyword3"
  ],
  "secondary": [
    "keyword4", "keyword5"
  ]
}
```

- **`core`** — the most important keywords for this role (weighted at 70%)
- **`secondary`** — supporting skills and tools (weighted at 30%)

### Tips for good keyword sets

- Include common synonyms (e.g. `"postgres"` alongside `"postgresql"`)
- Cover both technologies and concepts (e.g. `"docker"` and `"containerization"`)
- Don't overload — quality over quantity; 20–40 core keywords is a good range
- Check what real job descriptions for this role commonly require

### Test your new role

```bash
cvz roles                          # should show your new role
cvz analyze resume.pdf --role your_role
```

---

## Submitting a Pull Request

1. Push your branch to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a PR against the `main` branch of the original repo

3. In your PR description, include:
   - **What** you changed
   - **Why** (link to an issue if relevant)
   - **How to test** it

4. Be responsive to review feedback — small iterations are totally fine

---

## Code Style

- Follow existing code patterns in the file you're editing
- Use clear variable names — readability over cleverness
- Add a comment if something isn't immediately obvious
- Keep functions focused — one job per function

No strict linter enforced yet, but keep things clean and consistent.

---

## Reporting Bugs

Open an issue and include:

- Your OS and Python version
- The command you ran
- What you expected vs what happened
- The full error output (if any)

---

## Suggesting Features

Open an issue with the `enhancement` label. Describe:

- The problem you're trying to solve
- Your proposed solution
- Any alternatives you considered

Big changes are best discussed in an issue before you start coding, so effort isn't wasted.

---

## Questions?

Open an issue or reach out directly. Happy to help you get started. 🚀
