"""Regression tests for templates/cowork-consultant/04_tools/.

    python3 -m unittest discover tests          # from the repository root

Standard library only. The Office fixtures are built here, in code, from the
minimal OOXML that Excel actually writes — no binary files in the repository,
and every fixture says exactly which feature it exists to pin down.
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
TOOLS = os.path.join(ROOT, "templates", "cowork-consultant", "04_tools")
NEW_PROJECT = os.path.join(ROOT, "bin", "new_project.py")


def load(name):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(TOOLS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


extract = load("extract_text")
index = load("update_index")


# --------------------------------------------------------------------------
# xlsx fixture builder
# --------------------------------------------------------------------------

S_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def make_xlsx(path, sheets, date1904=False):
    """sheets: [(name, hidden, sheet_xml_rows)] — rows are raw <row> XML.

    Style index 1 is a date (built-in numFmtId 14, m/d/yyyy); 0 is General.
    """
    wb_pr = '<workbookPr date1904="1"/>' if date1904 else "<workbookPr/>"
    sheet_tags = "".join(
        f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"'
        + (' state="hidden"' if hidden else "") + "/>"
        for i, (name, hidden, _) in enumerate(sheets, 1))
    workbook = (f'<workbook xmlns="{S_NS}" xmlns:r="{R_NS}">{wb_pr}'
                f"<sheets>{sheet_tags}</sheets></workbook>")
    rels = (f'<Relationships xmlns="{PR_NS}">' + "".join(
        f'<Relationship Id="rId{i}" Type="x" Target="worksheets/sheet{i}.xml"/>'
        for i in range(1, len(sheets) + 1)) + "</Relationships>")
    styles = (f'<styleSheet xmlns="{S_NS}"><cellXfs count="2">'
              '<xf numFmtId="0"/><xf numFmtId="14"/></cellXfs></styleSheet>')
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", rels)
        zf.writestr("xl/styles.xml", styles)
        for i, (_, _, rows) in enumerate(sheets, 1):
            zf.writestr(f"xl/worksheets/sheet{i}.xml",
                        f'<worksheet xmlns="{S_NS}"><sheetData>{rows}'
                        "</sheetData></worksheet>")


def cell(ref, value, style=None, formula=None):
    s = f' s="{style}"' if style is not None else ""
    f = f"<f>{formula}</f>" if formula else ""
    return f'<c r="{ref}" t="inlineStr"{s}><is><t>{value}</t></is></c>' \
        if isinstance(value, str) else f'<c r="{ref}"{s}>{f}<v>{value}</v></c>'


def run_extract(path, max_rows=200):
    res = extract.extract_one(path, "xlsx", max_rows, None)
    return res, "\n".join(res.body)


# --------------------------------------------------------------------------
# extract_text.py — spreadsheets
# --------------------------------------------------------------------------

class ExcelDates(unittest.TestCase):

    def test_1900_system_is_the_default(self):
        self.assertEqual(extract.excel_date("45000"), "2023-03-15")
        self.assertEqual(extract.excel_date("61"), "1900-03-01")
        self.assertIsNone(extract.excel_date("0"))

    def test_1904_system_shifts_by_1462_days(self):
        self.assertEqual(extract.excel_date("45000", date1904=True), "2027-03-16")
        self.assertEqual(extract.excel_date("0", date1904=True), "1904-01-01")

    def test_workbook_date_system_is_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = f'<row r="1">{cell("A1", 45000, style=1)}</row>'
            for flag, expect in ((False, "2023-03-15"), (True, "2027-03-16")):
                p = os.path.join(tmp, f"d{int(flag)}.xlsx")
                make_xlsx(p, [("S", False, row)], date1904=flag)
                res, body = run_extract(p)
                self.assertIn(expect, body, f"date1904={flag}")
                self.assertEqual(res.meta.get("date_system"), 1904 if flag else None)


class ExcelCoordinates(unittest.TestCase):

    def test_row_numbers_and_column_letters_survive_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "gap.xlsx")
            rows = (f'<row r="1">{cell("A1", "Item")}{cell("C1", "Qty")}</row>'
                    f'<row r="2">{cell("A2", "Bolt")}{cell("C2", 12)}</row>'
                    f'<row r="100">{cell("A100", "Total")}'
                    f'{cell("C100", 12, formula="SUM(C2:C99)")}</row>')
            make_xlsx(p, [("Data", False, rows), ("Old", True, "")])
            res, body = run_extract(p)
            lines = body.splitlines()
            self.assertIn("| # | A | B | C |", lines)
            self.assertIn("| 1 | Item |  | Qty |", lines)
            self.assertIn("| 2 | Bolt |  | 12 |", lines)
            self.assertIn("| 100 | Total |  | 12 |", lines)
            # A blank row is dropped, not rendered as ninety-seven empty lines.
            self.assertNotIn("| 3 |", body)
            self.assertIn("## Sheet: Old (hidden)", body)
            self.assertIn("`C100` = `=SUM(C2:C99)` → 12", body)
            self.assertEqual(res.meta.get("formulas"), 1)

    def test_col_letter_round_trips(self):
        for ref in ("A", "Z", "AA", "AZ", "BA", "ZZ", "AAA"):
            self.assertEqual(extract.col_letter(extract.col_index(ref)), ref)

    def test_truncation_records_the_row_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "long.xlsx")
            rows = "".join(f'<row r="{i}">{cell(f"A{i}", i)}</row>'
                           for i in range(1, 6))
            make_xlsx(p, [("S", False, rows)])
            res, body = run_extract(p, max_rows=2)
            self.assertIn("truncated", res.flags)
            self.assertEqual(res.meta.get("max_rows"), 2)
            self.assertIn("3 further populated rows not shown", body)


# --------------------------------------------------------------------------
# extract_text.py — freshness, PDF page ranges, orphans
# --------------------------------------------------------------------------

CURRENT = object()


def write_extraction(out_path, st, flags=(), version=CURRENT, extra=()):
    if version is CURRENT:
        version = extract.EXTRACTOR_VERSION
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    lines = ["---", "source: x", f"source_size: {st.st_size}",
             f"source_mtime: {round(st.st_mtime, 2)}", "extracted: t",
             "extractor: test"]
    if version is not None:
        lines.append(f"extractor_version: {version}")
    lines += list(extra)
    if flags:
        lines.append("flags: " + ", ".join(flags))
    lines += ["---", "", "body"]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


class Freshness(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.src = os.path.join(self.tmp, "doc.pdf")
        with open(self.src, "wb") as f:
            f.write(b"%PDF-1.4 fixture")
        self.st = os.stat(self.src)
        self.out = os.path.join(self.tmp, "doc.pdf.md")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def stale(self, **kw):
        write_extraction(self.out, self.st, **kw)
        return extract.staleness(self.out, self.st, 200)

    def test_a_good_extraction_is_current(self):
        self.assertIsNone(self.stale())

    def test_failed_attempts_are_retried(self):
        # The bug this pins: a stub written because pypdf was missing matched
        # its source on size and mtime and was "current" forever.
        self.assertEqual(self.stale(flags=["not-extracted"]),
                         "previous attempt failed")
        self.assertEqual(self.stale(flags=["extract-error"]),
                         "previous attempt failed")

    def test_document_facts_are_not_retried(self):
        for flag in ("encrypted", "likely-scanned-needs-ocr",
                     "rights-managed-or-encrypted", "comments"):
            self.assertIsNone(self.stale(flags=[flag]), flag)

    def test_older_extractor_output_is_redone(self):
        self.assertEqual(self.stale(version=None), "extractor updated")
        self.assertEqual(self.stale(version=extract.EXTRACTOR_VERSION - 1),
                         "extractor updated")

    def test_source_change_wins(self):
        write_extraction(self.out, self.st, flags=["not-extracted"])
        with open(self.src, "ab") as f:
            f.write(b" more")
        self.assertEqual(extract.staleness(self.out, os.stat(self.src), 200),
                         "source changed")

    def test_truncated_sheet_follows_the_row_limit(self):
        self.assertEqual(self.stale(flags=["truncated"], extra=["max_rows: 200"]),
                         None)
        write_extraction(self.out, self.st, flags=["truncated"],
                         extra=["max_rows: 200"])
        self.assertEqual(extract.staleness(self.out, self.st, 500),
                         "row limit changed")


class PdfPages(unittest.TestCase):

    def test_page_ranges(self):
        self.assertEqual(extract.page_ranges([1, 2, 3, 7, 9, 10]), "1-3, 7, 9-10")
        self.assertEqual(extract.page_ranges([4]), "4")
        self.assertEqual(extract.page_ranges([]), "")

    def test_mixed_pdf_reports_the_textless_pages(self):
        class Page:
            def __init__(self, text):
                self.text = text

            def extract_text(self):
                return self.text

        class Reader:
            is_encrypted = False

            def __init__(self, path):
                self.pages = [Page("x" * 400), Page(""), Page("12"),
                              Page("y" * 400), Page("")]

        res = extract.Result("pdf")
        extract.extract_pdf("ignored", res, Reader)
        self.assertEqual(res.meta["textless_pages"], "2-3, 5")
        self.assertIn("mixed-text-and-scanned", res.flags)
        self.assertNotIn("likely-scanned-needs-ocr", res.flags)

        class Scanned(Reader):
            def __init__(self, path):
                self.pages = [Page(""), Page("3")]

        res = extract.Result("pdf")
        extract.extract_pdf("ignored", res, Scanned)
        self.assertEqual(res.meta["textless_pages"], "1-2")
        self.assertIn("likely-scanned-needs-ocr", res.flags)


class Orphans(unittest.TestCase):

    def test_extraction_without_a_source_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            ext = os.path.join(root, "03_working", "_extracted", "01_basis")
            os.makedirs(os.path.join(root, "01_basis"))
            os.makedirs(ext)
            open(os.path.join(root, "01_basis", "kept.docx"), "w").close()
            open(os.path.join(ext, "kept.docx.md"), "w").close()
            open(os.path.join(ext, "gone.docx.md"), "w").close()
            open(os.path.join(ext, ".gitkeep"), "w").close()
            self.assertEqual(list(extract.orphans(root)), ["01_basis/gone.docx.md"])


# --------------------------------------------------------------------------
# update_index.py and end-to-end instantiation
# --------------------------------------------------------------------------

def run(*argv, cwd=None):
    proc = subprocess.run([sys.executable, *argv], cwd=cwd, capture_output=True,
                          text=True)
    return proc.returncode, proc.stdout + proc.stderr


class Project(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.proj = os.path.join(self.tmp, "proj")
        code, out = run(NEW_PROJECT, self.proj, "--name", "Fixture",
                        "--template", "cowork-consultant")
        self.assertEqual(code, 0, out)
        self.tools = os.path.join(self.proj, "04_tools")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def diff(self):
        return run(os.path.join(self.tools, "update_index.py"), self.proj, "--diff")

    def reindex(self):
        return run(os.path.join(self.tools, "update_index.py"), self.proj)

    def extract(self, *extra):
        return run(os.path.join(self.tools, "extract_text.py"), self.proj, *extra)

    def test_fresh_project_is_clean_and_complete(self):
        code, out = self.diff()
        self.assertEqual(code, 0, out)
        self.assertIn("Clean", out)
        self.assertEqual(index.missing_dirs(self.proj), [])
        for rel in ("VERSION", "01_basis/.gitkeep", "_inbox/.gitkeep"):
            self.assertFalse(os.path.exists(os.path.join(self.proj, rel)), rel)
        self.assertTrue(os.path.isdir(os.path.join(self.proj, "_inbox")))
        with open(os.path.join(self.proj, "README.md"), encoding="utf-8") as f:
            self.assertNotIn("{{", f.read())

    def test_inbox_is_counted_until_empty_and_is_schema(self):
        inbox = os.path.join(self.proj, "_inbox")
        for name in ("attachment.pdf", "old-drive", "old-drive/scan.docx"):
            full = os.path.join(inbox, name)
            if os.path.splitext(name)[1]:
                open(full, "wb").close()
            else:
                os.makedirs(full)
        code, out = self.diff()
        self.assertEqual(code, 1, out)
        self.assertIn("2 file(s) in _inbox/ awaiting filing (R3)", out)
        self.assertIn("NEW      _inbox/attachment.pdf", out)
        self.assertIn("INBOX     _inbox/old-drive/scan.docx", out)
        # Regeneration baselines the files, indexes them, and still counts them.
        code, out = self.reindex()
        self.assertEqual(code, 0, out)
        self.assertIn("2 file(s) in _inbox/", out)
        with open(os.path.join(self.proj, "00_AI_context", "INDEX.md"),
                  encoding="utf-8") as f:
            self.assertIn("_inbox/attachment.pdf", f.read())
        code, out = self.diff()
        self.assertEqual(code, 0, out)
        self.assertNotIn("NEW", out)
        self.assertIn("2 file(s) in _inbox/", out)
        # Nothing unfiled is extracted: the inbox is not a source zone.
        code, out = self.extract()
        self.assertEqual(code, 0, out)
        self.assertFalse(os.path.exists(os.path.join(
            self.proj, "03_working", "_extracted", "_inbox")))
        self.assertNotIn("_inbox", out)
        # Emptied, the count goes away; removed, the inbox is a missing schema dir.
        shutil.rmtree(inbox)
        code, out = self.diff()
        self.assertNotIn("awaiting filing", out)
        self.assertIn("MISSING DIR  _inbox/", out)
        self.assertEqual(index.missing_dirs(self.proj), ["_inbox"])

    def test_missing_schema_directory_is_reported(self):
        # The bug this pins: the manifest records files, so a directory that
        # held only its .gitkeep — or nothing — vanished without a trace.
        os.rmdir(os.path.join(self.proj, "05_temp"))
        self.assertEqual(index.missing_dirs(self.proj), ["05_temp"])
        code, out = self.diff()
        self.assertEqual(code, 1, out)
        self.assertIn("MISSING DIR  05_temp/", out)
        self.assertIn("1 schema directory missing", out)

    def test_pdf_stub_is_retried_not_cached(self):
        # Runs the real script twice with pypdf hidden, the way a machine
        # without it would.
        pdf = os.path.join(self.proj, "01_basis", "doc.pdf")
        with open(pdf, "wb") as f:
            f.write(b"%PDF-1.4 fixture")
        env_hide = os.path.join(self.tmp, "nopypdf")
        for name in ("pypdf", "PyPDF2"):
            os.makedirs(os.path.join(env_hide, name))
            with open(os.path.join(env_hide, name, "__init__.py"), "w") as f:
                f.write("raise ImportError('hidden for the test')\n")
        env = dict(os.environ, PYTHONPATH=env_hide)

        def go(*extra):
            proc = subprocess.run(
                [sys.executable, os.path.join(self.tools, "extract_text.py"),
                 self.proj, *extra], capture_output=True, text=True, env=env)
            return proc.stdout + proc.stderr

        first = go()
        self.assertIn("1 not extracted (will retry next run)", first)
        self.assertIn("[not-extracted]", first)
        second = go()
        self.assertIn("1 not extracted (will retry next run)", second)
        self.assertNotIn("1 already current", second)
        report = go("--report")
        self.assertIn("not-extracted — STALE (previous attempt failed)", report)

    def test_report_lists_orphans(self):
        docx_md = os.path.join(self.proj, "03_working", "_extracted", "01_basis",
                               "vanished.docx.md")
        os.makedirs(os.path.dirname(docx_md))
        open(docx_md, "w").close()
        code, out = self.extract("--report")
        self.assertEqual(code, 0, out)
        self.assertIn("Orphaned", out)
        self.assertIn("01_basis/vanished.docx.md", out)


if __name__ == "__main__":
    unittest.main()
