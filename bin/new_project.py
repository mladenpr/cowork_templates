#!/usr/bin/env python3
"""new_project.py — instantiate a cowork template into a new folder.

    python3 bin/new_project.py ~/OneDrive/01_PROJECTS/ACME-Bridge-Cowork \
        --name "ACME Bridge" --client "ACME Infrastructure" --owner "Jane Doe"

    python3 bin/new_project.py ~/OneDrive/01_PROJECTS/Quay-Wall \
        --template cowork-contractor --name "Quay Wall"

What it does:
1. Copies `templates/<template>/` to the destination, creating the empty
   working directories. Repository scaffolding is dropped on the way through:
   `.gitkeep` markers exist only so git tracks empty folders here, and
   `VERSION` only so this script knows what to stamp.
2. Substitutes the template placeholders in every text file.
3. Runs `04_tools/update_index.py` in the new folder to write the first
   INDEX.md / MANIFEST.json baseline.

Placeholders substituted: {{PROJECT_NAME}}, {{PROJECT_FOLDER}}, {{CLIENT}},
{{OWNER}}, {{DATE}}, {{CLIENT_SUFFIX}}, {{TEMPLATE_VERSION}}.

Each template carries its own `VERSION`, because the templates are versioned
independently — a fix to one must not renumber the other. That version is
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
TEMPLATES = os.path.join(ROOT, "templates")
DEFAULT_TEMPLATE = "cowork-consultant"
ROOT_VERSION_FILE = os.path.join(ROOT, "VERSION")
TEXT_EXT = {".md", ".py", ".json", ".txt", ".csv", ".yml", ".yaml", ".toml", ".cfg"}
# Files that serve this repository rather than the projects it creates.
SCAFFOLDING = {".gitkeep", "VERSION"}


def available():
    try:
        return sorted(d for d in os.listdir(TEMPLATES)
                      if not d.startswith(".")
                      and os.path.isdir(os.path.join(TEMPLATES, d)))
    except OSError:
        return []


def read_version(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def template_version(template_dir):
    """A template's own VERSION, falling back to the repository's."""
    return (read_version(os.path.join(template_dir, "VERSION"))
            or read_version(ROOT_VERSION_FILE)
            or "unknown")


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
        description="Instantiate a cowork template into a new folder.")
    ap.add_argument("dest", help="destination folder for the new project")
    ap.add_argument("--template", default=DEFAULT_TEMPLATE,
                    help=f"template to instantiate (default: {DEFAULT_TEMPLATE}); "
                         f"available: {', '.join(available()) or 'none'}")
    ap.add_argument("--name", help="project name (default: destination folder name)")
    ap.add_argument("--client", default="", help="client or counterparty")
    ap.add_argument("--owner", default="", help="who owns the work")
    ap.add_argument("--date", default=date.today().isoformat(),
                    help="start date, ISO (default: today)")
    ap.add_argument("--force", action="store_true",
                    help="allow writing into an existing non-empty folder")
    ap.add_argument("--version", action="version",
                    version=f"cowork_templates v{read_version(ROOT_VERSION_FILE)}")
    args = ap.parse_args()

    if args.template not in available():
        sys.exit(f"Unknown template: {args.template}\n"
                 f"Available: {', '.join(available()) or 'none'}")
    template = os.path.join(TEMPLATES, args.template)

    dest = os.path.abspath(os.path.expanduser(args.dest))
    folder = os.path.basename(dest.rstrip(os.sep))
    if os.path.exists(dest) and os.listdir(dest) and not args.force:
        sys.exit(f"Destination exists and is not empty: {dest}\n"
                 f"Pass --force to write into it anyway.")

    name = args.name or folder
    version = template_version(template)
    mapping = {
        "{{TEMPLATE_VERSION}}": version,
        "{{PROJECT_NAME}}": name,
        "{{PROJECT_FOLDER}}": folder,
        "{{CLIENT}}": args.client or "_TBC_",
        "{{OWNER}}": args.owner or "_TBC_",
        "{{DATE}}": args.date,
        "{{CLIENT_SUFFIX}}": f" — for {args.client}" if args.client else "",
    }

    shutil.copytree(template, dest, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))

    for dirpath, dirnames, filenames in os.walk(dest):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if fn in SCAFFOLDING:
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

    print(f"\nProject created: {dest}  ({args.template} v{version})")
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
