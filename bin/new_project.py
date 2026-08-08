#!/usr/bin/env python3
"""new_project.py — instantiate the cowork-project template into a new folder.

    python3 bin/new_project.py ~/OneDrive/01_PROJECTS/ACME-Bridge-Cowork \
        --name "ACME Bridge" --client "ACME Infrastructure" --owner "Jane Doe"

What it does:
1. Copies `templates/cowork-project/` to the destination, creating the empty
   working directories (`.gitkeep` markers are dropped — they exist only so
   git tracks the empty folders in this repository).
2. Substitutes the template placeholders in every text file.
3. Runs `04_tools/update_index.py` in the new folder to write the first
   INDEX.md / MANIFEST.json baseline.

Placeholders substituted: {{PROJECT_NAME}}, {{PROJECT_FOLDER}}, {{CLIENT}},
{{OWNER}}, {{DATE}}, {{CLIENT_SUFFIX}}, {{TEMPLATE_VERSION}}.

The template version is read from the VERSION file at the repository root and
stamped into the new project's README footer and its first WORKLOG entry. A
project is a copy, not a link: nothing propagates once it is created, so the
stamp is the only record of which rules and tooling it has.

Put the destination inside a synced cloud drive, and do NOT `git init` in it
(rule R9) — the sync client and git fight over the object store.
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(ROOT, "templates", "cowork-project")
VERSION_FILE = os.path.join(ROOT, "VERSION")
TEXT_EXT = {".md", ".py", ".json", ".txt", ".csv", ".yml", ".yaml", ".toml", ".cfg"}


def template_version():
    try:
        with open(VERSION_FILE, encoding="utf-8") as f:
            return f.read().strip() or "unknown"
    except OSError:
        return "unknown"


def substitute(path, mapping):
    with open(path, encoding="utf-8") as f:
        original = f.read()
    text = original
    for key, value in mapping.items():
        text = text.replace(key, value)
    if text != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


def main():
    ap = argparse.ArgumentParser(
        description="Instantiate the cowork-project template into a new folder.")
    ap.add_argument("dest", help="destination folder for the new project")
    ap.add_argument("--name", help="project name (default: destination folder name)")
    ap.add_argument("--client", default="", help="client or counterparty")
    ap.add_argument("--owner", default="", help="who owns the work")
    ap.add_argument("--date", default=date.today().isoformat(),
                    help="start date, ISO (default: today)")
    ap.add_argument("--force", action="store_true",
                    help="allow writing into an existing non-empty folder")
    ap.add_argument("--version", action="version",
                    version=f"cowork-project template v{template_version()}")
    args = ap.parse_args()

    if not os.path.isdir(TEMPLATE):
        sys.exit(f"Template not found: {TEMPLATE}")

    dest = os.path.abspath(os.path.expanduser(args.dest))
    folder = os.path.basename(dest.rstrip(os.sep))
    if os.path.exists(dest) and os.listdir(dest) and not args.force:
        sys.exit(f"Destination exists and is not empty: {dest}\n"
                 f"Pass --force to write into it anyway.")

    name = args.name or folder
    version = template_version()
    mapping = {
        "{{TEMPLATE_VERSION}}": version,
        "{{PROJECT_NAME}}": name,
        "{{PROJECT_FOLDER}}": folder,
        "{{CLIENT}}": args.client or "_TBC_",
        "{{OWNER}}": args.owner or "_TBC_",
        "{{DATE}}": args.date,
        "{{CLIENT_SUFFIX}}": f" — for {args.client}" if args.client else "",
    }

    shutil.copytree(TEMPLATE, dest, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))

    for dirpath, dirnames, filenames in os.walk(dest):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if fn == ".gitkeep":
                os.remove(full)
                continue
            if os.path.splitext(fn)[1].lower() in TEXT_EXT:
                substitute(full, mapping)

    index = os.path.join(dest, "04_tools", "update_index.py")
    for script in ("update_index.py", "extract_text.py"):
        path = os.path.join(dest, "04_tools", script)
        if os.path.exists(path):
            os.chmod(path, 0o755)
    subprocess.run([sys.executable, index, dest, "--name", name, "--hash"],
                   check=True)

    print(f"\nProject created: {dest}  (template v{version})")
    print("Next:")
    print("  1. Pin the folder for offline availability in your sync client (R9).")
    print("  2. File what you already have: reference material into 01_basis/,")
    print("     anything another party sent you into 02_exchange/received/.")
    print("  3. Run 04_tools/extract_text.py to build the searchable text layer")
    print("     (PDFs also need `pip install pypdf`).")
    print("  4. Open a Cowork session on the folder and say: "
          "'read CLAUDE.md and run the session-start scan'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
