#!/usr/bin/env python3
"""update_index.py — regenerate INDEX.md and MANIFEST.json (rule R7).

Usage (run from anywhere; repo root is auto-detected as this script's
grandparent directory, or pass it explicitly):

    python3 04_tools/update_index.py                # regenerate INDEX + MANIFEST
    python3 04_tools/update_index.py --diff         # diff repo vs MANIFEST, change nothing
    python3 04_tools/update_index.py --hash         # regenerate, recording sha256 per file
    python3 04_tools/update_index.py --diff --hash  # diff by content, ignoring mtime churn
    python3 04_tools/update_index.py --rehash       # recompute every hash from scratch
    python3 04_tools/update_index.py --no-hash      # drop back to size+mtime
    python3 04_tools/update_index.py /path/to/repo [--diff] [--hash]
    python3 04_tools/update_index.py --name "Project name"

On Windows use `py -3` in place of `python3`.

Behavior:
- Walks the whole repo, skipping _to_delete/, hidden files, and the temporary
  files Office and the sync client leave behind (see SKIP_* below).
- MANIFEST.json: {"generated": iso-ts, "project": name,
  "files": [{"path","size","mtime"[,"sha256"]}]}.
- INDEX.md: one line per file, grouped by top-level directory. One-line
  descriptions are PRESERVED across regenerations — edit them in INDEX.md and
  they survive; new files get an empty description to be filled in.
- --diff: prints NEW / CHANGED / MISSING files relative to MANIFEST.json and
  exits 1 if anything differs (0 if clean). Used by the session-start scan.
- Both modes also print WARNINGS: suspected sync-conflict copies, and names
  OneDrive/SharePoint will refuse to sync. Warnings never change the exit code
  on their own — they are for the human to resolve.

Hashing:
- --hash records sha256 per file and uses it as the change signal instead of
  size+mtime. A sync client rewrites mtimes when it hydrates a file or resolves
  a conflict, which makes a plain --diff noisy; sha256 is immune to that.
- Hashing is STICKY. Once a manifest carries hashes, every later regeneration
  keeps hashing without needing the flag again. Pass --no-hash to deliberately
  drop back to size+mtime.
- Hashes are reused from the manifest when a file's size AND mtime both match
  the baseline, so a scan only reads the bytes of files that actually look
  touched. Pass --rehash to recompute everything (the honest-but-slow mode:
  it also catches content edited in place with the mtime preserved).
- A manifest written with hashes can still be diffed without them, and vice
  versa — the comparison falls back to size+mtime when either side lacks a
  hash, so the flag can be adopted or dropped at any time.

Project-agnostic: the project name comes from --name, else from the first
heading of 00_AI_context/PROJECT.md, else from the repository folder name.
"""

import argparse
import hashlib
import json
import os
import platform
import re
import sys
from datetime import datetime, timezone

SKIP_DIRS = {"_to_delete", ".git"}
SKIP_FILES = {".DS_Store", "Icon\r", "desktop.ini", "Thumbs.db"}
# Office leaves owner-lock files (~$name.docx) and save-temps (~WRL0001.tmp)
# behind; LibreOffice leaves .~lock.name#. None of them are project content,
# and all of them would otherwise be reported NEW and ingested into 01_SoT.
SKIP_PREFIXES = ("~", ".~lock.")
SKIP_SUFFIXES = (".tmp", ".laccdb", ".partial", ".crdownload")
# Generated meta-files exclude themselves — otherwise every regeneration
# changes their mtimes and the next --diff is never clean.
SKIP_PATHS = {"00_AI_context/INDEX.md", "00_AI_context/MANIFEST.json"}

# Names SharePoint/OneDrive refuse to sync. Characters first, then the
# reserved device names inherited from DOS, then structural rules.
BAD_CHARS = set('"*:<>?/\\|')
RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", "LPT0", "COM0"} | {
    f"{p}{i}" for p in ("COM", "LPT") for i in range(1, 10)
}
# OneDrive's limit is 400 characters for the entire item URL, which includes
# the sync root we cannot see from here. Warn early enough to leave headroom.
MAX_REL_PATH = 300

CONFLICT_PATTERNS = [
    (re.compile(r"conflicted copy", re.I), "Dropbox conflict copy"),
    (re.compile(r"\(conflicted\)", re.I), "sync conflict copy"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def skipped(fn):
    if fn in SKIP_FILES or fn.startswith("."):
        return True
    if fn.startswith(SKIP_PREFIXES):
        return True
    return fn.lower().endswith(SKIP_SUFFIXES)


def walk(root, with_hash=False, baseline=None, rehash=False):
    """Collect one record per file. Reuses baseline hashes where it safely can.

    A baseline hash is reused only when size and mtime both match, so mtime
    churn still forces a real read and a real comparison. --rehash disables the
    reuse entirely.
    """
    baseline = baseline or {}
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
        )
        for fn in sorted(filenames):
            if skipped(fn):
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
                prev = baseline.get(rel)
                reusable = (
                    not rehash
                    and prev
                    and "sha256" in prev
                    and prev["size"] == rec["size"]
                    and prev["mtime"] == rec["mtime"]
                )
                rec["sha256"] = prev["sha256"] if reusable else sha256(full)
            out.append(rec)
    return out


def load_manifest(root):
    p = os.path.join(root, "00_AI_context", "MANIFEST.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def baseline_files(manifest):
    return {f["path"]: f for f in manifest["files"]} if manifest else {}


def resolve_hashing(args, baseline):
    """Hashing is sticky: a hashed baseline keeps hashing unless --no-hash."""
    if args.no_hash:
        return False
    if args.hash or args.rehash:
        return True
    return any("sha256" in f for f in baseline.values())


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


def conflict_reason(rel, device):
    """Name looks like a sync-conflict copy rather than a real input.

    OneDrive names a conflict copy `<stem>-<ComputerName>.<ext>`, so the
    machine name is the reliable signal; the rest are other clients' habits.
    A numbered duplicate is reported too, more quietly — it is usually a
    re-upload of the same document, and occasionally a legitimate name.
    """
    stem = os.path.splitext(os.path.basename(rel))[0]
    for pat, label in CONFLICT_PATTERNS:
        if pat.search(stem):
            return label
    if device and re.search(rf"-{re.escape(device)}(\s*\(\d+\))?$", stem, re.I):
        return f"OneDrive conflict copy (device '{device}')"
    if re.search(r"\s\(\d+\)$", stem):
        return "possible duplicate copy"
    return None


def name_problem(rel):
    """Name or path SharePoint/OneDrive will refuse to sync."""
    if len(rel) > MAX_REL_PATH:
        return f"path is {len(rel)} chars — near OneDrive's 400-char URL limit"
    for part in rel.split("/"):
        bad = sorted(BAD_CHARS & set(part))
        if bad:
            return f"illegal character(s) {' '.join(bad)} in '{part}'"
        if part != part.strip() or part.endswith("."):
            return f"leading/trailing space or trailing dot in '{part}'"
        if os.path.splitext(part)[0].upper() in RESERVED_NAMES:
            return f"'{part}' is a reserved device name"
        if "_vti_" in part.lower():
            return f"'_vti_' is reserved by SharePoint in '{part}'"
    return None


def warnings_for(paths, device):
    conflicts, names = [], []
    for rel in sorted(paths):
        reason = conflict_reason(rel, device)
        if reason:
            conflicts.append((rel, reason))
        problem = name_problem(rel)
        if problem:
            names.append((rel, problem))
    return conflicts, names


def print_warnings(conflicts, names):
    if conflicts:
        print("\nSuspected sync-conflict copies — do NOT ingest into 01_SoT "
              "until you have decided which copy is real:")
        for rel, reason in conflicts:
            print(f"  CONFLICT? {rel}  ({reason})")
    if names:
        print("\nNames OneDrive/SharePoint will refuse to sync:")
        for rel, problem in names:
            print(f"  BAD NAME  {rel}  ({problem})")
    if conflicts or names:
        print("\nWarnings do not affect the exit code — they are yours to "
              "resolve, not the session's (R8).")


def diff(root, args):
    manifest = load_manifest(root)
    if manifest is None:
        print("No MANIFEST.json baseline — run without --diff to create one.")
        return 1
    old = baseline_files(manifest)
    with_hash = resolve_hashing(args, old)
    new = {f["path"]: f
           for f in walk(root, with_hash, old, args.rehash)}
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
              f"(baseline {manifest.get('generated', '?')}"
              f"{', hashed' if with_hash else ''}).")
    else:
        print(f"\n{len(added)} new, {len(changed)} changed, {len(missing)} missing.")
    print_warnings(*warnings_for(new, args.device))
    return 0 if not (added or changed or missing) else 1


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


def find_name(args, root):
    if args.name:
        return args.name
    p = os.path.join(root, "00_AI_context", "PROJECT.md")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            first = f.readline().strip()
        m = re.match(r"^#\s*(?:PROJECT\.md\s*[—–-]\s*)?(.+?)\s*$", first)
        if m and m.group(1):
            return m.group(1)
    return os.path.basename(root.rstrip("/")) or "project"


def regenerate(root, name, args):
    old = baseline_files(load_manifest(root))
    with_hash = resolve_hashing(args, old)
    files = walk(root, with_hash, old, args.rehash)
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
    print_warnings(*warnings_for({f["path"] for f in files}, args.device))
    return 0


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description="Regenerate INDEX.md and MANIFEST.json, or diff against them.")
    ap.add_argument("root", nargs="?", help="repo root (default: this script's parent's parent)")
    ap.add_argument("--diff", action="store_true",
                    help="report NEW/CHANGED/MISSING and change nothing; exit 1 if dirty")
    ap.add_argument("--name", help="project name for the INDEX heading")
    ap.add_argument("--hash", action="store_true",
                    help="record sha256 per file and compare by content")
    ap.add_argument("--no-hash", action="store_true",
                    help="drop a hashed manifest back to size+mtime")
    ap.add_argument("--rehash", action="store_true",
                    help="recompute every hash instead of reusing unchanged ones")
    ap.add_argument("--device", default=platform.node().split(".")[0],
                    help="computer name used to spot OneDrive conflict copies "
                         "(default: this machine's)")
    args = ap.parse_args(argv)
    if args.hash and args.no_hash:
        ap.error("--hash and --no-hash are mutually exclusive")
    return args


if __name__ == "__main__":
    args = parse_args()
    root = (os.path.abspath(os.path.expanduser(args.root)) if args.root
            else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.isdir(root):
        sys.exit(f"Repo root not found: {root}")
    if args.diff:
        sys.exit(diff(root, args))
    sys.exit(regenerate(root, find_name(args, root), args))
