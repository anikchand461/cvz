import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box
import json
import time
from typing import Optional

from cvscan.utils.loader import load_resume, load_keywords, load_all_roles
from cvscan.utils.cleaner import clean_text

app = typer.Typer(
    help="🚀 CVZ — ATS Resume Analyzer CLI",
    add_completion=False,
)
console = Console()

VERSION = "0.1.2"

def _imports():
    global keyword_score, spacy_score, structure_score, flatten_role, get_best_role_and_score
    from cvscan.engines.keyword_engine import keyword_score
    from cvscan.engines.spacy_engine import spacy_score
    from cvscan.engines.structure_engine import structure_score
    from cvscan.utils.scorer import flatten_role, get_best_role_and_score


# ─────────────────────────────────────────
# VERSION
# ─────────────────────────────────────────
def version_callback(value: bool):
    if value:
        console.print(f"[bold cyan]cvz[/bold cyan] version [green]{VERSION}[/green]")
        raise typer.Exit()


# ─────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────
def print_banner():
    console.print(
        Panel.fit(
            f"[bold cyan]CVZ — ATS Resume Analyzer[/bold cyan]  [dim]v{VERSION}[/dim]",
            border_style="cyan",
            padding=(0, 2),
        )
    )


# ─────────────────────────────────────────
# SCORE COLOR HELPER
# ─────────────────────────────────────────
def score_color(score: float) -> str:
    if score >= 75:
        return "green"
    elif score >= 50:
        return "yellow"
    else:
        return "red"


def score_bar(score: float, width: int = 20) -> str:
    filled = int(score / 100 * width)
    empty = width - filled
    color = score_color(score)
    return f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"


# ─────────────────────────────────────────
# CALLBACK
# ─────────────────────────────────────────
@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    )
):
    """
    🚀 CVZ — ATS Resume Analyzer CLI

    Commands:

    \b
      analyze      Score a resume against a role or job description
      gap          Show missing skills for a role
      compare      Compare multiple resumes side by side
      suggest-role Auto-detect the best matching role
      roles        List all supported roles
    """
    pass


# ─────────────────────────────────────────
# ANALYZE
# ─────────────────────────────────────────
@app.command()
def analyze(
    file: str = typer.Argument(..., help="Path to resume (.pdf, .docx, .txt)"),
    role: Optional[str] = typer.Option(None, "--role", "-r", help="Target role (e.g. backend, devops)"),
    jd: Optional[str] = typer.Option(None, "--jd", help="Custom job description keywords"),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export report to a JSON file"),
    top: int = typer.Option(10, "--top", "-t", help="Number of missing skills to show"),
):
    _imports()
    """Score a resume against a role or custom job description."""
    print_banner()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        t1 = progress.add_task("Parsing resume...", total=None)
        raw = load_resume(file)
        progress.remove_task(t1)

        if not raw:
            console.print("[red]❌ Failed to load resume. Check the file path and format.[/red]")
            raise typer.Exit(1)

        t2 = progress.add_task("Cleaning text...", total=None)
        text = clean_text(raw)
        progress.remove_task(t2)

        t3 = progress.add_task("Scoring...", total=None)

        if jd:
            keywords = jd.lower().split()
            job_desc = " ".join(keywords)
            k_score = sum(1 for k in keywords if k in text) / len(keywords) * 100
            matched = keywords
            flat = keywords
        else:
            if not role:
                progress.update(t3, description="Auto-detecting role...")
                role, _ = get_best_role_and_score(text)
                console.print(f"\n[yellow]⚡ Auto-detected role:[/yellow] [bold cyan]{role}[/bold cyan]\n")

            role_data = load_keywords(role)
            flat = flatten_role(role_data)
            k_score, matched = keyword_score(text, role_data)
            job_desc = " ".join(flat)

        s_score = spacy_score(text, job_desc)
        st_score = structure_score(text)

        # Gate semantic contribution when keyword match is very weak to prevent
        # corpus-level vector similarity from inflating scores on poor matches
        s_weight = 0.3 if k_score >= 20 else 0.15
        k_weight = 1.0 - s_weight - 0.2
        final = k_weight * k_score + s_weight * s_score + 0.2 * st_score

        progress.remove_task(t3)

    # ── Score table ──
    color = score_color(final)
    table = Table(box=box.ROUNDED, border_style="dim", show_header=True, header_style="bold")
    table.add_column("Metric", style="bold", width=12)
    table.add_column("Bar", width=24, no_wrap=True)
    table.add_column("Score", justify="right", width=8)

    for label, val in [("Keyword", k_score), ("Semantic", s_score), ("Structure", st_score)]:
        c = score_color(val)
        table.add_row(label, score_bar(val), f"[{c}]{val:.1f}%[/{c}]")

    table.add_section()
    table.add_row(
        "Final",
        score_bar(final),
        f"[bold {color}]{final:.1f}%[/bold {color}]",
    )

    console.print(Panel(table, title=f"[bold]📊 CVSCAN REPORT[/bold]  [dim]{file}[/dim]", border_style=color))

    # ── Tip ──
    if final >= 75:
        console.print("[green]✅ Great match! Your resume aligns well with this role.[/green]")
    elif final >= 50:
        console.print("[yellow]⚠️  Decent match. A few targeted improvements could boost your score.[/yellow]")
    else:
        console.print("[red]❌ Low match. Consider tailoring your resume more closely to the role.[/red]")

    # ── Missing skills ──
    if not jd:
        matched_flat = [kw for group in matched for kw in group]
        missing = sorted(set(flat) - set(matched_flat))[:top]

        if missing:
            console.print(f"\n[bold red]Missing Skills[/bold red] [dim](top {min(top, len(missing))})[/dim]")
            miss_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
            miss_table.add_column("", style="red", width=3)
            miss_table.add_column("")
            for skill in missing:
                miss_table.add_row("✗", f"[dim]{skill}[/dim]")
            console.print(miss_table)
        else:
            console.print("\n[green]🎉 No missing core skills![/green]")

    # ── Export ──
    if export:
        report = {
            "file": file,
            "role": role if not jd else None,
            "jd": jd,
            "scores": {
                "keyword": round(k_score, 2),
                "semantic": round(s_score, 2),
                "structure": round(st_score, 2),
                "final": round(final, 2),
            },
            "missing_skills": missing if not jd else [],
        }
        with open(export, "w") as f:
            json.dump(report, f, indent=2)
        console.print(f"\n[cyan]📁 Report exported → {export}[/cyan]")


# ─────────────────────────────────────────
# ROLES
# ─────────────────────────────────────────
@app.command()
def roles():
    """List all supported roles."""
    print_banner()
    all_roles = load_all_roles()

    table = Table(box=box.ROUNDED, border_style="dim", header_style="bold cyan")
    table.add_column("#", width=4, style="dim")
    table.add_column("Role", style="bold")

    for i, r in enumerate(all_roles, 1):
        table.add_row(str(i), r)

    console.print(Panel(table, title="[bold]📌 Available Roles[/bold]", border_style="cyan"))
    console.print(f"[dim]Use with:[/dim] [cyan]cvz analyze resume.pdf --role <name>[/cyan]\n")


# ─────────────────────────────────────────
# SUGGEST ROLE
# ─────────────────────────────────────────
@app.command("suggest-role")
def suggest_role(
    file: str = typer.Argument(..., help="Path to resume (.pdf, .docx, .txt)"),
    top: int = typer.Option(5, "--top", "-t", help="Number of top roles to show"),
):
    _imports()
    """Auto-detect the best-fit roles for a resume."""
    print_banner()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task("Analyzing resume...", total=None)
        raw = load_resume(file)
        text = clean_text(raw)
        results = get_best_role_and_score(text, return_all=True)

    best_role, best_score = results[0]
    color = score_color(best_score)

    console.print(f"\n[bold]🏆 Best Match:[/bold] [bold {color}]{best_role}[/bold {color}]  {score_bar(best_score)}  [{color}]{best_score:.1f}%[/{color}]\n")

    table = Table(box=box.ROUNDED, border_style="dim", header_style="bold")
    table.add_column("#", width=4, style="dim")
    table.add_column("Role", style="bold")
    table.add_column("Bar", width=24)
    table.add_column("Score", justify="right")

    for i, (r, s) in enumerate(results[:top], 1):
        c = score_color(s)
        table.add_row(str(i), r, score_bar(s), f"[{c}]{s:.1f}%[/{c}]")

    console.print(Panel(table, title="[bold]🎯 Role Suggestions[/bold]", border_style="cyan"))


# ─────────────────────────────────────────
# GAP
# ─────────────────────────────────────────
@app.command()
def gap(
    file: str = typer.Argument(..., help="Path to resume (.pdf, .docx, .txt)"),
    role: str = typer.Option(..., "--role", "-r", help="Target role to analyze gap for"),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export gap report to JSON"),
):
    _imports()
    """Show skill gap — what you have and what's missing for a role."""
    print_banner()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task("Running gap analysis...", total=None)
        raw = load_resume(file)
        text = clean_text(raw)

    role_data = load_keywords(role)
    if not role_data:
        console.print(f"[red]❌ Role '{role}' not found. Run [bold]cvz roles[/bold] to see available roles.[/red]")
        raise typer.Exit(1)

    def match_group(group):
        return any(k in text for k in group)

    matched = [g for g in role_data["core"] if match_group(g)]
    missing = [g for g in role_data["core"] if not match_group(g)]
    score = len(matched) / len(role_data["core"]) * 100
    color = score_color(score)

    console.print(f"\n[bold]Role:[/bold] [cyan]{role}[/cyan]   [bold]Core Match:[/bold] [{color}]{score:.1f}%[/{color}]  {score_bar(score)}\n")

    # strengths
    s_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    s_table.add_column("", style="green", width=3)
    s_table.add_column("")
    for g in matched:
        s_table.add_row("✓", f"[green]{' / '.join(g)}[/green]")
    console.print(Panel(s_table, title="[bold green]✅ Strengths[/bold green]", border_style="green"))

    # gaps
    if missing:
        m_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        m_table.add_column("", style="red", width=3)
        m_table.add_column("")
        m_table.add_column("Suggestion", style="dim")
        for g in missing:
            label = " / ".join(g)
            tip = f"Add any of: {', '.join(g)}"
            m_table.add_row("✗", f"[red]{label}[/red]", tip)
        console.print(Panel(m_table, title="[bold red]❌ Missing Skills[/bold red]", border_style="red"))
    else:
        console.print("[green]🎉 No core skill gaps found![/green]")

    if export:
        report = {
            "file": file,
            "role": role,
            "score": round(score, 2),
            "strengths": matched,
            "missing": missing,
        }
        with open(export, "w") as f:
            json.dump(report, f, indent=2)
        console.print(f"\n[cyan]📁 Gap report exported → {export}[/cyan]")


# ─────────────────────────────────────────
# COMPARE
# ─────────────────────────────────────────
@app.command()
def compare(
    files: list[str] = typer.Argument(..., help="Two or more resume files to compare"),
    role: Optional[str] = typer.Option(None, "--role", "-r", help="Role to compare against (auto-detected if omitted)"),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export comparison to JSON"),
):
    _imports()
    """Compare multiple resumes side by side."""
    print_banner()

    if len(files) < 2:
        console.print("[red]❌ Provide at least 2 resume files to compare.[/red]")
        raise typer.Exit(1)

    results = []

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        for file in files:
            progress.add_task(f"Scoring {file}...", total=None)
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

            s_weight = 0.3 if k_score >= 20 else 0.15
            k_weight = 1.0 - s_weight - 0.2
            final = k_weight * k_score + s_weight * s_score + 0.2 * st_score

            results.append({
                "file": file,
                "role": used_role,
                "keyword": k_score,
                "semantic": s_score,
                "structure": st_score,
                "final": final,
            })

    results.sort(key=lambda x: x["final"], reverse=True)

    table = Table(box=box.ROUNDED, border_style="dim", header_style="bold")
    table.add_column("Rank", width=5, style="dim")
    table.add_column("Resume", style="bold")
    table.add_column("Role", style="cyan")
    table.add_column("Keyword", justify="right")
    table.add_column("Semantic", justify="right")
    table.add_column("Structure", justify="right")
    table.add_column("Bar", width=20)
    table.add_column("Final", justify="right")

    medals = ["🥇", "🥈", "🥉"]
    for i, r in enumerate(results):
        rank = medals[i] if i < 3 else str(i + 1)
        c = score_color(r["final"])
        table.add_row(
            rank,
            r["file"],
            r["role"],
            f"{r['keyword']:.1f}%",
            f"{r['semantic']:.1f}%",
            f"{r['structure']:.1f}%",
            score_bar(r["final"]),
            f"[bold {c}]{r['final']:.1f}%[/bold {c}]",
        )

    console.print(Panel(table, title="[bold]📊 Resume Comparison[/bold]", border_style="cyan"))

    winner = results[0]
    console.print(f"[green]🏆 Best resume:[/green] [bold]{winner['file']}[/bold] with [bold]{winner['final']:.1f}%[/bold]\n")

    if export:
        with open(export, "w") as f:
            json.dump(results, f, indent=2, default=lambda x: round(x, 2))
        console.print(f"[cyan]📁 Comparison exported → {export}[/cyan]")


if __name__ == "__main__":
    app()
