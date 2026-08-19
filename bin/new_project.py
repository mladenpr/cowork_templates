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
3. Writes `00_AI_context/TEMPLATE.json` — the machine-readable stamp: which
   template, which version, the placeholder values substituted, and a content
   hash of every scaffolding file as instantiated (CLAUDE.md, README.md, the
   tools scripts, the `_TEMPLATE.md` stubs). `bin/upgrade_project.py` reads it
   to tell, later, which scaffolding files were locally edited and which are
   safe to replace.
4. Runs the template's `update_index.py` in the new folder to write the first
   INDEX.md / MANIFEST.json baseline.

Templates number their zones differently — the tools directory is `04_tools/`
in one and `05_tools/` in another — so it is discovered rather than assumed.
A template that renumbers its zones needs no change here.

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
import hashlib
import json
import os
import re
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


def tools_dir(dest):
    """The template's numbered tools directory, whatever it is numbered.

    Zone numbering differs between templates and will differ again; hardcoding
    `04_tools` here would break a template silently, after the copy, with a
    half-written project on disk.
    """
    pattern = re.compile(r"^\d\d_tools$")
    for entry in sorted(os.listdir(dest)):
        if pattern.match(entry) and os.path.isdir(os.path.join(dest, entry)):
            return entry
    return None


def frozen_zones(dest):
    """The numbered zones that hold filed material, for the closing hint.

    Derived rather than listed, because the zones differ per template and a
    hardcoded list would go stale silently — printing advice about a directory
    the project does not have.
    """
    skip = re.compile(r"^\d\d_(AI_context|working|tools|temp)$")
    return [d for d in sorted(os.listdir(dest))
            if re.match(r"^\d\d_", d) and not skip.match(d)
            and os.path.isdir(os.path.join(dest, d))]


def scaffolding_files(root):
    """Relative paths (with '/') of the files the template owns in a project.

    Scaffolding is what an upgrade may later act on: the session bootstrap,
    the rules, the tools scripts and the context-file stubs. Everything else
    a template ships is seed material that becomes project state the moment
    the project exists. `upgrade_project.py` applies the same rule; the
    regression tests pin the two to each other.
    """
    tools = re.compile(r"^\d\d_tools$")
    out = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), root)
            rel = rel.replace(os.sep, "/")
            if rel in ("CLAUDE.md", "README.md") or fn == "_TEMPLATE.md" \
                    or tools.match(rel.split("/", 1)[0]):
                out.add(rel)
    return out


def write_stamp(dest, template_name, version, mapping):
    """00_AI_context/TEMPLATE.json — the machine-readable version stamp."""
    hashes = {}
    for rel in sorted(scaffolding_files(dest)):
        with open(os.path.join(dest, rel.replace("/", os.sep)), "rb") as f:
            hashes[rel] = hashlib.sha256(f.read()).hexdigest()
    stamp = {
        "_comment": ("Template stamp — written by new_project.py, updated by "
                     "upgrade_project.py. Records which template version this "
                     "project's scaffolding carries, the placeholder values "
                     "substituted at creation, and the sha256 of each "
                     "scaffolding file as tooling last wrote it (null = "
                     "unknown; treated as locally modified). Do not edit."),
        "template": template_name,
        "version": version,
        "created": {"version": version, "date": mapping["{{DATE}}"]},
        "mapping": {k.strip("{}"): v for k, v in mapping.items()
                    if k != "{{TEMPLATE_VERSION}}"},
        "scaffolding": hashes,
        "upgrades": [],
    }
    path = os.path.join(dest, "00_AI_context", "TEMPLATE.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stamp, f, indent=2)
        f.write("\n")


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

    write_stamp(dest, args.template, version, mapping)

    tools = tools_dir(dest)
    if not tools:
        sys.exit(f"Template '{args.template}' has no NN_tools directory — "
                 f"cannot generate the first index. Project written to {dest}.")
    for script in sorted(os.listdir(os.path.join(dest, tools))):
        if script.endswith(".py"):
            os.chmod(os.path.join(dest, tools, script), 0o755)
    index = os.path.join(dest, tools, "update_index.py")
    subprocess.run([sys.executable, index, dest, "--name", name, "--hash"],
                   check=True)

    inbox = os.path.isdir(os.path.join(dest, "_inbox"))
    print(f"\nProject created: {dest}  ({args.template} v{version})")
    print("Next:")
    print("  1. Pin the folder for offline availability in your sync client (R9).")
    if inbox:
        print("  2. Drop what you already have into _inbox/, then open a session")
        print("     and ask it to clear the inbox — it files by the rules in")
        print("     README.md rather than by guesswork.")
    else:
        zones = frozen_zones(dest)
        print(f"  2. File what you already have into the frozen zones "
              f"({', '.join(z + '/' for z in zones)}) —")
        print("     README.md says which material belongs in which.")
    print(f"  3. Run {tools}/extract_text.py to build the searchable text layer")
    print("     (PDFs also need `pip install pypdf`).")
    print("  4. Open a Cowork session on the folder and say: "
          "'read CLAUDE.md and run the session-start scan'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
