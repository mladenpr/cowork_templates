"""Regression tests for templates/cowork-author/05_tools/.

    python3 -m unittest discover tests          # from the repository root

Standard library only. The Word fixtures are built here, in code, from the
minimal OOXML that Word actually writes — no binary files in the repository,
and every fixture says which feature it exists to pin down.
"""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "templates", "cowork-author", "05_tools")
NEW_PROJECT = os.path.join(ROOT, "bin", "new_project.py")


def load(name):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(TOOLS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


index = load("update_index")
extract = load("extract_text")


def run(script, *args, cwd=None):
    proc = subprocess.run([sys.executable, script, *args],
                          capture_output=True, text=True, cwd=cwd)
    return proc.returncode, proc.stdout + proc.stderr


# --------------------------------------------------------------------------
# docx fixture builder
# --------------------------------------------------------------------------

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def make_docx(path, paras, comments=None, header=None):
    """paras: [(text, style-or-None)], comments: [(author, text)]."""
    def p(text, style=None):
        ppr = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
        return (f'<w:p>{ppr}<w:r><w:t xml:space="preserve">{text}</w:t></w:r>'
                f"</w:p>")
    body = "".join(p(t, s) for t, s in paras)
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("[Content_Types].xml",
                    '<Types xmlns="http://schemas.openxmlformats.org/package/'
                    '2006/content-types"/>')
        zf.writestr("word/document.xml",
                    f'<w:document xmlns:w="{W_NS}"><w:body>{body}</w:body>'
                    f"</w:document>")
        if header:
            zf.writestr("word/header1.xml",
                        f'<w:hdr xmlns:w="{W_NS}">{p(header)}</w:hdr>')
        if comments:
            cs = "".join(
                f'<w:comment w:id="{i}" w:author="{a}" '
                f'w:date="2026-08-19T10:00:00Z">{p(t)}</w:comment>'
                for i, (a, t) in enumerate(comments))
            zf.writestr("word/comments.xml",
                        f'<w:comments xmlns:w="{W_NS}">{cs}</w:comments>')


BASE = [("Introduction", "Heading1"),
        ("This method statement covers the piling works at the north quay.", None),
        ("Scope", "Heading1"),
        ("The works comprise 40 bored piles of 900 mm diameter.", None),
        ("Risks", "Heading1"),
        ("Noise and vibration near the residential block.", None)]

REVISED = [("Introduction", "Heading1"),
           ("This method statement covers the piling works at the north quay "
            "and the approach ramp.", None),
           ("Scope", "Heading1"),
           ("The works comprise 44 bored piles of 900 mm diameter.", None),
           ("Programme", "Heading1"),
           ("Twelve weeks from mobilisation.", None)]


# --------------------------------------------------------------------------
# a fresh project per test
# --------------------------------------------------------------------------

class Project(unittest.TestCase):

    SLUG = "method-statement"

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.proj = os.path.join(self.tmp, "proj")
        code, out = run(NEW_PROJECT, self.proj, "--name", "Fixture",
                        "--template", "cowork-author", "--client", "ACME Ltd")
        self.assertEqual(code, 0, out)
        self.tools = os.path.join(self.proj, "05_tools")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def path(self, *parts):
        return os.path.join(self.proj, *parts)

    def touch(self, rel, content=b"x"):
        full = self.path(*rel.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as f:
            f.write(content)
        return rel

    def read(self, rel):
        with open(self.path(*rel.split("/")), encoding="utf-8") as f:
            return f.read()

    def diff(self):
        return run(os.path.join(self.tools, "update_index.py"), self.proj, "--diff")

    def reindex(self):
        return run(os.path.join(self.tools, "update_index.py"), self.proj)

    def extract(self, *extra):
        return run(os.path.join(self.tools, "extract_text.py"), self.proj, *extra)

    def draft_diff(self, *extra):
        return run(os.path.join(self.tools, "draft_diff.py"), self.SLUG,
                   self.proj, *extra)

    def revision(self, n, paras, name=None, **kw):
        d = self.path("03_revisions", self.SLUG, f"R{n:02d}")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, name or f"{self.SLUG}_R{n:02d}.docx")
        make_docx(p, paras, **kw)
        return p

    def draft(self, paras, name="Method Statement.docx", **kw):
        d = self.path("04_working", "drafts", self.SLUG)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, name)
        make_docx(p, paras, **kw)
        return p


# --------------------------------------------------------------------------
# instantiation
# --------------------------------------------------------------------------

class Instantiation(Project):

    def test_fresh_project_is_clean_and_complete(self):
        code, out = self.diff()
        self.assertEqual(code, 0, out)
        self.assertIn("Clean", out)
        self.assertEqual(index.missing_dirs(self.proj), [])
        for rel in ("VERSION", "01_basis/reference/.gitkeep",
                    "04_working/drafts/.gitkeep"):
            self.assertFalse(os.path.exists(self.path(*rel.split("/"))), rel)
        for rel in ("README.md", "CLAUDE.md", "00_AI_context/PROJECT.md",
                    "00_AI_context/WORKLOG.md", "02_exchange/LOG.md",
                    "03_revisions/LOG.md",
                    "00_AI_context/documents/_TEMPLATE.md",
                    "00_AI_context/datasets/_TEMPLATE.md"):
            text = self.read(rel)
            self.assertNotIn("{{", text, rel)
            self.assertNotIn("04_tools", text, rel)
            self.assertNotIn("03_working", text, rel)
        self.assertIn("cowork-author", self.read("README.md"))
        self.assertIn("R12", self.read("README.md"))

    def test_three_basis_roles_and_documents_are_schema(self):
        for d in ("01_basis/reference", "01_basis/examples",
                  "01_basis/templates", "00_AI_context/documents",
                  "03_revisions"):
            self.assertTrue(os.path.isdir(self.path(*d.split("/"))), d)
        shutil.rmtree(self.path("01_basis", "examples"))
        os.rmdir(self.path("00_AI_context", "documents")) if not os.listdir(
            self.path("00_AI_context", "documents")) else shutil.rmtree(
            self.path("00_AI_context", "documents"))
        self.assertEqual(index.missing_dirs(self.proj),
                         ["00_AI_context/documents", "01_basis/examples"])
        code, out = self.diff()
        self.assertEqual(code, 1, out)
        self.assertIn("MISSING DIR  01_basis/examples/", out)
        self.assertIn("MISSING DIR  00_AI_context/documents/", out)


# --------------------------------------------------------------------------
# the scan
# --------------------------------------------------------------------------

class Scan(Project):

    def test_draft_edit_is_its_own_section_not_an_alarm(self):
        self.draft(BASE)
        self.touch("04_working/analysis/calc.csv")
        self.reindex()
        with open(self.draft(REVISED), "ab") as f:
            f.write(b"x")
        self.touch("04_working/analysis/calc.csv", b"y,z")
        code, out = self.diff()
        self.assertEqual(code, 1, out)
        self.assertIn("DRAFT EDITED since last index", out)
        self.assertIn("  CHANGED  04_working/drafts/method-statement/Method Statement.docx", out)
        self.assertNotIn("FROZEN ZONE MOVED", out)
        self.assertIn("0 in a frozen zone, 1 in a live draft", out)
        # analysis is routine and listed once, in the plain section
        self.assertIn("CHANGED  04_working/analysis/calc.csv", out)
        self.assertEqual(out.count("calc.csv"), 1)
        self.assertEqual(out.count("Method Statement.docx"), 1)

    def test_log_growth_is_not_an_alarm_but_loss_is(self):
        for rel in ("02_exchange/LOG.md", "03_revisions/LOG.md"):
            with open(self.path(*rel.split("/")), "a", encoding="utf-8") as f:
                f.write("| 2026-08-19 | x | | | | | | | |\n")
        code, out = self.diff()
        self.assertEqual(code, 1, out)
        self.assertNotIn("FROZEN ZONE MOVED", out)
        self.assertIn("CHANGED  03_revisions/LOG.md", out)
        self.assertIn("0 in a frozen zone", out)
        os.remove(self.path("03_revisions", "LOG.md"))
        code, out = self.diff()
        self.assertIn("FROZEN ZONE MOVED", out)
        self.assertIn("MISSING  03_revisions/LOG.md", out)

    def test_revision_zone_is_frozen_and_temp_is_ignored(self):
        p = self.revision(1, BASE)
        self.touch("06_temp/scratch.txt")
        self.reindex()
        with open(p, "ab") as f:
            f.write(b"tampered")
        code, out = self.diff()
        self.assertEqual(code, 1, out)
        self.assertIn("FROZEN ZONE MOVED", out)
        self.assertIn("CHANGED  03_revisions/method-statement/R01/method-statement_R01.docx", out)
        self.assertNotIn("06_temp", out)
        self.assertNotIn("06_temp", self.read("00_AI_context/INDEX.md"))


    def test_inbox_is_counted_until_empty_and_is_schema(self):
        self.touch("_inbox/IMG_0001.jpg")
        self.touch("_inbox/spec.pdf")
        code, out = self.diff()
        self.assertEqual(code, 1, out)
        self.assertIn("2 file(s) in _inbox/ awaiting filing", out)
        self.assertIn("NEW      _inbox/IMG_0001.jpg", out)
        code, out = self.reindex()
        self.assertIn("2 file(s) in _inbox/", out)
        # baselined: no longer NEW, still counted, every scan
        code, out = self.diff()
        self.assertNotIn("NEW", out)
        self.assertIn("2 file(s) in _inbox/", out)
        os.remove(self.path("_inbox", "IMG_0001.jpg"))
        os.remove(self.path("_inbox", "spec.pdf"))
        os.rmdir(self.path("_inbox"))
        self.assertIn("_inbox", index.missing_dirs(self.proj))

    def photos(self, folder, n, ext=".jpg", start=1):
        for i in range(start, start + n):
            self.touch(f"{folder}/IMG_{i:04d}{ext}", b"\xff\xd8" + bytes([i % 251]))

    def test_media_folders_roll_up_in_index_diff_and_inbox(self):
        self.photos("01_basis/reference/photos/walk-01", 12)
        self.photos("01_basis/reference/photos/walk-01", 2, ".png", 13)
        self.touch("01_basis/reference/photos/walk-01/notes.txt", b"what each shows")
        self.photos("01_basis/reference/photos/walk-02", 9)      # below threshold
        self.photos("_inbox", 11)                                  # rolls up too
        code, out = self.diff()
        self.assertEqual(code, 1, out)
        self.assertIn("NEW      01_basis/reference/photos/walk-01/ — 14 media files (.jpg ×12, .png ×2)", out)
        self.assertNotIn("walk-01/IMG_0001.jpg", out)
        self.assertIn("NEW      01_basis/reference/photos/walk-01/notes.txt", out)
        self.assertIn("NEW      01_basis/reference/photos/walk-02/IMG_0009.jpg", out)
        self.assertIn("NEW      _inbox/ — 11 media files (.jpg ×11)", out)
        self.assertIn("11 file(s) in _inbox/ awaiting filing", out)
        self.assertIn("INBOX     _inbox/ — 11 media files (.jpg ×11)", out)
        self.assertNotIn("INBOX     _inbox/IMG_0001.jpg", out)
        code, out = self.reindex()
        self.assertIn("2 media folder(s) rolled up", out)
        idx = self.read("00_AI_context/INDEX.md")
        self.assertIn("- `01_basis/reference/photos/walk-01/` — 14 media files (.jpg ×12, .png ×2) — ", idx)
        self.assertNotIn("walk-01/IMG_0001.jpg", idx)
        self.assertIn("walk-01/notes.txt", idx)
        self.assertIn("walk-02/IMG_0001.jpg", idx)
        self.assertIn("- `_inbox/` — 11 media files (.jpg ×11) — ", idx)
        self.assertNotIn("_inbox/IMG_0001.jpg", idx)
        # the manifest still records every file
        import json
        with open(self.path("00_AI_context", "MANIFEST.json"), encoding="utf-8") as f:
            paths = {x["path"] for x in json.load(f)["files"]}
        self.assertIn("01_basis/reference/photos/walk-01/IMG_0001.jpg", paths)
        # a description written on the folder line survives, and the count
        # is not read back as the description
        idx = idx.replace(
            "- `01_basis/reference/photos/walk-01/` — 14 media files (.jpg ×12, .png ×2) — ",
            "- `01_basis/reference/photos/walk-01/` — 14 media files (.jpg ×12, .png ×2) — site walk, north quay")
        with open(self.path("00_AI_context", "INDEX.md"), "w", encoding="utf-8") as f:
            f.write(idx)
        self.photos("01_basis/reference/photos/walk-01", 1, ".jpg", 15)
        self.reindex()
        idx = self.read("00_AI_context/INDEX.md")
        self.assertIn("- `01_basis/reference/photos/walk-01/` — 15 media files (.jpg ×13, .png ×2) — site walk, north quay", idx)
        # neither the described folder nor the undescribed one self-appends
        self.assertEqual(idx.count("media files"), 2)
        self.assertIn("- `_inbox/` — 11 media files (.jpg ×11) — \n", idx)
        self.reindex()
        idx = self.read("00_AI_context/INDEX.md")
        self.assertEqual(idx.count("site walk, north quay"), 1)
        self.assertEqual(idx.count("media files"), 2)
        # a folder that loses files is one MISSING line too
        for i in range(1, 13):
            os.remove(self.path("01_basis", "reference", "photos", "walk-01", f"IMG_{i:04d}.jpg"))
        code, out = self.diff()
        self.assertIn("FROZEN ZONE MOVED", out)           # photos in basis are frozen
        self.assertIn("MISSING  01_basis/reference/photos/walk-01/IMG_0001.jpg", out)


# --------------------------------------------------------------------------
# the extractor
# --------------------------------------------------------------------------

class Extractor(Project):

    def test_covers_three_zones_and_mirrors_returns_with_authors(self):
        self.revision(1, BASE)
        ret = self.path("03_revisions", self.SLUG, "R01", "returns")
        os.makedirs(ret)
        make_docx(os.path.join(ret, "JD_R01_comments.docx"), BASE,
                  comments=[("Jane Doe", "Pile count looks low")])
        make_docx(self.path("01_basis", "examples", "old-proposal.docx"),
                  [("Intro", "Heading1"), ("Written for Globex in 2024.", None)])
        self.touch("02_exchange/received/rfq.txt", b"text already")
        code, out = self.extract()
        self.assertEqual(code, 0, out)
        code, out = self.extract("--report")
        self.assertIn("01_basis/examples/old-proposal.docx", out)
        self.assertIn("03_revisions/method-statement/R01/returns/JD_R01_comments.docx", out)
        self.assertIn("02_exchange/received/rfq.txt", out)
        self.assertIn("already text", out)
        mirrored = self.read("04_working/_extracted/03_revisions/method-statement/"
                             "R01/returns/JD_R01_comments.docx.md")
        self.assertIn("**Jane Doe** (2026-08-19): Pile count looks low", mirrored)
        self.assertIn("flags: comments", mirrored)
        # the live draft is never mirrored
        self.draft(BASE)
        self.extract()
        self.assertFalse(os.path.exists(
            self.path("04_working", "_extracted", "04_working")))

    def test_report_rolls_up_opaque_folders(self):
        for i in range(1, 12):
            self.touch(f"01_basis/reference/photos/IMG_{i:03d}.jpg")
        self.touch("01_basis/reference/photos/site-plan.dwg")
        self.touch("01_basis/reference/one.dwg")
        code, out = self.extract("--report")
        self.assertEqual(code, 0, out)
        self.assertIn("01_basis/reference/photos/  12 not extractable (image ×11, CAD drawing ×1)", out.replace("   ", " ").replace("  ", " ").replace("photos/ ", "photos/  "))
        self.assertNotIn("IMG_001.jpg", out)
        self.assertIn("01_basis/reference/one.dwg", out)
        self.assertIn("not extractable (CAD drawing)", out)

    def test_extract_file_reads_any_path_and_writes_nothing(self):
        p = self.draft(BASE, comments=[("M", "fix")])
        before = sorted(os.listdir(self.path("04_working", "_extracted")))
        res = extract.extract_file(p)
        self.assertIn("# Introduction", res.body)
        self.assertIn("comments", res.flags)
        self.assertEqual(before, sorted(os.listdir(self.path("04_working", "_extracted"))))
        txt = self.touch("06_temp/note.md", "# hello\n".encode())
        res = extract.extract_file(self.path(*txt.split("/")))
        self.assertEqual(res.body, ["# hello"])
        self.assertIn("already-text", res.flags)


# --------------------------------------------------------------------------
# draft_diff.py
# --------------------------------------------------------------------------

class DraftDiff(Project):

    def test_identical_is_exit_0(self):
        self.revision(1, BASE)
        self.draft(BASE)
        code, out = self.draft_diff()
        self.assertEqual(code, 0, out)
        self.assertIn("Identical", out)
        self.assertIn("R01 → live draft", out)

    def test_changes_by_section_with_word_marks_against_latest(self):
        self.revision(1, [("Intro", "Heading1"), ("very old", None)])
        self.revision(2, BASE)
        self.draft(REVISED, comments=[("Mladen", "Check pile count")])
        code, out = self.draft_diff()
        self.assertEqual(code, 1, out)
        self.assertIn("R02 → live draft", out)
        self.assertIn("## CHANGED  Introduction", out)
        self.assertIn("[-quay.-]{+quay and the approach ramp.+}", out)
        self.assertIn("[-40-]{+44+}", out)
        self.assertIn("## REMOVED  Risks", out)
        self.assertIn("## ADDED    Programme", out)
        # the extractor's own sections stay top-level, and comments are called out
        self.assertIn("## ADDED    Comments", out)
        self.assertNotIn("Programme › Comments", out)
        self.assertIn("carries **comments** — that is feedback", out)
        self.assertIn("2 changed, 2 added, 1 removed", out)

    def test_summary_against_and_between(self):
        self.revision(1, BASE)
        self.revision(2, BASE[:4])
        self.draft(REVISED)
        code, out = self.draft_diff("--summary")
        self.assertEqual(code, 1, out)
        self.assertIn("## CHANGED  Scope", out)
        self.assertNotIn("[-40-]", out)
        code, out = self.draft_diff("--against", "R01")
        self.assertIn("R01 → live draft", out)
        self.assertIn("## REMOVED  Risks", out)
        code, out = self.draft_diff("--between", "R01", "R02")
        self.assertEqual(code, 1, out)
        self.assertIn("R01 → R02", out)
        self.assertIn("## REMOVED  Risks", out)
        self.assertNotIn("Programme", out)

    def test_usage_errors_are_exit_2_and_name_what_exists(self):
        self.draft(BASE)
        code, out = self.draft_diff()
        self.assertEqual(code, 2, out)
        self.assertIn("No frozen revisions", out)
        self.revision(1, BASE)
        code, out = self.draft_diff("--against", "R07")
        self.assertEqual(code, 2, out)
        self.assertIn("have: R01", out)
        code, out = run(os.path.join(self.tools, "draft_diff.py"), "nosuch", self.proj)
        self.assertEqual(code, 2, out)
        self.assertIn("Present: method-statement", out)

    def test_several_files_pair_by_stem_then_by_elimination_never_by_guess(self):
        # A freeze names the main document <slug>_Rnn and keeps a companion's
        # own stem with _Rnn appended (R11).
        self.revision(1, BASE)
        self.revision(1, [("Appendix", "Heading1")], name="Appendix A_R01.docx")
        # neither live filename starts with the slug, so nothing picks the
        # primary on its own
        self.draft(REVISED, name="Method Statement.docx")
        self.draft([("Appendix", "Heading1"), ("changed", None)], name="Appendix A.docx")
        code, out = self.draft_diff()
        self.assertEqual(code, 2, out)
        self.assertIn("say which with --file", out)
        # the appendix pairs by stem
        code, out = self.draft_diff("--file", "Appendix A.docx")
        self.assertEqual(code, 1, out)
        self.assertIn("Appendix A_R01.docx", out)
        self.assertIn("## CHANGED  Appendix", out)
        self.assertNotIn("method-statement_R01", out)
        # the main document pairs by elimination — it is the one file left on
        # each side once same-stem partners are set aside
        code, out = self.draft_diff("--file", "Method Statement.docx")
        self.assertEqual(code, 1, out)
        self.assertIn("method-statement_R01.docx", out)
        self.assertIn("[-40-]{+44+}", out)
        # a live file named like its frozen counterpart is found without --file
        os.rename(self.path("04_working", "drafts", self.SLUG, "Method Statement.docx"),
                  self.path("04_working", "drafts", self.SLUG, "method-statement.docx"))
        code, out = self.draft_diff()
        self.assertEqual(code, 1, out)
        self.assertIn("method-statement_R01.docx", out)
        # no stem match and no unique leftover: refuse, and point at --rev-file
        self.revision(1, [("Appendix", "Heading1")], name="Appendix B_R01.docx")
        code, out = self.draft_diff("--file", "method-statement.docx")
        self.assertEqual(code, 1, out)            # still paired by stem
        self.draft([("X", "Heading1")], name="Appendix C.docx")
        code, out = self.draft_diff("--file", "Appendix C.docx")
        self.assertEqual(code, 2, out)
        self.assertIn("no counterpart for 'Appendix C.docx'", out)
        self.assertIn("--rev-file", out)
        code, out = self.draft_diff("--file", "Appendix C.docx",
                                    "--rev-file", "Appendix B_R01.docx")
        self.assertEqual(code, 1, out)
        self.assertIn("Appendix B_R01.docx", out)


if __name__ == "__main__":
    unittest.main()
