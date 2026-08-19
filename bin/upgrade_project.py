#!/usr/bin/env python3
"""upgrade_project.py — bring a project's scaffolding up to the toolbox's version.

    python3 bin/upgrade_project.py ~/OneDrive/01_PROJECTS/ACME-Bridge-Cowork
    python3 bin/upgrade_project.py ~/OneDrive/01_PROJECTS/ACME-Bridge-Cowork --dry-run

A project is a copy, not a link — nothing propagates from the template by
itself. This tool is the explicit step that propagates, and it acts on the
scaffolding and nothing else. Scaffolding means the files the template owns
and a project merely carries:

    CLAUDE.md                 the session bootstrap
    README.md                 the schema and the working rules
    NN_tools/*                the scripts the template ships
    **/_TEMPLATE.md           the context-file stubs

Everything else — the frozen zones, the drafts, PROJECT.md, the index, the
logs, every document — is project work, and is never an upgrade candidate:
never rewritten, never moved, never staged for deletion. The record of an
applied upgrade is written where the rules put records: a dated entry
appended to WORKLOG.md, a line under the README footer, and the stamp in
TEMPLATE.json.

Within the scaffolding, what happens to a file depends on whether it has been
touched since the tooling last wrote it, which `00_AI_context/TEMPLATE.json`
records as a content hash:

- unmodified            → replaced with the new version, placeholders re-substituted
- locally edited        → left exactly as it is; the new version is written to
                          `NN_temp/template-upgrade-v<version>/` for review
- no longer shipped     → moved to `_to_delete/` if unmodified (R8 — nothing is
                          ever deleted), left in place if edited
- missing               → restored

Across a major version the tool refuses: a major bump means the schema or the
rules changed such that an existing project cannot simply adopt them, and a
live project may be better finished on the rules it started with. Below 1.0.0
the minor is the compatibility boundary and cross-minor is refused the same
way.

Projects created before TEMPLATE.json existed are adopted on the first run:
template and version are read from the README footer, and where the toolbox's
git history is available the tool still proves which files are unmodified.
Anything it cannot prove is proposed rather than replaced — the failure mode
is a review copy, never an overwrite.

Each applied upgrade updates the README footer, appends a dated WORKLOG entry,
and records itself in TEMPLATE.json. Run the session-start scan afterwards —
`NN_tools/update_index.py --diff` — read what it says, then rebuild the
baseline. The scan is deliberately not run for you: rebaselining would swallow
any change that happened to be pending in the project, including one in a
frozen zone.

COWORK_TEMPLATES_DIR overrides where templates are read from (used by the
regression tests; you should not need it).
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
TEMPLATES = os.environ.get("COWORK_TEMPLATES_DIR") or os.path.join(ROOT, "templates")
TOOLBOX = os.path.dirname(TEMPLATES)
ROOT_VERSION_FILE = os.path.join(ROOT, "VERSION")
TEXT_EXT = {".md", ".py", ".json", ".txt", ".csv", ".yml", ".yaml", ".toml", ".cfg"}
STAMP_REL = "00_AI_context/TEMPLATE.json"
PLACEHOLDER = re.compile(r"\{\{[A-Z_]+\}\}")
TOOLS_ZONE = re.compile(r"^\d\d_tools$")
TEMP_ZONE = re.compile(r"^\d\d_temp$")

# Templates this repository renamed. A project stamped with the old name is
# the same template and upgrades against the new one.
RENAMED = {"cowork-project": "cowork-consultant", "sot-project": "cowork-consultant"}


# --------------------------------------------------------------------------
# small shared pieces
# --------------------------------------------------------------------------

def read_version(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def template_version(template_dir):
    return (read_version(os.path.join(template_dir, "VERSION"))
            or read_version(ROOT_VERSION_FILE)
            or "unknown")


def parse_version(v):
    try:
        parts = tuple(int(x) for x in v.split("."))
    except ValueError:
        sys.exit(f"Cannot parse version {v!r} — expected N.N.N.")
    return parts + (0,) * (3 - len(parts))


def compat_key(v):
    """The part of a version that must match for scaffolding to be adoptable.

    Below 1.0.0 the minor is the boundary — this repository's own 0.x history
    changed a log schema between minors, exactly as semver allows.
    """
    return (0, v[1]) if v[0] == 0 else (v[0],)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    with open(path, "rb") as f:
        return sha256_bytes(f.read())


def scaffolding_files(template_dir):
    """Relative paths (with '/') of every scaffolding file the template ships."""
    out = set()
    for dirpath, dirnames, filenames in os.walk(template_dir):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
        for fn in filenames:
            if fn in (".gitkeep", "VERSION", ".DS_Store") or fn.endswith(".pyc"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), template_dir)
            rel = rel.replace(os.sep, "/")
            top = rel.split("/", 1)[0]
            if rel in ("CLAUDE.md", "README.md") or TOOLS_ZONE.match(top) \
                    or fn == "_TEMPLATE.md":
                out.add(rel)
    return out


def substitute(text, stamp):
    mapping = {"{{%s}}" % k: v for k, v in stamp["mapping"].items()}
    mapping["{{TEMPLATE_VERSION}}"] = stamp["created"]["version"]
    for key, value in mapping.items():
        text = text.replace(key, value)
    return text


def upgrade_footer_line(to_version, on_date):
    return (f"Upgraded to **v{to_version}** on {on_date} — scaffolding only, by "
            f"`upgrade_project.py`; the record is `{STAMP_REL}`.")


def render(template_dir, rel, stamp, history):
    """The bytes this tool would write for rel, and whether placeholders remain.

    history is the full upgrade history the project will have once this run
    applies, as (to_version, date) pairs — the README footer carries one line
    per upgrade, regenerated from the stamp so a wholesale replacement of
    README.md never loses them.
    """
    src = os.path.join(template_dir, rel.replace("/", os.sep))
    with open(src, "rb") as f:
        raw = f.read()
    if os.path.splitext(rel)[1].lower() not in TEXT_EXT:
        return raw, False
    text = substitute(raw.decode("utf-8"), stamp)
    if rel == "README.md":
        if not text.endswith("\n"):
            text += "\n"
        for to_version, on_date in history:
            text += "\n" + upgrade_footer_line(to_version, on_date) + "\n"
    return text.encode("utf-8"), bool(PLACEHOLDER.search(text))


def write_atomic(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".upgrade-tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


def find_zone(dest, pattern):
    for entry in sorted(os.listdir(dest)):
        if pattern.match(entry) and os.path.isdir(os.path.join(dest, entry)):
            return entry
    return None


def retire(dest, rel):
    """Move rel into _to_delete/ under a non-colliding name (R8)."""
    staging = os.path.join(dest, "_to_delete")
    os.makedirs(staging, exist_ok=True)
    base = os.path.basename(rel)
    stem, ext = os.path.splitext(base)
    candidate, i = base, 0
    while os.path.exists(os.path.join(staging, candidate)):
        i += 1
        candidate = f"{stem}-retired-{i}{ext}"
    shutil.move(os.path.join(dest, rel.replace("/", os.sep)),
                os.path.join(staging, candidate))
    return "_to_delete/" + candidate


# --------------------------------------------------------------------------
# the stamp: load it, or adopt a project that predates it
# --------------------------------------------------------------------------

def load_stamp(dest):
    path = os.path.join(dest, STAMP_REL.replace("/", os.sep))
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            stamp = json.load(f)
    except (OSError, ValueError) as e:
        sys.exit(f"Cannot read {STAMP_REL}: {e}\n"
                 f"Fix or remove it; removed, the project is re-adopted from "
                 f"its README footer.")
    for key in ("template", "version", "created", "mapping", "scaffolding"):
        if key not in stamp:
            sys.exit(f"{STAMP_REL} is missing {key!r} — not written by this "
                     f"tooling? Remove it to re-adopt from the README footer.")
    stamp.setdefault("upgrades", [])
    return stamp


def save_stamp(dest, stamp):
    ordered = {
        "_comment": ("Template stamp — written by new_project.py, updated by "
                     "upgrade_project.py. Records which template version this "
                     "project's scaffolding carries, the placeholder values "
                     "substituted at creation, and the sha256 of each "
                     "scaffolding file as tooling last wrote it (null = "
                     "unknown; treated as locally modified). Do not edit."),
    }
    for key in ("template", "version", "created", "adopted", "mapping",
                "scaffolding", "upgrades"):
        if key in stamp:
            ordered[key] = stamp[key]
    ordered["scaffolding"] = dict(sorted(ordered["scaffolding"].items()))
    write_atomic(os.path.join(dest, STAMP_REL.replace("/", os.sep)),
                 (json.dumps(ordered, indent=2) + "\n").encode("utf-8"))


def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def recover_stamp(dest, args):
    """Build a stamp for a project created before TEMPLATE.json existed.

    Everything is recovered from what the project itself says — the README
    footer, the WORKLOG's creation entry, the CLAUDE.md project line — with
    command-line overrides for anything it does not say. Recovery errs
    conservative: a wrong guess makes a file look modified, and a modified
    file is proposed rather than replaced.
    """
    readme = read_text(os.path.join(dest, "README.md"))
    worklog = read_text(os.path.join(dest, "00_AI_context", "WORKLOG.md"))
    claude = read_text(os.path.join(dest, "CLAUDE.md"))

    m = (re.search(r"Instantiated from the `([\w.-]+)` template \*\*v([\w.]+)\*\*",
                   readme)
         or re.search(r"instantiated from the `([\w.-]+)` template\s+\*\*v([\w.]+)\*\*",
                      worklog))
    template = args.template or (m and m.group(1))
    version = args.at_version or (m and m.group(2))
    if not template or not version:
        sys.exit(f"No {STAMP_REL} and no 'Instantiated from' stamp found in "
                 f"README.md or WORKLOG.md.\nPass --template and --at-version "
                 f"to say what this project was created from.")

    d = (re.search(r"^## (\d{4}-\d{2}-\d{2}) — Repository created", worklog, re.M)
         or re.search(r"\bon (\d{4}-\d{2}-\d{2})\.", readme))
    created_date = args.date or (d.group(1) if d else "")

    name, suffix = "", ""
    p = re.search(r"^Project: \*\*(.*?)\*\*(.*)$", claude, re.M)
    if p:
        name, suffix = p.group(1), p.group(2).rstrip()
    name = args.name or name or os.path.basename(dest.rstrip(os.sep))
    if suffix.startswith(" — for "):
        client = args.client or suffix[len(" — for "):]
        suffix = f" — for {client}"
    else:
        client = args.client or "_TBC_"
        if args.client:
            suffix = f" — for {client}"

    stamp = {
        "template": template,
        "version": version,
        "created": {"version": version, "date": created_date or "unknown"},
        "adopted": date.today().isoformat(),
        "mapping": {
            "PROJECT_NAME": name,
            "PROJECT_FOLDER": os.path.basename(dest.rstrip(os.sep)),
            "CLIENT": client,
            "OWNER": args.owner or "_TBC_",
            "DATE": created_date or "unknown",
            "CLIENT_SUFFIX": suffix,
        },
        "scaffolding": {},
        "upgrades": [],
    }
    return stamp


def historical_hashes(template_names, rel, stamp):
    """Normalized hashes of every version of rel the toolbox's history holds.

    Adoption has no recorded hash to compare against, but the toolbox is a git
    clone: if a project file matches *any* historical template version of
    itself (after substitution), it is unmodified scaffolding. No git, no
    match — and no match only means the file is treated as modified, which is
    the safe direction.
    """
    if not os.path.isdir(os.path.join(TOOLBOX, ".git")):
        return set()

    def git(*argv):
        proc = subprocess.run(["git", "-C", TOOLBOX, *argv],
                              capture_output=True, text=True)
        return proc.stdout if proc.returncode == 0 else ""

    hashes = set()
    for name in template_names:
        path = f"templates/{name}/{rel}"
        blobs = set()
        for commit in git("log", "--all", "--pretty=%H", "--", path).split():
            blob = git("rev-parse", f"{commit}:{path}").strip()
            if blob:
                blobs.add(blob)
        for blob in blobs:
            proc = subprocess.run(["git", "-C", TOOLBOX, "cat-file", "blob", blob],
                                  capture_output=True)
            if proc.returncode != 0:
                continue
            try:
                text = proc.stdout.decode("utf-8")
            except UnicodeDecodeError:
                hashes.add(sha256_bytes(proc.stdout))
                continue
            text = substitute(text, stamp)
            hashes.add(sha256_bytes(text.replace("\r\n", "\n").encode("utf-8")))
    return hashes


def normalized_file_hash(path):
    with open(path, "rb") as f:
        raw = f.read()
    try:
        return sha256_bytes(raw.decode("utf-8").replace("\r\n", "\n").encode("utf-8"))
    except UnicodeDecodeError:
        return sha256_bytes(raw)


def adopt_hashes(dest, stamp, considered):
    """Fill stamp['scaffolding'] for an adopted project: proven hash or None."""
    names = {stamp["template"]}
    names.update(old for old, new in RENAMED.items() if new == stamp["template"])
    proven = 0
    for rel in sorted(considered):
        full = os.path.join(dest, rel.replace("/", os.sep))
        if not os.path.isfile(full):
            continue
        if normalized_file_hash(full) in historical_hashes(names, rel, stamp):
            stamp["scaffolding"][rel] = sha256_file(full)
            proven += 1
        else:
            stamp["scaffolding"][rel] = None
    return proven


# --------------------------------------------------------------------------
# planning and applying
# --------------------------------------------------------------------------

def plan(dest, template_dir, stamp, history):
    """Decide, per scaffolding file, what this run would do. Reads only."""
    actions = []
    shipped = scaffolding_files(template_dir)
    recorded = stamp["scaffolding"]
    for rel in sorted(shipped | set(recorded)):
        full = os.path.join(dest, rel.replace("/", os.sep))
        exists = os.path.isfile(full)
        if rel in shipped:
            new_bytes, unresolved = render(template_dir, rel, stamp, history)
            if not exists:
                verb = "restore" if rel in recorded else "add"
                actions.append((verb, rel, new_bytes, None))
            elif unresolved:
                actions.append(("propose", rel, new_bytes,
                                "new version uses a placeholder this project "
                                "has no value for"))
            else:
                current = sha256_file(full)
                if current == sha256_bytes(new_bytes):
                    actions.append(("ok", rel, None, None))
                elif recorded.get(rel) == current:
                    actions.append(("replace", rel, new_bytes, None))
                else:
                    actions.append(("propose", rel, new_bytes, "locally modified"))
        else:
            if not exists:
                actions.append(("forget", rel, None, None))
            elif recorded.get(rel) == sha256_file(full):
                actions.append(("retire", rel, None, None))
            else:
                actions.append(("keep", rel, None,
                                "no longer shipped, and locally modified"))
    return actions


VERBS = {
    "replace": "replaced (unmodified scaffolding)",
    "add": "added (new in this version)",
    "restore": "restored (scaffolding file was missing)",
    "propose": "left alone; new version written for review",
    "retire": "moved to _to_delete/ (no longer shipped)",
    "keep": "left alone (no longer shipped, locally modified)",
    "ok": "already current",
    "forget": "no longer shipped; already gone",
}


def describe(actions, propose_dir):
    lines = []
    for verb, rel, _, note in actions:
        if verb == "forget":
            continue
        text = f"  {verb:<8} {rel}"
        if verb == "propose":
            text += f"  → {propose_dir}/{rel}" + (f"  ({note})" if note else "")
        elif note:
            text += f"  ({note})"
        lines.append(text)
    return lines


def worklog_entry(stamp, old_version, new_version, results, propose_dir):
    today = date.today().isoformat()
    lines = [f"## {today} — Template upgraded: `{stamp['template']}` "
             f"v{old_version} → v{new_version}", "",
             "- Scaffolding upgraded with the toolbox's `upgrade_project.py` — "
             "CLAUDE.md, README.md, the tools scripts and the `_TEMPLATE.md` "
             "stubs are the only candidates; documents, context files and logs "
             "are untouched by construction."]
    def bullet(label, rels):
        if rels:
            lines.append(f"- {label}: " + ", ".join(f"`{r}`" for r in rels) + ".")
    bullet("Replaced", results["replaced"])
    bullet("Added", results["added"])
    bullet(f"Proposed, not applied — locally modified; review copies in "
           f"`{propose_dir}/`", results["proposed"])
    bullet("Retired to `_to_delete/`", results["retired"])
    lines += ["", "---"]
    return "\n".join(lines)


def append_worklog(dest, entry):
    path = os.path.join(dest, "00_AI_context", "WORKLOG.md")
    if not os.path.isfile(path):
        return False
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not text.endswith("\n"):
        text += "\n"
    write_atomic(path, (text + "\n" + entry + "\n").encode("utf-8"))
    return True


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Bring a project's scaffolding up to the toolbox's "
                    "template version. Scaffolding only — project work is "
                    "never touched.")
    ap.add_argument("dest", help="the project folder to upgrade")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would happen; write nothing")
    ap.add_argument("--template",
                    help="adoption only: the template this project was created "
                         "from, when its README footer does not say")
    ap.add_argument("--at-version",
                    help="adoption only: the version it was created at, when "
                         "its README footer does not say")
    ap.add_argument("--name", help="adoption only: override the recovered project name")
    ap.add_argument("--client", help="adoption only: override the recovered client")
    ap.add_argument("--owner", help="adoption only: override the recovered owner")
    ap.add_argument("--date", help="adoption only: override the recovered start date")
    args = ap.parse_args()

    dest = os.path.abspath(os.path.expanduser(args.dest))
    if not os.path.isdir(dest):
        sys.exit(f"Not a directory: {dest}")
    if os.path.isdir(os.path.join(dest, "templates")) \
            and os.path.isfile(os.path.join(dest, "bin", "new_project.py")):
        sys.exit(f"{dest} looks like the cowork_templates toolbox, not a "
                 f"project. Point this tool at a project folder.")
    if not os.path.isfile(os.path.join(dest, "CLAUDE.md")) \
            and not os.path.isdir(os.path.join(dest, "00_AI_context")):
        sys.exit(f"{dest} does not look like a cowork project — no CLAUDE.md "
                 f"and no 00_AI_context/.")

    stamp = load_stamp(dest)
    adopted = stamp is None
    if adopted:
        stamp = recover_stamp(dest, args)
        print(f"No {STAMP_REL} — adopting this project from its own record:")
        print(f"  template {stamp['template']} v{stamp['version']}, created "
              f"{stamp['created']['date']}, project \"{stamp['mapping']['PROJECT_NAME']}\"")

    canonical = RENAMED.get(stamp["template"], stamp["template"])
    if canonical != stamp["template"]:
        print(f"  `{stamp['template']}` is now `{canonical}` — same template, renamed.")
        stamp["template"] = canonical

    template_dir = os.path.join(TEMPLATES, stamp["template"])
    if not os.path.isdir(template_dir):
        sys.exit(f"This toolbox has no template named {stamp['template']!r}.\n"
                 f"Available: "
                 f"{', '.join(sorted(os.listdir(TEMPLATES))) or 'none'}.")

    old_version = stamp["version"]
    new_version = template_version(template_dir)
    vo, vn = parse_version(old_version), parse_version(new_version)

    if vo > vn:
        sys.exit(f"Project is at {stamp['template']} v{old_version} but this "
                 f"toolbox has only v{new_version}.\nUpdate the toolbox first: "
                 f"git -C {ROOT} pull")
    if compat_key(vo) != compat_key(vn):
        boundary = "a major version" if vn[0] != 0 else "a pre-1.0 minor version"
        sys.exit(f"Refusing: {stamp['template']} v{old_version} → v{new_version} "
                 f"crosses {boundary}.\nThat bump means the schema or the rules "
                 f"changed such that an existing project cannot simply adopt "
                 f"them — upgrading is a hand migration (see CHANGELOG.md), and "
                 f"a live project may be better finished on the rules it "
                 f"started with.\nNothing was changed.")

    same_version = vo == vn
    considered = scaffolding_files(template_dir) | set(stamp["scaffolding"])
    if adopted:
        proven = adopt_hashes(dest, stamp, considered)
        unproven = sum(1 for v in stamp["scaffolding"].values() if v is None)
        print(f"  {proven} scaffolding file(s) proven unmodified against the "
              f"toolbox's git history; {unproven} could not be proven and will "
              f"be proposed, not replaced.")

    history = [(u["to"], u["date"]) for u in stamp["upgrades"]]
    if not same_version:
        history.append((new_version, date.today().isoformat()))

    actions = plan(dest, template_dir, stamp, history)
    temp_zone = find_zone(dest, TEMP_ZONE)
    propose_dir = ((temp_zone or "_to_delete") + f"/template-upgrade-v{new_version}")

    header = (f"{stamp['template']} v{old_version}"
              + ("" if same_version else f" → v{new_version}")
              + f"  ({dest})")
    print("\n" + header)
    lines = describe(actions, propose_dir)
    print("\n".join(lines) if lines else "  nothing to do")
    print("\nNothing outside the scaffolding is an upgrade candidate — "
          "documents, context files, logs and drafts stay as they are. An "
          "applied upgrade writes only its own record: a dated WORKLOG entry, "
          "the README footer line, TEMPLATE.json.")

    if args.dry_run:
        print("\nDry run — nothing was written.")
        return 0

    if same_version and not any(v in ("restore", "add") for v, *_ in actions):
        # Nothing to write in the project itself. The stamp may still need
        # saving: an adoption just happened, or a file proposed earlier has
        # since been merged by hand and now matches the template — record its
        # hash so the next real upgrade replaces it instead of re-proposing.
        changed = adopted
        for verb, rel, _, _ in actions:
            if verb != "ok":
                continue
            digest = sha256_file(os.path.join(dest, rel.replace("/", os.sep)))
            if stamp["scaffolding"].get(rel) != digest:
                stamp["scaffolding"][rel] = digest
                changed = True
        if changed:
            save_stamp(dest, stamp)
        print(f"\nAlready at v{new_version}; nothing to do.")
        return 0

    # Apply. Only these verbs write, and none of them writes outside the
    # scaffolding, the temp zone, _to_delete/, the stamp and the WORKLOG.
    results = {"replaced": [], "added": [], "proposed": [], "retired": []}
    for verb, rel, new_bytes, _ in actions:
        full = os.path.join(dest, rel.replace("/", os.sep))
        if verb in ("replace", "add", "restore"):
            write_atomic(full, new_bytes)
            if rel.endswith(".py") and TOOLS_ZONE.match(rel.split("/", 1)[0]):
                os.chmod(full, 0o755)
            stamp["scaffolding"][rel] = sha256_file(full)
            results["replaced" if verb == "replace" else "added"].append(rel)
        elif verb == "propose":
            target = os.path.join(dest, propose_dir.replace("/", os.sep),
                                  rel.replace("/", os.sep))
            write_atomic(target, new_bytes)
            results["proposed"].append(rel)
            stamp["scaffolding"].setdefault(rel, None)
        elif verb == "retire":
            retire(dest, rel)
            del stamp["scaffolding"][rel]
            results["retired"].append(rel)
        elif verb in ("keep", "forget"):
            stamp["scaffolding"].pop(rel, None)
        elif verb == "ok":
            stamp["scaffolding"][rel] = sha256_file(full)

    if not same_version:
        stamp["upgrades"].append({
            "date": date.today().isoformat(),
            "from": old_version,
            "to": new_version,
            **{k: v for k, v in results.items()},
        })
        stamp["version"] = new_version
    save_stamp(dest, stamp)

    if not same_version:
        if not append_worklog(dest, worklog_entry(stamp, old_version,
                                                  new_version, results,
                                                  propose_dir)):
            print("\nNo 00_AI_context/WORKLOG.md to record the upgrade in — "
                  "record it yourself.")

    tools = find_zone(dest, TOOLS_ZONE)
    print(f"\nDone: {stamp['template']} v{stamp['version']}.")
    print("Next:")
    step = 1
    if results["proposed"]:
        print(f"  {step}. Review {propose_dir}/ — merge what you want into the "
              f"live files by hand,")
        print(f"     then empty the folder. Nothing in it is live.")
        step += 1
    if tools:
        print(f"  {step}. Run python3 {tools}/update_index.py --diff, read what "
              f"it says, then rebuild")
        print(f"     the baseline with python3 {tools}/update_index.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
