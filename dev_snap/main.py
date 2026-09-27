from pathlib import Path
import subprocess
from typing import Optional, List, Dict, Any
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="dev-snap: Terminal dashboard for local Git workspace activity.")
console = Console()

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
    """Extract Git status, branch, ahead/behind count, and last commit info."""
    # 1. Branch name
    branch = run_git_cmd(["branch", "--show-current"], repo_path) or "HEAD detached"

    # 2. Status check (staged, unstaged, untracked)
    status_raw = run_git_cmd(["status", "--porcelain"], repo_path) or ""
    lines = [line for line in status_raw.splitlines() if line.strip()]
    staged = sum(1 for line in lines if line[0] in "MADRC")
    unstaged = sum(1 for line in lines if line[1] in "MD")
    untracked = sum(1 for line in lines if line.startswith("??"))

    # 3. Sync status vs upstream (ahead / behind)
    rev_count = run_git_cmd(["rev-list", "--left-right", "--count", "HEAD...@{u}"], repo_path)
    ahead, behind = 0, 0
    if rev_count:
        parts = rev_count.split()
        if len(parts) == 2:
            ahead, behind = int(parts[0]), int(parts[1])

    # 4. Last commit details
    log_info = run_git_cmd(["log", "-1", "--format=%cr|%s"], repo_path)
    last_commit_time, last_commit_msg = ("No commits yet", "")
    if log_info and "|" in log_info:
        last_commit_time, last_commit_msg = log_info.split("|", 1)

    return {
        "name": repo_path.name,
        "branch": branch,
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked,
        "ahead": ahead,
        "behind": behind,
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
):
    """Scan workspace directories and display a styled status table."""
    repos: List[Path] = []

    # Find directories containing a .git folder up to specified depth
    for d in [path] + [p for p in path.glob("*/" * depth) if p.is_dir()]:
        if (d / ".git").is_dir():
            repos.append(d)

    unique_repos = list(dict.fromkeys(repos))

    if not unique_repos:
        console.print(f"[yellow]No Git repositories discovered under:[/yellow] {path}")
        raise typer.Exit()

    table = Table(
        title="[bold cyan]⚡ dev-snap Workspace Snapshot[/bold cyan]",
        border_style="bright_black",
        header_style="bold magenta",
        title_justify="left",
    )

    table.add_column("Repository", style="bold white")
    table.add_column("Branch", style="green")
    table.add_column("Working Tree", justify="center")
    table.add_column("Sync", justify="center")
    table.add_column("Last Commit", style="dim")

    for repo in unique_repos:
        data = analyze_repo(repo)

        # Working tree status badge
        changes = []
        if data["staged"]:
            changes.append(f"[green]+{data['staged']}[/green]")
        if data["unstaged"]:
            changes.append(f"[yellow]*{data['unstaged']}[/yellow]")
        if data["untracked"]:
            changes.append(f"[red]?{data['untracked']}[/red]")
        status_display = " ".join(changes) if changes else "[bold green]Clean[/bold green]"

        # Sync badge
        sync_items = []
        if data["ahead"]:
            sync_items.append(f"[cyan]▲{data['ahead']}[/cyan]")
        if data["behind"]:
            sync_items.append(f"[red]▼{data['behind']}[/red]")
        sync_display = " ".join(sync_items) if sync_items else "[dim]Synced[/dim]"

        # Commit summary
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

    console.print()
    console.print(table)
    console.print()

if __name__ == "__main__":
    app()