from pathlib import Path
import subprocess
import json
import os
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(help="dev-snap: Fast terminal dashboard for local Git workspace activity.")
console = Console()

class SortOption(str, Enum):
    name = "name"
    recent = "recent"
    dirty = "dirty"

def run_git_cmd(cmd: List[str], cwd: Path) -> Optional[str]:
    """Execute a Git command safely inside a target directory."""
    try:
        res = subprocess.run(
            ["git"] + cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            encoding="utf-8"
        )
        return res.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def analyze_repo(repo_path: Path) -> Dict[str, Any]:
    """Extract Git status, branch, ahead/behind count, and commit info."""
    branch = run_git_cmd(["branch", "--show-current"], repo_path) or "HEAD detached"

    status_raw = run_git_cmd(["status", "--porcelain"], repo_path) or ""
    lines = [line for line in status_raw.splitlines() if line.strip()]
    staged = sum(1 for line in lines if line[0] in "MADRC")
    unstaged = sum(1 for line in lines if line[1] in "MD")
    untracked = sum(1 for line in lines if line.startswith("??"))

    rev_count = run_git_cmd(["rev-list", "--left-right", "--count", "HEAD...@{u}"], repo_path)
    ahead, behind = 0, 0
    if rev_count:
        parts = rev_count.split()
        if len(parts) == 2:
            ahead, behind = int(parts[0]), int(parts[1])

    log_info = run_git_cmd(["log", "-1", "--format=%cr|%s|%ct"], repo_path)
    last_commit_time, last_commit_msg, commit_epoch = ("No commits yet", "", 0)
    if log_info and "|" in log_info:
        parts = log_info.split("|", 2)
        last_commit_time = parts[0]
        last_commit_msg = parts[1]
        commit_epoch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0

    is_dirty = (staged > 0) or (unstaged > 0) or (untracked > 0)

    return {
        "name": repo_path.name,
        "path": str(repo_path.resolve()),
        "branch": branch,
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked,
        "ahead": ahead,
        "behind": behind,
        "is_dirty": is_dirty,
        "commit_epoch": commit_epoch,
        "last_commit_time": last_commit_time,
        "last_commit_msg": last_commit_msg[:40] + ("..." if len(last_commit_msg) > 40 else ""),
    }

@app.command()
def scan(
    path: Path = typer.Argument(
        Path("."),
        help="Root directory containing project folders to scan",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    depth: int = typer.Option(
        2,
        "--depth",
        "-d",
        help="Subdirectory search depth for Git repositories",
    ),
    dirty_only: bool = typer.Option(
        False,
        "--dirty-only",
        "-o",
        help="Display only repositories with uncommitted or unpushed changes",
    ),
    sort: SortOption = typer.Option(
        SortOption.name,
        "--sort",
        "-s",
        help="Sort results by: name, recent (last commit), or dirty",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output raw snapshot data formatted as JSON",
    ),
):
    """Scan workspace directories in parallel and display a styled status dashboard."""
    repos: List[Path] = []

    for d in [path] + [p for p in path.glob("*/" * depth) if p.is_dir()]:
        if (d / ".git").is_dir():
            repos.append(d)

    unique_repos = list(dict.fromkeys(repos))

    if not unique_repos:
        if as_json:
            print("[]")
        else:
            console.print(f"[yellow]No Git repositories discovered under:[/yellow] {path}")
        raise typer.Exit()

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(analyze_repo, unique_repos))

    if dirty_only:
        results = [r for r in results if r["is_dirty"] or r["ahead"] > 0]

    # Sorting
    if sort == SortOption.recent:
        results.sort(key=lambda r: r["commit_epoch"], reverse=True)
    elif sort == SortOption.dirty:
        results.sort(key=lambda r: (not r["is_dirty"], r["name"].lower()))
    else:
        results.sort(key=lambda r: r["name"].lower())

    # Raw JSON Output
    if as_json:
        print(json.dumps(results, indent=2))
        return

    # Visual Output
    total_repos = len(results)
    dirty_count = sum(1 for r in results if r["is_dirty"])
    ahead_count = sum(1 for r in results if r["ahead"] > 0)
    behind_count = sum(1 for r in results if r["behind"] > 0)

    banner = (
        f"[bold white]Repos:[/bold white] [cyan]{total_repos}[/cyan]  │  "
        f"[bold white]Dirty:[/bold white] [{'red' if dirty_count else 'green'}]{dirty_count}[/{'red' if dirty_count else 'green'}]  │  "
        f"[bold white]Unpushed (▲):[/bold white] [{'yellow' if ahead_count else 'dim'}]{ahead_count}[/{'yellow' if ahead_count else 'dim'}]  │  "
        f"[bold white]Behind (▼):[/bold white] [{'magenta' if behind_count else 'dim'}]{behind_count}[/{'magenta' if behind_count else 'dim'}]"
    )
    console.print()
    console.print(Panel(banner, title="[bold cyan]⚡ dev-snap Workspace Overview[/bold cyan]", border_style="cyan"))

    if dirty_only and not results:
        console.print("[bold green]✨ All repositories are clean and synced![/bold green]\n")
        raise typer.Exit()

    table = Table(
        border_style="bright_black",
        header_style="bold magenta",
        title_justify="left",
    )

    table.add_column("Repository", style="bold white")
    table.add_column("Branch", style="green")
    table.add_column("Working Tree", justify="center")
    table.add_column("Sync", justify="center")
    table.add_column("Last Commit", style="dim")

    for data in results:
        changes = []
        if data["staged"]:
            changes.append(f"[green]+{data['staged']}[/green]")
        if data["unstaged"]:
            changes.append(f"[yellow]*{data['unstaged']}[/yellow]")
        if data["untracked"]:
            changes.append(f"[red]?{data['untracked']}[/red]")
        status_display = " ".join(changes) if changes else "[bold green]Clean[/bold green]"

        sync_items = []
        if data["ahead"]:
            sync_items.append(f"[cyan]▲{data['ahead']}[/cyan]")
        if data["behind"]:
            sync_items.append(f"[red]▼{data['behind']}[/red]")
        sync_display = " ".join(sync_items) if sync_items else "[dim]Synced[/dim]"

        commit_display = f"{data['last_commit_time']}"
        if data["last_commit_msg"]:
            commit_display += f" - [white]{data['last_commit_msg']}[/white]"

        table.add_row(
            data["name"],
            data["branch"],
            status_display,
            sync_display,
            commit_display,
        )

    console.print(table)
    console.print("[dim]Legend: [green]+staged[/green]  [yellow]*unstaged[/yellow]  [red]?untracked[/red]  │  [cyan]▲ ahead[/cyan]  [red]▼ behind[/red][/dim]")
    console.print()

if __name__ == "__main__":
    app()