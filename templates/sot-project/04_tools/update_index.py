#!/usr/bin/env python3
"""update_index.py — regenerate INDEX.md and MANIFEST.json (rule R7).

Usage (run from anywhere; repo root is auto-detected as this script's
grandparent directory, or pass it explicitly):

    python3 04_tools/update_index.py                # regenerate INDEX + MANIFEST
    python3 04_tools/update_index.py --diff         # diff repo vs MANIFEST, change nothing
    python3 04_tools/update_index.py --hash         # regenerate, recording sha256 per file
    python3 04_tools/update_index.py --diff --hash  # diff by content, ignoring mtime churn
    python3 04_tools/update_index.py /path/to/repo [--diff] [--hash]
    python3 04_tools/update_index.py --name "Project name"

Behavior:
- Walks the whole repo, skipping _to_delete/, hidden files (.DS_Store etc.),
  and sync-client artifacts.
- MANIFEST.json: {"generated": iso-ts, "project": name,
  "files": [{"path","size","mtime"[,"sha256"]}]}.
- INDEX.md: one line per file, grouped by top-level directory. One-line
  descriptions are PRESERVED across regenerations — edit them in INDEX.md and
  they survive; new files get an empty description to be filled in.
- --diff: prints NEW / CHANGED / MISSING files relative to MANIFEST.json and
  exits 1 if anything differs (0 if clean). Used by the session-start scan.
- --hash: use sha256 instead of size+mtime as the change signal. A cloud sync
  client can rewrite mtimes without the content changing, which makes a plain
  --diff noisy; --hash is immune to that, at the cost of reading every file.
  A manifest written with --hash can still be diffed without it, and vice
  versa — the comparison falls back to size+mtime when either side lacks a
  hash, so the flag can be adopted or dropped at any time.

Project-agnostic: the project name comes from --name, else from the first
heading of 00_AI_context/PROJECT.md, else from the repository folder name.
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

SKIP_DIRS = {"_to_delete", ".git"}
SKIP_FILES = {".DS_Store", "Icon\r", "desktop.ini", "Thumbs.db"}
# Generated meta-files exclude themselves — otherwise every regeneration
# changes their mtimes and the next --diff is never clean.
SKIP_PATHS = {"00_AI_context/INDEX.md", "00_AI_context/MANIFEST.json"}


def find_root(argv):
    skip_next = False
    for a in argv[1:]:
        if skip_next:
            skip_next = False
            continue
        if a == "--name":
            skip_next = True
            continue
        if not a.startswith("-"):
            return os.path.abspath(a)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_name(argv, root):
    if "--name" in argv:
        i = argv.index("--name")
        if i + 1 < len(argv):
            return argv[i + 1]
    p = os.path.join(root, "00_AI_context", "PROJECT.md")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            first = f.readline().strip()
        m = re.match(r"^#\s*(?:PROJECT\.md\s*[—–-]\s*)?(.+?)\s*$", first)
        if m and m.group(1):
            return m.group(1)
    return os.path.basename(root.rstrip("/")) or "project"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(root, with_hash=False):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
        )
        for fn in sorted(filenames):
            if fn in SKIP_FILES or fn.startswith("~$") or fn.startswith("."):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            if rel in SKIP_PATHS:
                continue
            if not os.path.isfile(full):
                continue
            st = os.stat(full)
            rec = {"path": rel, "size": st.st_size, "mtime": round(st.st_mtime, 2)}
            if with_hash:
                rec["sha256"] = sha256(full)
            out.append(rec)
    return out


def load_manifest(root):
    p = os.path.join(root, "00_AI_context", "MANIFEST.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def differs(a, b):
    """True if two records describe different content.

    Compare by sha256 when both sides carry one; otherwise fall back to
    size + mtime. Size always counts: a changed size is a changed file even
    if one side was recorded without a hash.
    """
    if a["size"] != b["size"]:
        return True
    if "sha256" in a and "sha256" in b:
        return a["sha256"] != b["sha256"]
    return a["mtime"] != b["mtime"]


def diff(root, with_hash=False):
    manifest = load_manifest(root)
    if manifest is None:
        print("No MANIFEST.json baseline — run without --diff to create one.")
        return 1
    old = {f["path"]: f for f in manifest["files"]}
    baseline_hashed = any("sha256" in f for f in old.values())
    new = {f["path"]: f for f in walk(root, with_hash or baseline_hashed)}
    added = sorted(set(new) - set(old))
    missing = sorted(set(old) - set(new))
    changed = sorted(p for p in set(old) & set(new) if differs(old[p], new[p]))
    for p in added:
        print(f"NEW      {p}")
    for p in changed:
        print(f"CHANGED  {p}")
    for p in missing:
        print(f"MISSING  {p}")
    if not (added or changed or missing):
        print(f"Clean — {len(new)} files match the manifest "
              f"(baseline {manifest.get('generated', '?')}).")
        return 0
    print(f"\n{len(added)} new, {len(changed)} changed, {len(missing)} missing.")
    return 1


def load_descriptions(root):
    """Parse existing INDEX.md lines of the form `- `path` — description`."""
    p = os.path.join(root, "00_AI_context", "INDEX.md")
    desc = {}
    if not os.path.exists(p):
        return desc
    pat = re.compile(r"^- `([^`]+)`(?: — (.*))?$")
    with open(p, encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.rstrip("\n"))
            if m and m.group(2):
                desc[m.group(1)] = m.group(2).strip()
    return desc


def regenerate(root, name, with_hash=False):
    files = walk(root, with_hash)
    desc = load_descriptions(root)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    ctx = os.path.join(root, "00_AI_context")
    os.makedirs(ctx, exist_ok=True)
    with open(os.path.join(ctx, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump({"generated": ts, "project": name, "files": files}, f, indent=1)

    groups = {}
    for fi in files:
        top = fi["path"].split("/")[0] if "/" in fi["path"] else "(root)"
        groups.setdefault(top, []).append(fi)

    lines = [
        f"# INDEX — {name}",
        "",
        f"Generated {ts} by `04_tools/update_index.py`. "
        f"{len(files)} files. Edit the one-line descriptions freely — they are "
        "preserved across regenerations.",
        "",
    ]
    order = sorted(groups, key=lambda k: ("" if k == "(root)" else k))
    for g in order:
        lines.append(f"## {g}")
        lines.append("")
        for fi in groups[g]:
            d = desc.get(fi["path"], "")
            lines.append(f"- `{fi['path']}`" + (f" — {d}" if d else " — "))
        lines.append("")
    with open(os.path.join(ctx, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"INDEX.md and MANIFEST.json regenerated — {len(files)} files"
          f"{' (hashed)' if with_hash else ''}.")
    return 0


if __name__ == "__main__":
    root = find_root(sys.argv)
    if not os.path.isdir(root):
        sys.exit(f"Repo root not found: {root}")
    use_hash = "--hash" in sys.argv
    if "--diff" in sys.argv:
        sys.exit(diff(root, use_hash))
    sys.exit(regenerate(root, find_name(sys.argv, root), use_hash))
