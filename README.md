# ⚡ dev-snap

> **A fast, terminal-based Git workspace dashboard for developers.**

`dev-snap` scans your workspace for Git repositories and gives you an instant overview of their current state — branches, working-tree changes, remote sync status, and recent activity — all from a single terminal command.

Instead of opening repositories one by one and running `git status`, `git log`, and remote checks manually, `dev-snap` gives you the bigger picture in seconds.

---

## ✨ Features

* 🔍 **Recursive Git repository discovery**
* ⚡ **Parallel repository scanning** using multiple workers
* 🌳 **Branch detection**
* 🟢 **Clean / dirty working-tree status**
* 📦 **Staged, unstaged, and untracked file counts**
* ⬆️ **Unpushed commits detection**
* ⬇️ **Commits behind remote detection**
* 🕒 **Latest commit information**
* 📊 **Workspace summary dashboard**
* 🔎 **Dirty-only filtering**
* ↕️ **Multiple sorting modes**
* 📄 **JSON output for scripting and automation**
* 🎨 **Rich terminal interface**
* 🛡️ **Graceful handling of invalid or non-Git directories**

---

## 🚀 Example

Run `dev-snap` on your current directory:

```bash
dev-snap .
```

Or scan an entire workspace:

```bash
dev-snap C:\Users\alden
```

Example output:

```text
╭───────────────────────────────╮
│       ⚡ DEV-SNAP             │
│   Git Workspace Dashboard     │
╰───────────────────────────────╯

Workspace: C:\Users\alden

Repositories: 12
Clean:        8
Dirty:        3
Unpushed:     1

┏━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Repository   ┃ Branch   ┃ Status   ┃ Remote       ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ dev-snap     │ main     │ ✓ Clean  │ Synced       │
│ ml-project   │ main     │ ⚠ Dirty  │ ↑ 2 ahead    │
│ leetcode     │ develop  │ ✓ Clean  │ Synced       │
└──────────────┴──────────┴──────────┴──────────────┘
```

---

## 📦 Installation

### Requirements

* Python 3.10+
* Git
* Windows, macOS, or Linux

### Clone the repository

```bash
git clone https://github.com/alden-p642/dev-snap.git
cd dev-snap
```

### Install

For development/editable installation:

```bash
pip install -e .
```

After installation, the `dev-snap` command is available directly from your terminal.

Verify the installation:

```bash
dev-snap --help
```

---

## 🖥️ Usage

### Scan the current directory

```bash
dev-snap .
```

### Scan a specific workspace

```bash
dev-snap C:\Users\alden
```

You can point `dev-snap` at a directory containing multiple projects, and it will automatically discover Git repositories inside it.

---

## 🔎 Dirty repositories only

If you only want to see repositories that currently need attention:

```bash
dev-snap . --dirty-only
```

This includes repositories with:

* staged changes
* unstaged changes
* untracked files
* unpushed commits

---

## ↕️ Sorting

Sort repositories by name:

```bash
dev-snap . --sort name
```

Sort by recent activity:

```bash
dev-snap . --sort recent
```

Sort by working-tree status:

```bash
dev-snap . --sort dirty
```

---

## 📄 JSON Output

`dev-snap` can output repository information as JSON, making it useful for scripts, automation, and other developer tools.

```bash
dev-snap . --json
```

Example:

```json
[
  {
    "name": "dev-snap",
    "branch": "main",
    "dirty": false,
    "ahead": 0,
    "behind": 0
  }
]
```

---

## 📊 Workspace Overview

When scanning a workspace containing multiple repositories, `dev-snap` provides a summary of the overall Git state.

The dashboard tracks:

| Metric       | Description                                      |
| ------------ | ------------------------------------------------ |
| Repositories | Total Git repositories discovered                |
| Clean        | Repositories with no local changes               |
| Dirty        | Repositories with local changes                  |
| Ahead        | Repositories with commits not pushed to remote   |
| Behind       | Repositories with commits not pulled from remote |

This makes it easy to identify repositories that need attention without checking them individually.

---

## 🧠 What does "Dirty" mean?

A repository is considered **dirty** when its working tree contains changes that haven't been fully committed.

This can include:

* Modified files
* Staged files
* Untracked files

`dev-snap` also considers repositories with unpushed commits when reporting repositories that need attention.

---

## ⚡ Performance

Scanning a workspace can involve checking many repositories.

To keep the process responsive, `dev-snap` uses parallel workers to analyze repositories concurrently.

This allows multiple Git repositories to be inspected without waiting for each repository to be processed completely before moving to the next one.

---

## 🏗️ Project Structure

```text
dev-snap/
│
├── dev_snap/
│   ├── __init__.py
│   └── main.py
│
├── tests/
│   └── test_scanner.py
│
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🧪 Testing

Run the test suite with:

```bash
pytest
```

The tests cover core repository-scanning functionality.

---

## 🛠️ Tech Stack

`dev-snap` is built with:

* **Python** — core language
* **Typer** — command-line interface
* **Rich** — terminal formatting and dashboard UI
* **Git** — repository information
* **pytest** — testing
* **ThreadPoolExecutor** — parallel repository scanning

---

## 🎯 Why dev-snap?

Managing multiple coding projects often means repeatedly running commands like:

```bash
git status
git branch
git log
git fetch
```

across different directories.

`dev-snap` provides a single high-level view of your Git workspace.

Instead of asking:

> "Which project did I leave with uncommitted changes?"

you can simply run:

```bash
dev-snap C:\Users\alden
```

and get the answer immediately.

---

## 🔮 Future Ideas

Possible future improvements include:

* Remote fetch / stale repository warnings
* More advanced filtering
* Configurable scan depth
* Custom output formats
* Repository grouping
* Configuration file support
* Improved remote tracking information
* Packaging and publishing to PyPI
* Additional automated tests

---

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.

### Development setup

Clone the repository:

```bash
git clone https://github.com/alden-p642/dev-snap.git
cd dev-snap
```

Install in editable mode:

```bash
pip install -e .
```

Run tests:

```bash
pytest
```

Make your changes, add tests where appropriate, and submit a pull request.

---

## 📜 License

This project is open source. See the repository for licensing information.

---

## 👨‍💻 Author

**Alden S Paul**

GitHub:
https://github.com/alden-p642

Project:
https://github.com/alden-p642/dev-snap

---

⭐ If you find `dev-snap` useful, consider giving the repository a star!
