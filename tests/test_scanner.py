from pathlib import Path
from dev_snap.main import analyze_repo

def test_current_repo_analysis():
    cwd = Path(".").resolve()
    data = analyze_repo(cwd)
    assert data["name"] == "dev-snap"
    assert data["branch"] in ["main", "HEAD detached"]
    assert isinstance(data["staged"], int)
    assert isinstance(data["unstaged"], int)
    assert isinstance(data["untracked"], int)