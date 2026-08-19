#!/usr/bin/env python3
"""draft_diff.py — what changed in a draft, against a frozen revision (R6, R11).

    python3 05_tools/draft_diff.py <slug>                    # live draft vs latest frozen revision
    python3 05_tools/draft_diff.py <slug> --against R03      # live draft vs R03
    python3 05_tools/draft_diff.py <slug> --between R02 R04  # R02 vs R04
    python3 05_tools/draft_diff.py <slug> --file Report.docx # which file, if the draft folder has several
    python3 05_tools/draft_diff.py <slug> --file "Appendix A.docx" --rev-file "Appendix A_R02.docx"
    python3 05_tools/draft_diff.py <slug> --summary          # sections only, no line diffs
    python3 05_tools/draft_diff.py <slug> /path/to/repo

On Windows use `py -3` in place of `python3`.

Why this exists
---------------
The live draft in `04_working/drafts/<slug>/` changes every session, and
nothing mirrors it — extracting it would only produce a stale copy that a
session might read instead of the draft. So "what changed?" has no cheap
answer, and it is asked at exactly two moments that matter:

- **Session start, when the scan says DRAFT EDITED.** The draft changed since
  the last index, which means outside a session — the user edited it by hand.
  The session must know what they changed before it touches anything (R6).
- **Freeze time.** The revision log's "what changed" column is the one that
  gets reread months later, and it is written from this.

It reads the live draft through the same readers `extract_text.py` uses for
the frozen zones, so the two sides compare like with like, and it writes
nothing — not into the draft, not into the revision, not into `_extracted/`.

What it shows
-------------
Both documents are split into sections by heading, and only sections that
differ are printed: added, removed, or changed, with a line diff inside each.
A paragraph that was reworded rather than replaced is shown once, with the
removed words marked `[-like this-]` and the added words `{+like this+}`,
because a two-line diff of a 200-word paragraph hides the three words that
moved. Headers, footers and comments come through as sections of their own —
a comment that appeared in the live draft is feedback (R10), and this is
where it surfaces.

Exit code 0 when the two sides are identical, 1 when they differ, 2 on a
usage error — the same convention as `update_index.py --diff`.
"""

import argparse
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_text  # noqa: E402 — the readers live beside this script

DRAFTS = os.path.join("04_working", "drafts")
REVISIONS = "03_revisions"
REV_DIR = re.compile(r"^R(\d+)$")
REV_SUFFIX = re.compile(r"_R\d+$")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
# Sections the extractor adds around a document's own text — chrome, notes,
# comments, a spreadsheet's sheets. They are not part of the document's outline
# and must not nest under whatever heading happened to come last.
EXTRACTOR_SECTIONS = re.compile(
    r"^(Header / footer|Footnotes|Endnotes|Comments|Sheet: .*|Slide \d+.*|Page \d+.*)$")


def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


# --------------------------------------------------------------------------
# locating the two sides
# --------------------------------------------------------------------------

def extractable(fn):
    if fn.startswith((".", "~")) or fn.lower().endswith(".tmp"):
        return False
    return extract_text.classify(os.path.splitext(fn)[1].lower()) not in (
        "opaque",)


def candidates(folder, label):
    try:
        return sorted(fn for fn in os.listdir(folder)
                      if os.path.isfile(os.path.join(folder, fn))
                      and extractable(fn))
    except OSError:
        die(f"{label}: no such folder: {folder}")


def stem_of(fn):
    """Filename stem with a trailing _Rnn removed, lower-cased, plus extension."""
    stem, ext = os.path.splitext(fn)
    return REV_SUFFIX.sub("", stem).lower(), ext.lower()


def choose_primary(folder, slug, wanted, label):
    """The file on the side being compared FROM — the live draft, usually.

    An explicit --file wins. Otherwise: the only extractable file; failing
    that, the one whose stem starts with the slug. Several candidates and no
    rule to choose by is a question for the user, not a guess.
    """
    names = candidates(folder, label)
    if wanted:
        if wanted not in names:
            die(f"{label}: no file named {wanted!r} in {folder}\n"
                f"  present: {', '.join(names) or '(none)'}")
        return os.path.join(folder, wanted)
    if not names:
        die(f"{label}: nothing extractable in {folder}")
    if len(names) == 1:
        return os.path.join(folder, names[0])
    by_slug = [fn for fn in names if os.path.splitext(fn)[0].lower().startswith(slug.lower())]
    if len(by_slug) == 1:
        return os.path.join(folder, by_slug[0])
    die(f"{label}: several files in {folder} — say which with --file:\n  "
        + "\n  ".join(names))


def choose_counterpart(folder, primary_folder, primary, slug, wanted, label):
    """The file on the other side that corresponds to `primary`.

    An explicit --rev-file wins. Otherwise the counterpart is the file with
    the same stem (ignoring a trailing _Rnn) and extension. If there is none,
    one more case is recognised, because the freeze step creates it (R11): the
    main document is renamed <slug>_Rnn at freeze while companions keep their
    stems. So if the revision folder's <slug>_Rnn file has no same-stem partner
    on the live side, and `primary` is the only live file without a same-stem
    partner in the revision folder, those two are the main document and are
    paired. Anything less certain is an error, because a diff of the wrong
    pair reads exactly like a diff of the right one.
    """
    names = candidates(folder, label)
    if wanted:
        if wanted not in names:
            die(f"{label}: no file named {wanted!r} in {folder}\n"
                f"  present: {', '.join(names) or '(none)'}")
        return os.path.join(folder, wanted)
    if not names:
        die(f"{label}: nothing extractable in {folder}")
    want = stem_of(os.path.basename(primary))
    same = [fn for fn in names if stem_of(fn) == want]
    if len(same) == 1:
        return os.path.join(folder, same[0])
    if len(names) == 1 and len(candidates(primary_folder, "primary")) == 1:
        return os.path.join(folder, names[0])
    primaries = candidates(primary_folder, "primary")
    other_side = {stem_of(fn) for fn in primaries}
    this_side = {stem_of(fn) for fn in names}
    main_here = [fn for fn in names
                 if stem_of(fn) not in other_side
                 and stem_of(fn)[0] == slug.lower()
                 and stem_of(fn)[1] == want[1]]
    left_there = [fn for fn in primaries if stem_of(fn) not in this_side]
    if len(main_here) == 1 and left_there == [os.path.basename(primary)]:
        return os.path.join(folder, main_here[0])
    die(f"{label}: no counterpart for {os.path.basename(primary)!r} in {folder} "
        f"— say which with --rev-file:\n  " + "\n  ".join(names))


def revisions(root, slug):
    base = os.path.join(root, REVISIONS, slug)
    if not os.path.isdir(base):
        return {}
    out = {}
    for d in os.listdir(base):
        m = REV_DIR.match(d)
        if m and os.path.isdir(os.path.join(base, d)):
            out[int(m.group(1))] = os.path.join(base, d)
    return out


def revision_dir(root, slug, label, available):
    m = REV_DIR.match(label or "")
    if not m:
        die(f"Revision labels look like R03; got {label!r}")
    n = int(m.group(1))
    if n not in available:
        have = ", ".join(f"R{k:02d}" for k in sorted(available)) or "(none)"
        die(f"No frozen revision {label} for '{slug}' under {REVISIONS}/{slug}/ "
            f"— have: {have}")
    return available[n]


# --------------------------------------------------------------------------
# text, sections, diff
# --------------------------------------------------------------------------

def body_of(path):
    res = extract_text.extract_file(path)
    if set(res.flags) & {"rights-managed-or-encrypted", "not-a-valid-office-file",
                         "extract-error", "not-extracted", "not-extractable"}:
        die(f"Cannot read {path}: {', '.join(res.flags)}\n"
            + "\n".join(res.body))
    return [ln.rstrip() for ln in res.body], res


def sections(lines):
    """Split extracted lines into ordered (heading-path, lines) sections.

    Text before the first heading is the section "(front)". Headings nest by
    level so a renamed subsection shows under its parent rather than as an
    unrelated removal plus addition.
    """
    out = []
    path = []
    key, body = "(front)", []
    for ln in lines:
        m = HEADING.match(ln)
        if m:
            if body or key != "(front)":
                out.append((key, body))
            level = len(m.group(1))
            title = m.group(2).strip()
            if EXTRACTOR_SECTIONS.match(title):
                path = [title]
            else:
                path = path[:level - 1] + [title]
            key, body = " › ".join(path), []
        elif ln.strip():
            body.append(ln)
    out.append((key, body))
    # keep order; a heading that occurs twice gets a (2) suffix the second time
    seen, merged = {}, []
    for key, body in out:
        if key in seen:
            seen[key] += 1
            key = f"{key} ({seen[key]})"
        else:
            seen[key] = 1
        merged.append((key, body))
    return merged


def words(s):
    return re.findall(r"\S+|\s+", s)


def word_diff(a, b):
    """One paragraph, reworded: mark removed [-…-] and added {+…+} words."""
    wa, wb = words(a), words(b)
    sm = difflib.SequenceMatcher(None, wa, wb, autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            out.append("".join(wa[i1:i2]))
        elif op == "delete":
            out.append("[-" + "".join(wa[i1:i2]).strip() + "-]")
        elif op == "insert":
            out.append("{+" + "".join(wb[j1:j2]).strip() + "+}")
        else:
            out.append("[-" + "".join(wa[i1:i2]).strip() + "-]"
                       "{+" + "".join(wb[j1:j2]).strip() + "+}")
    return "".join(out)


def similar(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio() >= 0.5


def section_diff(old, new):
    """Line diff of one section; reworded paragraphs rendered once, word-marked."""
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    out, removed, added = [], 0, 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        if op == "replace" and (i2 - i1) == (j2 - j1) and all(
                similar(a, b) for a, b in zip(old[i1:i2], new[j1:j2])):
            for a, b in zip(old[i1:i2], new[j1:j2]):
                out.append("~ " + word_diff(a, b))
            removed += i2 - i1
            added += j2 - j1
            continue
        for ln in old[i1:i2]:
            out.append("- " + ln)
            removed += 1
        for ln in new[j1:j2]:
            out.append("+ " + ln)
            added += 1
    return out, removed, added


def compare(old_lines, new_lines, summary_only=False):
    old_s = dict(sections(old_lines))
    new_s = dict(sections(new_lines))
    order = []
    for key, _ in sections(old_lines) + sections(new_lines):
        if key not in order:
            order.append(key)
    report, n_added, n_removed, n_changed = [], 0, 0, 0
    tot_minus = tot_plus = 0
    for key in order:
        o, n = old_s.get(key), new_s.get(key)
        if o is not None and n is not None:
            if o == n:
                continue
            body, minus, plus = section_diff(o, n)
            n_changed += 1
            tot_minus += minus
            tot_plus += plus
            report.append(f"## CHANGED  {key}   (-{minus} +{plus})")
            if not summary_only:
                report.extend("    " + ln for ln in body)
                report.append("")
        elif o is None:
            n_added += 1
            tot_plus += len(n)
            report.append(f"## ADDED    {key}   (+{len(n)} paragraphs)")
            if not summary_only:
                report.extend("    + " + ln for ln in n)
                report.append("")
        else:
            n_removed += 1
            tot_minus += len(o)
            report.append(f"## REMOVED  {key}   (-{len(o)} paragraphs)")
            if not summary_only:
                report.extend("    - " + ln for ln in o)
                report.append("")
    return report, (n_changed, n_added, n_removed, tot_minus, tot_plus)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Diff a live draft against a frozen revision, by section.")
    ap.add_argument("slug", help="the deliverable's slug: 04_working/drafts/<slug>/")
    ap.add_argument("root", nargs="?",
                    help="repo root (default: this script's parent's parent)")
    ap.add_argument("--against", metavar="Rnn",
                    help="compare the live draft with this frozen revision "
                         "(default: the latest)")
    ap.add_argument("--between", nargs=2, metavar=("Rnn", "Rmm"),
                    help="compare two frozen revisions; the live draft is not read")
    ap.add_argument("--file", help="which file in the draft folder (or the first "
                                   "revision of --between), if several")
    ap.add_argument("--rev-file", help="which file in the revision folder, if it "
                                       "cannot be matched to --file by name")
    ap.add_argument("--summary", action="store_true",
                    help="sections only — no line diffs")
    args = ap.parse_args(argv)

    root = (os.path.abspath(os.path.expanduser(args.root)) if args.root
            else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.isdir(os.path.join(root, DRAFTS)):
        die(f"Not a cowork-author project (no {DRAFTS}/): {root}")
    if args.between and args.against:
        die("--between and --against are mutually exclusive")

    slug = args.slug
    avail = revisions(root, slug)

    if args.between:
        lo, hi = (revision_dir(root, slug, r, avail) for r in args.between)
        old_path = choose_primary(lo, slug, args.file, args.between[0])
        new_path = choose_counterpart(hi, lo, old_path, slug, args.rev_file, args.between[1])
        old_label, new_label = args.between
    else:
        draft_dir = os.path.join(root, DRAFTS, slug)
        if not os.path.isdir(draft_dir):
            die(f"No live draft folder {DRAFTS}/{slug}/ — is the slug right? "
                f"Present: {', '.join(sorted(os.listdir(os.path.join(root, DRAFTS)))) or '(none)'}")
        if not avail:
            die(f"No frozen revisions for '{slug}' under {REVISIONS}/{slug}/ — "
                f"nothing to diff against. Freeze one first (R11).", 2)
        if args.against:
            rev_dir = revision_dir(root, slug, args.against, avail)
            old_label = args.against
        else:
            n = max(avail)
            rev_dir, old_label = avail[n], f"R{n:02d}"
        new_path = choose_primary(draft_dir, slug, args.file, "live draft")
        old_path = choose_counterpart(rev_dir, draft_dir, new_path, slug, args.rev_file, old_label)
        new_label = "live draft"

    old_lines, _ = body_of(old_path)
    new_lines, new_res = body_of(new_path)
    rel = lambda p: os.path.relpath(p, root).replace(os.sep, "/")
    print(f"# {slug}: {old_label} → {new_label}")
    print(f"- {old_label}: `{rel(old_path)}`")
    print(f"- {new_label}: `{rel(new_path)}`")
    live_flags = [f for f in new_res.flags if f in ("comments", "tracked-changes")]
    if new_label == "live draft" and live_flags:
        print(f"- the live draft carries **{' and '.join(live_flags)}** — that "
              f"is feedback (R10): register it before acting on it.")
    print()

    report, (chg, add, rem, minus, plus) = compare(old_lines, new_lines, args.summary)
    if not report:
        print("Identical — no section differs.")
        return 0
    print(f"{chg} changed, {add} added, {rem} removed section(s); "
          f"-{minus} +{plus} paragraph(s).")
    print()
    print("\n".join(report))
    return 1


if __name__ == "__main__":
    sys.exit(main())
