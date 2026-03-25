import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
import time

from cvscan.utils.loader import load_resume, load_keywords, load_all_roles
from cvscan.utils.cleaner import clean_text

from cvscan.engines.keyword_engine import keyword_score
from cvscan.engines.structure_engine import structure_score

app = typer.Typer(help="🚀 CVScan - ATS Resume Analyzer CLI")
console = Console()


# =========================
# HELP
# =========================
@app.callback()
def main():
    """
🚀 CVScan - ATS Resume Analyzer CLI

Usage:

1. Analyze resume:
   cvscan analyze resume.pdf --role backend

2. Auto-detect role:
   cvscan analyze resume.pdf

3. Custom JD:
   cvscan analyze resume.pdf --jd "python django api"

4. Compare resumes:
   cvscan compare r1.pdf r2.pdf

5. Gap analysis:
   cvscan gap resume.pdf --role machine_learning

6. Suggest role:
   cvscan suggest-role resume.pdf

7. List roles:
   cvscan roles
"""
    pass


# =========================
# HELPERS
# =========================
def flatten_role(role_data):
    return [
        kw
        for group in (role_data.get("core", []) + role_data.get("secondary", []))
        for kw in group
    ]


def get_best_role_and_score(text):
    roles = load_all_roles()
    results = []

    for role in roles:
        role_data = load_keywords(role)
        flat = flatten_role(role_data)

        k_score, _ = keyword_score(text, role_data)
        s_score = spacy_score(text, " ".join(flat))

        final = 0.6 * k_score + 0.4 * s_score
        results.append((role, final))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[0]


# =========================
# ANALYZE
# =========================
@app.command()
def analyze(
    file: str,
    role: str = typer.Option(None, "--role", "-r"),
    jd: str = typer.Option(None, "--jd")
):
    from cvscan.engines.spacy_engine import spacy_score
    console.print("\n🔍 Analyzing Resume...\n")

    for _ in track(range(3)):
        time.sleep(0.3)

    raw = load_resume(file)
    if not raw:
        console.print("[red]❌ Failed to load resume[/red]")
        return

    text = clean_text(raw)

    # -------- role logic --------
    if jd:
        keywords = jd.lower().split()
        job_desc = " ".join(keywords)

        k_score = sum(1 for k in keywords if k in text) / len(keywords) * 100
        matched = keywords

    else:
        if not role:
            console.print("[yellow]⚡ Auto detecting role...[/yellow]")
            role, score = get_best_role_and_score(text)
            console.print(f"[green]🎯 Role: {role} ({score:.2f}%)\n[/green]")

        role_data = load_keywords(role)
        flat = flatten_role(role_data)

        k_score, matched = keyword_score(text, role_data)
        job_desc = " ".join(flat)

    s_score = spacy_score(text, job_desc)
    st_score = structure_score(text)

    final = 0.5 * k_score + 0.3 * s_score + 0.2 * st_score

    # -------- UI --------
    table = Table()
    table.add_column("Metric")
    table.add_column("Score")

    table.add_row("Keyword", f"{k_score:.2f}%")
    table.add_row("Semantic", f"{s_score:.2f}%")
    table.add_row("Structure", f"{st_score:.2f}%")
    table.add_row("Final", f"[bold]{final:.2f}%[/bold]")

    console.print(Panel(table, title="📊 CVSCAN REPORT"))

    # -------- missing --------
    if not jd:
# flatten matched groups
        matched_flat = [kw for group in matched for kw in group]

        missing = list(set(flat) - set(matched_flat))
        console.print("\n[red]Missing Skills:[/red]")
        for m in missing[:10]:
            console.print(f"- {m}")


# =========================
# ROLES
# =========================
@app.command()
def roles():
    console.print("\n📌 Available Roles:\n")

    for r in load_all_roles():
        console.print(f"👉 {r}")


# =========================
# SUGGEST ROLE
# =========================
@app.command("suggest-role")
def suggest_role(file: str):
    raw = load_resume(file)
    text = clean_text(raw)

    roles = load_all_roles()
    results = []

    for role in roles:
        role_data = load_keywords(role)
        flat = flatten_role(role_data)

        k_score, _ = keyword_score(text, role_data)
        s_score = spacy_score(text, " ".join(flat))

        final = 0.6 * k_score + 0.4 * s_score
        results.append((role, final))

    results.sort(key=lambda x: x[1], reverse=True)

    best_role, best_score = results[0]

    console.print(f"\n🏆 Best Role: {best_role} ({best_score:.2f}%)\n")

    table = Table()
    table.add_column("Role")
    table.add_column("Score")

    for r, s in results[:5]:
        table.add_row(r, f"{s:.2f}%")

    console.print(table)


# =========================
# GAP
# =========================
@app.command()
def gap(file: str, role: str = typer.Option(..., "-r")):
    raw = load_resume(file)
    text = clean_text(raw)

    role_data = load_keywords(role)

    def match_group(group):
        return any(k in text for k in group)

    matched = [g for g in role_data["core"] if match_group(g)]
    missing = [g for g in role_data["core"] if not match_group(g)]

    score = len(matched) / len(role_data["core"]) * 100

    console.print(f"\n📊 Match Score: {score:.2f}%\n")

    console.print("✅ Strengths:")
    for g in matched:
        console.print(f"- {g}")

    console.print("\n❌ Missing:")
    for g in missing:
        console.print(f"- {g}")


# =========================
# COMPARE
# =========================
@app.command()
def compare(
    files: list[str],
    role: str = typer.Option(None, "-r")
):
    results = []

    for file in files:
        raw = load_resume(file)
        text = clean_text(raw)

        if role:
            role_data = load_keywords(role)
            used_role = role
        else:
            used_role, _ = get_best_role_and_score(text)
            role_data = load_keywords(used_role)

        flat = flatten_role(role_data)

        k_score, _ = keyword_score(text, role_data)
        s_score = spacy_score(text, " ".join(flat))
        st_score = structure_score(text)

        final = 0.5 * k_score + 0.3 * s_score + 0.2 * st_score

        results.append((file, final, used_role))

    results.sort(key=lambda x: x[1], reverse=True)

    table = Table()
    table.add_column("Resume")
    table.add_column("Role")
    table.add_column("Score")

    for f, s, r in results:
        table.add_row(f, r, f"{s:.2f}%")

    console.print(Panel(table, title="📊 Comparison"))


if __name__ == "__main__":
    app()
