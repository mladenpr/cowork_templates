#!/usr/bin/env python3
"""extract_text.py — build the searchable text layer for the frozen zones (R10).

    python3 04_tools/extract_text.py            # extract what is new or changed
    python3 04_tools/extract_text.py --report   # what is filed, and in what state
    python3 04_tools/extract_text.py --force    # re-extract everything
    python3 04_tools/extract_text.py /path/to/repo

On Windows use `py -3` in place of `python3`.

Why this exists
---------------
`INDEX.md` gives one line per file and the `00_AI_context/datasets/` context
files give a paragraph per dataset. For a project made of Word documents, PDFs
and spreadsheets that is the entire searchable surface: an agent cannot grep a
.docx, so every question that needs a number means reopening and reparsing a
binary, and "which document says X" cannot be answered at all without opening
all of them.

This script mirrors the frozen zones — `01_basis/` and `02_exchange/`, both
directions — into `03_working/_extracted/` as one markdown file per source
document, keeping the full zone-relative path so the two cannot collide. The
result is greppable, cheap to read, and rebuilt by one command, so it never
becomes something you have to back up.

It reads only the frozen zones and writes only into `03_working/_extracted/`.
It cannot modify a source document (R1).

The extraction is an index, not a substitute (R10): it drops layout, page
numbers, images and drawings, and reconstructs Word list numbering and Excel
dates rather than reading them. Find things here; read them in the source.
Every extracted file opens with a banner saying so.

Formats
-------
.docx/.dotx  paragraphs, headings, tables, tracked insertions and deletions,
             comments with their authors, and the document's core properties
.xlsx/.xlsm  every sheet, its used range, and its cells rendered as a table,
             with formulas shown alongside their cached results
.pptx/.potx  slide text in slide order, plus speaker notes
.pdf         page-by-page text, if pypdf is installed; flags a PDF that has no
             text layer as needing OCR

Office formats are handled with the standard library alone — .docx, .xlsx and
.pptx are ZIP archives of XML. Nothing needs installing. PDFs are the exception:
they need `pypdf` (`pip install pypdf`). Without it, PDFs still get a stub
recording that they were seen and why they were not read, so the gap is visible
rather than silent.

Rights-managed files
--------------------
An Office document carrying an encrypting sensitivity label ("Confidential",
IRM-protected) is not a ZIP archive at all — it is an OLE compound file that
only authenticated Office can open. No Python library can read it, and neither
can an agent. The script detects this and flags it explicitly instead of
failing with something unhelpful, because in a Microsoft 365 tenant it is the
single most common reason a document cannot be processed.
"""

import argparse
import os
import re
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree as ET

# The frozen zones (R1) are what gets extracted: reference material and both
# directions of the exchange. 03_working/ is not extracted — it is already
# yours, already mutable, and extracting a live draft would only produce a
# stale copy of something that changes hourly.
SOURCE_DIRS = ("01_basis", "02_exchange")
OUT_DIR = os.path.join("03_working", "_extracted")

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
PR = "{http://schemas.openxmlformats.org/package/2006/relationships}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
CP = "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}"
DC = "{http://purl.org/dc/elements/1.1/}"
DCT = "{http://purl.org/dc/terms/}"

WORD_EXT = {".docx", ".docm", ".dotx", ".dotm"}
EXCEL_EXT = {".xlsx", ".xlsm", ".xltx", ".xltm"}
PPT_EXT = {".pptx", ".pptm", ".potx", ".potm"}
PDF_EXT = {".pdf"}
TEXT_EXT = {".txt", ".md", ".csv", ".tsv", ".json", ".xml", ".yml", ".yaml"}
# Extensions worth naming in the report rather than treating as a mystery.
OPAQUE_EXT = {
    ".dwg": "CAD drawing", ".dxf": "CAD exchange", ".dgn": "MicroStation drawing",
    ".ifc": "BIM model", ".rvt": "Revit model", ".png": "image", ".jpg": "image",
    ".jpeg": "image", ".tif": "scan/image", ".tiff": "scan/image",
    ".zip": "archive", ".7z": "archive", ".rar": "archive", ".msg": "Outlook message",
    ".eml": "email", ".doc": "legacy Word (binary)", ".xls": "legacy Excel (binary)",
    ".ppt": "legacy PowerPoint (binary)",
}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_xml(zf, name):
    try:
        return ET.fromstring(zf.read(name))
    except (KeyError, ET.ParseError):
        return None


def squeeze(text):
    return re.sub(r"[ \t]+", " ", (text or "")).strip()


def is_ole(path):
    """True for an OLE compound file — a rights-managed/encrypted Office doc."""
    try:
        with open(path, "rb") as f:
            return f.read(8) == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
    except OSError:
        return False


class Result:
    """What one source document turned into."""

    def __init__(self, extractor):
        self.extractor = extractor
        self.meta = {}
        self.body = []
        self.flags = []

    def line(self, text=""):
        self.body.append(text)

    def flag(self, name):
        if name not in self.flags:
            self.flags.append(name)


# --------------------------------------------------------------------------
# Word
# --------------------------------------------------------------------------

ROMAN = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"),
         (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"),
         (4, "iv"), (1, "i")]


def roman(n):
    out = []
    for value, sym in ROMAN:
        while n >= value:
            out.append(sym)
            n -= value
    return "".join(out)


def format_counter(n, fmt):
    if fmt == "lowerLetter":
        return chr(ord("a") + (n - 1) % 26)
    if fmt == "upperLetter":
        return chr(ord("A") + (n - 1) % 26)
    if fmt == "lowerRoman":
        return roman(n)
    if fmt == "upperRoman":
        return roman(n).upper()
    return str(n)


def load_numbering(zf):
    """{numId: {ilvl: {fmt, text, start}}} from word/numbering.xml."""
    root = read_xml(zf, "word/numbering.xml")
    if root is None:
        return {}
    abstract = {}
    for an in root.findall(f"{W}abstractNum"):
        levels = {}
        for lvl in an.findall(f"{W}lvl"):
            try:
                ilvl = int(lvl.get(f"{W}ilvl", "0"))
            except ValueError:
                continue
            fmt = lvl.find(f"{W}numFmt")
            text = lvl.find(f"{W}lvlText")
            start = lvl.find(f"{W}start")
            levels[ilvl] = {
                "fmt": fmt.get(f"{W}val", "decimal") if fmt is not None else "decimal",
                "text": text.get(f"{W}val", "%1.") if text is not None else "%1.",
                "start": int(start.get(f"{W}val", "1")) if start is not None else 1,
            }
        abstract[an.get(f"{W}abstractNumId")] = levels
    nums = {}
    for n in root.findall(f"{W}num"):
        ref = n.find(f"{W}abstractNumId")
        if ref is not None:
            nums[n.get(f"{W}numId")] = abstract.get(ref.get(f"{W}val"), {})
    return nums


def list_marker(p, numbering, counters):
    """Reconstruct a paragraph's visible list number, or None.

    Word stores the numbering *scheme*, not the numbers — they are computed
    when the document is rendered. Dropping them loses how a specification is
    referenced ("clause 2.1"), so they are rebuilt here for the ordinary case:
    sequential decimal/letter/roman lists with no restarts or per-instance
    overrides. Anything more exotic will be wrong, which is why a document
    using this is flagged for the context md rather than trusted silently.
    """
    pr = p.find(f"{W}pPr")
    if pr is None:
        return None
    num_pr = pr.find(f"{W}numPr")
    if num_pr is None:
        return None
    nid_el = num_pr.find(f"{W}numId")
    if nid_el is None:
        return None
    nid = nid_el.get(f"{W}val")
    ilvl_el = num_pr.find(f"{W}ilvl")
    try:
        ilvl = int(ilvl_el.get(f"{W}val", "0")) if ilvl_el is not None else 0
    except ValueError:
        ilvl = 0
    levels = numbering.get(nid)
    if not levels or ilvl not in levels:
        return None
    spec = levels[ilvl]
    if spec["fmt"] in ("bullet", "none"):
        return "-"
    counters[(nid, ilvl)] = counters.get((nid, ilvl), spec["start"] - 1) + 1
    for key in [k for k in counters if k[0] == nid and k[1] > ilvl]:
        del counters[key]
    text = spec["text"]
    for level in range(9):
        token = f"%{level + 1}"
        if token in text:
            lvl_spec = levels.get(level, spec)
            count = counters.get((nid, level), lvl_spec["start"])
            text = text.replace(token, format_counter(count, lvl_spec["fmt"]))
    return text


def iter_blocks(container):
    """Yield ('p'|'tbl', element) for a container's direct block children.

    Descends into w:sdt content controls, which templates and forms wrap
    blocks in — paragraphs inside one would otherwise be invisible.
    """
    for child in container:
        if child.tag == f"{W}p":
            yield "p", child
        elif child.tag == f"{W}tbl":
            yield "tbl", child
        elif child.tag == f"{W}sdt":
            content = child.find(f"{W}sdtContent")
            if content is not None:
                yield from iter_blocks(content)


def para_segments(p):
    """Text of a paragraph as (kind, text) segments, in document order.

    kind is "t" for normal text and "del" for text struck out by a tracked
    deletion. Insertions carry no marker of their own — they read as normal
    text — but their presence is recorded as a flag on the document.
    """
    segs = []
    for node in p.iter():
        if node.tag == f"{W}t" and node.text:
            segs.append(("t", node.text))
        elif node.tag == f"{W}delText" and node.text:
            segs.append(("del", node.text))
        elif node.tag in (f"{W}tab",):
            segs.append(("t", "\t"))
        elif node.tag in (f"{W}br", f"{W}cr"):
            segs.append(("t", " "))
        elif node.tag == f"{W}footnoteReference":
            segs.append(("t", f"[^{node.get(f'{W}id', '?')}]"))
        elif node.tag == f"{W}endnoteReference":
            segs.append(("t", f"[^e{node.get(f'{W}id', '?')}]"))
    merged = []
    for kind, text in segs:
        if merged and merged[-1][0] == kind:
            merged[-1][1] += text
        else:
            merged.append([kind, text])
    return merged


def para_text(p):
    out = []
    for kind, text in para_segments(p):
        if kind == "del" and text.strip():
            # Keep the surrounding whitespace outside the markers, or the
            # strikethrough does not render.
            lead = text[:len(text) - len(text.lstrip())]
            trail = text[len(text.rstrip()):]
            out.append(f"{lead}~~{text.strip()}~~{trail}")
        else:
            out.append(text)
    return squeeze("".join(out))


def heading_level(p):
    """Outline level first — it survives a localized Word install; style second."""
    pr = p.find(f"{W}pPr")
    if pr is None:
        return 0
    lvl = pr.find(f"{W}outlineLvl")
    if lvl is not None:
        try:
            return min(int(lvl.get(f"{W}val", "9")) + 1, 6)
        except ValueError:
            pass
    style = pr.find(f"{W}pStyle")
    if style is not None:
        val = style.get(f"{W}val", "")
        m = re.match(r"^Heading(\d)$", val)
        if m:
            return min(int(m.group(1)), 6)
        if val in ("Title", "Titel", "Titre"):
            return 1
    return 0


def cell_text(tc):
    """Text of one table cell, keeping a nested table visible as a table.

    Collecting every descendant paragraph instead would silently merge an
    inner table's cells into the outer one, which reads as a single run-on
    value and loses the structure entirely.
    """
    parts = []
    for kind, el in iter_blocks(tc):
        if kind == "p":
            text = para_text(el)
            if text:
                parts.append(text)
        else:
            rows = [" / ".join(cell_text(inner) for inner in tr.findall(f"{W}tc"))
                    for tr in el.findall(f"{W}tr")]
            if rows:
                parts.append("[nested table: " + " ; ".join(rows) + "]")
    return squeeze(" ".join(parts))


def table_markdown(tbl):
    rows = []
    for tr in tbl.findall(f"{W}tr"):
        rows.append([cell_text(tc).replace("|", "\\|")
                     for tc in tr.findall(f"{W}tc")])
    if not rows:
        return []
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |",
           "|" + "|".join([" --- "] * width) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return out


def core_properties(zf):
    root = read_xml(zf, "docProps/core.xml")
    if root is None:
        return {}
    fields = {
        "title": f"{DC}title", "author": f"{DC}creator",
        "last_modified_by": f"{CP}lastModifiedBy", "revision": f"{CP}revision",
        "created": f"{DCT}created", "modified": f"{DCT}modified",
    }
    out = {}
    for key, tag in fields.items():
        node = root.find(tag)
        if node is not None and node.text:
            out[key] = squeeze(node.text)
    return out


def extract_docx(path, res):
    with zipfile.ZipFile(path) as zf:
        res.meta.update(core_properties(zf))
        doc = read_xml(zf, "word/document.xml")
        if doc is None:
            res.flag("unreadable-document.xml")
            return
        body = doc.find(f"{W}body")
        if body is None:
            return

        ins = len(list(doc.iter(f"{W}ins")))
        dele = len(list(doc.iter(f"{W}del")))
        if ins or dele:
            res.flag("tracked-changes")
            res.meta["tracked_insertions"] = ins
            res.meta["tracked_deletions"] = dele

        # Headers and footers carry the document number, revision and any
        # confidentiality marking — in a controlled document that is where
        # the identity lives, not in the body.
        chrome = []
        for name in sorted(n for n in zf.namelist()
                           if re.match(r"word/(header|footer)\d*\.xml$", n)):
            part = read_xml(zf, name)
            if part is None:
                continue
            text = squeeze(" ".join(para_text(p) for p in part.iter(f"{W}p")))
            if text and text not in [t for _, t in chrome]:
                chrome.append((name.split("/")[-1], text))
        if chrome:
            res.line("## Header / footer")
            res.line()
            for name, text in chrome:
                res.line(f"- `{name}`: {text}")
            res.line()

        numbering = load_numbering(zf)
        counters = {}
        numbered = False
        for kind, el in iter_blocks(body):
            if kind == "p":
                text = para_text(el)
                marker = list_marker(el, numbering, counters)
                if not text:
                    continue
                if marker and marker != "-":
                    numbered = True
                    text = f"{marker} {text}"
                elif marker:
                    text = f"- {text}"
                level = heading_level(el)
                res.line(("#" * level + " " + text) if level else text)
                res.line()
            else:
                lines = table_markdown(el)
                if lines:
                    res.body.extend(lines)
                    res.line()
        if numbered:
            res.flag("list-numbering-reconstructed")

        for part_name, label, prefix in (
                ("word/footnotes.xml", "Footnotes", ""),
                ("word/endnotes.xml", "Endnotes", "e")):
            part = read_xml(zf, part_name)
            if part is None:
                continue
            tag = f"{W}footnote" if prefix == "" else f"{W}endnote"
            items = [n for n in part.findall(tag)
                     if n.get(f"{W}type") in (None, "normal")]
            notes = []
            for note in items:
                text = squeeze(" ".join(para_text(p) for p in note.iter(f"{W}p")))
                if text:
                    notes.append((note.get(f"{W}id", "?"), text))
            if not notes:
                continue
            res.flag(label.lower())
            res.meta[label.lower()] = len(notes)
            res.line(f"## {label}")
            res.line()
            for note_id, text in notes:
                res.line(f"[^{prefix}{note_id}]: {text}")
            res.line()

        comments = read_xml(zf, "word/comments.xml")
        if comments is not None:
            items = comments.findall(f"{W}comment")
            if items:
                res.flag("comments")
                res.meta["comments"] = len(items)
                res.line("## Comments")
                res.line()
                for c in items:
                    who = c.get(f"{W}author", "?")
                    when = (c.get(f"{W}date", "") or "")[:10]
                    text = squeeze(" ".join(para_text(p) for p in c.iter(f"{W}p")))
                    res.line(f"- **{who}**{f' ({when})' if when else ''}: {text}")
                res.line()


# --------------------------------------------------------------------------
# Excel
# --------------------------------------------------------------------------

def shared_strings(zf):
    root = read_xml(zf, "xl/sharedStrings.xml")
    if root is None:
        return []
    out = []
    for si in root.findall(f"{S}si"):
        out.append(squeeze("".join(t.text or "" for t in si.iter(f"{S}t"))))
    return out


def sheet_targets(zf):
    """[(sheet name, part path, hidden)] in workbook order."""
    wb = read_xml(zf, "xl/workbook.xml")
    rels = read_xml(zf, "xl/_rels/workbook.xml.rels")
    if wb is None or rels is None:
        return []
    by_id = {r.get("Id"): r.get("Target") for r in rels.findall(f"{PR}Relationship")}
    out = []
    sheets = wb.find(f"{S}sheets")
    for sh in (sheets if sheets is not None else []):
        target = by_id.get(sh.get(f"{R}id"), "")
        if not target:
            continue
        if not target.startswith("/"):
            target = "xl/" + target.lstrip("./")
        out.append((sh.get("name", "?"), target.lstrip("/"),
                    sh.get("state", "visible") != "visible"))
    return out


def col_index(ref):
    letters = re.match(r"([A-Z]+)", ref or "")
    if not letters:
        return 0
    n = 0
    for ch in letters.group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


# Excel's built-in date and date-time number formats.
BUILTIN_DATE_IDS = (set(range(14, 23)) | set(range(27, 37))
                    | {45, 46, 47} | set(range(50, 59)))


def load_number_formats(zf):
    """(numFmtId per cell-style index, {numFmtId: formatCode})."""
    root = read_xml(zf, "xl/styles.xml")
    if root is None:
        return [], {}
    custom = {}
    fmts = root.find(f"{S}numFmts")
    if fmts is not None:
        for nf in fmts.findall(f"{S}numFmt"):
            try:
                custom[int(nf.get("numFmtId"))] = nf.get("formatCode", "")
            except (TypeError, ValueError):
                pass
    xfs = []
    cell_xfs = root.find(f"{S}cellXfs")
    if cell_xfs is not None:
        for xf in cell_xfs.findall(f"{S}xf"):
            try:
                xfs.append(int(xf.get("numFmtId", "0")))
            except ValueError:
                xfs.append(0)
    return xfs, custom


def is_date_style(style_index, xfs, custom):
    if style_index is None:
        return False
    try:
        idx = int(style_index)
    except ValueError:
        return False
    if idx >= len(xfs):
        return False
    fmt_id = xfs[idx]
    if fmt_id in BUILTIN_DATE_IDS:
        return True
    # Strip literals and colour/condition brackets before looking for date
    # placeholders, so a format like `#,##0 "days"` is not mistaken for one.
    code = re.sub(r'\[[^\]]*\]|"[^"]*"', "", custom.get(fmt_id, ""))
    return bool(re.search(r"[yd]", code, re.I))


def excel_date(raw):
    """Excel serial → ISO date. Serial 60 is Excel's fictional 1900-02-29."""
    try:
        serial = float(raw)
    except (TypeError, ValueError):
        return None
    if serial <= 0:
        return None
    base = datetime(1899, 12, 30) if serial > 59 else datetime(1899, 12, 31)
    dt = base + timedelta(days=serial)
    if abs(serial - round(serial)) < 1e-9:
        return dt.strftime("%Y-%m-%d")
    return dt.strftime("%Y-%m-%d %H:%M")


def cell_value(c, strings, xfs=(), custom=None):
    kind = c.get("t", "n")
    if kind == "inlineStr":
        node = c.find(f"{S}is")
        return squeeze("".join(t.text or "" for t in node.iter(f"{S}t"))) if node is not None else ""
    v = c.find(f"{S}v")
    raw = v.text if v is not None and v.text else ""
    if kind == "s":
        try:
            return strings[int(raw)]
        except (ValueError, IndexError):
            return ""
    if kind == "b":
        return "TRUE" if raw == "1" else "FALSE"
    if kind == "n" and raw and is_date_style(c.get("s"), xfs, custom or {}):
        as_date = excel_date(raw)
        if as_date:
            return as_date
    return squeeze(raw)


def extract_xlsx(path, res, max_rows):
    with zipfile.ZipFile(path) as zf:
        res.meta.update(core_properties(zf))
        strings = shared_strings(zf)
        xfs, custom = load_number_formats(zf)
        sheets = sheet_targets(zf)
        res.meta["sheets"] = len(sheets)
        formulas = 0
        styled_without_formats = False

        for name, part, hidden in sheets:
            root = read_xml(zf, part)
            res.line(f"## Sheet: {name}" + (" (hidden)" if hidden else ""))
            res.line()
            if root is None:
                res.line("_Sheet could not be read._")
                res.line()
                continue
            dim = root.find(f"{S}dimension")
            if dim is not None and dim.get("ref"):
                res.line(f"Used range: `{dim.get('ref')}`")
                res.line()
            # A merged range means the value sits in the top-left cell and the
            # rest are empty — without this the table below looks misaligned.
            merges = [mc.get("ref") for mc in root.iter(f"{S}mergeCell")
                      if mc.get("ref")]
            if merges:
                res.line(f"Merged ranges: {', '.join(merges)}")
                res.line()

            grid, sheet_formulas = [], []
            for row in root.iter(f"{S}row"):
                cells = {}
                for c in row.findall(f"{S}c"):
                    idx = col_index(c.get("r", ""))
                    value = cell_value(c, strings, xfs, custom)
                    f = c.find(f"{S}f")
                    if f is not None:
                        formulas += 1
                        sheet_formulas.append(
                            (c.get("r", "?"), squeeze(f.text or ""), value))
                    if value != "":
                        cells[idx] = value
                        if c.get("s") and not xfs:
                            styled_without_formats = True
                if cells:
                    width = max(cells) + 1
                    grid.append([cells.get(i, "") for i in range(width)])

            if not grid:
                res.line("_Empty sheet._")
                res.line()
                continue

            shown = grid[:max_rows]
            width = max(len(r) for r in shown)
            for r in shown:
                r += [""] * (width - len(r))
            res.line("| " + " | ".join(
                c.replace("|", "\\|") for c in shown[0]) + " |")
            res.line("|" + "|".join([" --- "] * width) + "|")
            for r in shown[1:]:
                res.line("| " + " | ".join(
                    c.replace("|", "\\|") for c in r) + " |")
            res.line()
            if len(grid) > max_rows:
                res.flag("truncated")
                res.line(f"_{len(grid) - max_rows} further rows not shown "
                         f"(--max-rows {max_rows})._")
                res.line()
            if sheet_formulas:
                res.line(f"<details><summary>{len(sheet_formulas)} formulas"
                         f"</summary>")
                res.line()
                for ref, formula, value in sheet_formulas[:max_rows]:
                    res.line(f"- `{ref}` = `={formula}` → {value}")
                res.line()
                res.line("</details>")
                res.line()

        if formulas:
            res.meta["formulas"] = formulas
        if styled_without_formats:
            res.flag("number-formats-unavailable-dates-may-be-serials")


# --------------------------------------------------------------------------
# PowerPoint
# --------------------------------------------------------------------------

def slide_order(zf):
    pres = read_xml(zf, "ppt/presentation.xml")
    rels = read_xml(zf, "ppt/_rels/presentation.xml.rels")
    if pres is None or rels is None:
        names = [n for n in zf.namelist()
                 if re.match(r"ppt/slides/slide\d+\.xml$", n)]
        return sorted(names, key=lambda n: int(re.search(r"(\d+)", n).group(1)))
    by_id = {r.get("Id"): r.get("Target") for r in rels.findall(f"{PR}Relationship")}
    out = []
    lst = pres.find(f"{P}sldIdLst")
    for sld in (lst if lst is not None else []):
        target = by_id.get(sld.get(f"{R}id"), "")
        if target:
            out.append("ppt/" + target.lstrip("./"))
    return out


def extract_pptx(path, res):
    with zipfile.ZipFile(path) as zf:
        res.meta.update(core_properties(zf))
        slides = slide_order(zf)
        res.meta["slides"] = len(slides)
        for i, part in enumerate(slides, 1):
            root = read_xml(zf, part)
            res.line(f"## Slide {i}")
            res.line()
            if root is None:
                res.line("_Slide could not be read._")
                res.line()
                continue
            for para in root.iter(f"{A}p"):
                text = squeeze("".join(t.text or "" for t in para.iter(f"{A}t")))
                if text:
                    res.line(f"- {text}")
            res.line()
            rels = read_xml(zf, os.path.join(
                os.path.dirname(part), "_rels",
                os.path.basename(part) + ".rels").replace(os.sep, "/"))
            if rels is None:
                continue
            for rel in rels.findall(f"{PR}Relationship"):
                if "notesSlide" not in (rel.get("Type") or ""):
                    continue
                notes = read_xml(zf, "ppt/notesSlides/" +
                                 os.path.basename(rel.get("Target", "")))
                if notes is None:
                    continue
                text = squeeze(" ".join(t.text or "" for t in notes.iter(f"{A}t")))
                # The notes part repeats the slide number placeholder; drop it
                # when it is all that is there.
                if text and text != str(i):
                    res.line(f"> Notes: {text}")
                    res.line()


# --------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------

def load_pypdf():
    try:
        from pypdf import PdfReader
        return PdfReader
    except ImportError:
        pass
    try:
        from PyPDF2 import PdfReader
        return PdfReader
    except ImportError:
        return None


def extract_pdf(path, res, reader_cls):
    if reader_cls is None:
        res.extractor = "none (pypdf not installed)"
        res.flag("not-extracted")
        res.line("PDF text was not extracted: no PDF library is available.")
        res.line()
        res.line("Install one and re-run: `pip install pypdf`.")
        return
    reader = reader_cls(path)
    if getattr(reader, "is_encrypted", False):
        try:
            reader.decrypt("")
        except Exception:
            pass
        if getattr(reader, "is_encrypted", False):
            res.flag("encrypted")
            res.line("PDF is encrypted and could not be opened without a password.")
            return
    pages = list(reader.pages)
    res.meta["pages"] = len(pages)
    total = 0
    for i, page in enumerate(pages, 1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            text = ""
            res.flag("page-extract-error")
            res.line(f"## Page {i}")
            res.line()
            res.line(f"_Extraction failed: {exc}_")
            res.line()
            continue
        total += len(text.strip())
        res.line(f"## Page {i}")
        res.line()
        res.line(text.strip() or "_(no text layer on this page)_")
        res.line()
    if pages and total / len(pages) < 50:
        res.flag("likely-scanned-needs-ocr")


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

def classify(ext):
    if ext in WORD_EXT:
        return "docx"
    if ext in EXCEL_EXT:
        return "xlsx"
    if ext in PPT_EXT:
        return "pptx"
    if ext in PDF_EXT:
        return "pdf"
    if ext in TEXT_EXT:
        return "text"
    return "opaque"


def extract_one(path, kind, max_rows, reader_cls):
    res = Result(kind)
    if kind in ("docx", "xlsx", "pptx"):
        if is_ole(path):
            res.flag("rights-managed-or-encrypted")
            res.extractor = "none (OLE compound file, not an Office package)"
            res.line("This file carries an encrypting sensitivity label "
                     "(Confidential / IRM) or a password.")
            res.line()
            res.line("Such a file can only be opened by authenticated Office — "
                     "no Python library and no agent can read it. Save a "
                     "decrypted copy into `03_working/` for analysis, or "
                     "record in the dataset's context md that the content is "
                     "unavailable and why.")
            return res
        if not zipfile.is_zipfile(path):
            res.flag("not-a-valid-office-file")
            res.extractor = "none (not a ZIP package)"
            res.line("This file has an Office extension but is not a valid "
                     "Office package — it is empty, truncated, or misnamed.")
            res.line()
            res.line("Check it against what was actually received. A zero-byte "
                     "or truncated file in a frozen zone usually means a sync that "
                     "never completed (R9).")
            return res
    try:
        if kind == "docx":
            extract_docx(path, res)
        elif kind == "xlsx":
            extract_xlsx(path, res, max_rows)
        elif kind == "pptx":
            extract_pptx(path, res)
        elif kind == "pdf":
            extract_pdf(path, res, reader_cls)
    except Exception as exc:
        res.flag("extract-error")
        res.line(f"_Extraction failed: {type(exc).__name__}: {exc}_")
    return res


def front_matter(rel, st, res):
    lines = ["---", f"source: {rel}", f"source_size: {st.st_size}",
             f"source_mtime: {round(st.st_mtime, 2)}", f"extracted: {now()}",
             f"extractor: {res.extractor}"]
    for key, value in res.meta.items():
        lines.append(f"{key}: {value}")
    if res.flags:
        lines.append("flags: " + ", ".join(res.flags))
    lines.append("---")
    lines.append("")
    lines.append(f"> Derived copy of `{rel}` — an index for finding things, not "
                 f"a substitute for the document. Extraction drops layout, page "
                 f"numbers, images and drawings, and reconstructs some features "
                 f"(list numbering, dates) rather than reading them. Verify any "
                 f"figure or quotation against the source before it enters a "
                 f"deliverable.")
    return lines


def read_front_matter(path):
    out = {}
    try:
        with open(path, encoding="utf-8") as f:
            if f.readline().strip() != "---":
                return out
            for line in f:
                line = line.rstrip("\n")
                if line.strip() == "---":
                    break
                if ":" in line:
                    key, _, value = line.partition(":")
                    out[key.strip()] = value.strip()
    except OSError:
        pass
    return out


def is_current(out_path, st):
    fm = read_front_matter(out_path)
    return (fm.get("source_size") == str(st.st_size)
            and fm.get("source_mtime") == str(round(st.st_mtime, 2)))


def sources(root):
    for zone in SOURCE_DIRS:
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, zone)):
            dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
            for fn in sorted(filenames):
                if fn.startswith((".", "~")) or fn.lower().endswith(".tmp"):
                    continue
                full = os.path.join(dirpath, fn)
                if not os.path.isfile(full):
                    continue
                yield full, os.path.relpath(full, root).replace(os.sep, "/")


def output_path(root, rel):
    """Mirror the full zone-relative path so the two zones cannot collide."""
    return os.path.join(root, OUT_DIR, rel + ".md")


def report(root, reader_cls):
    rows = []
    for full, rel in sources(root):
        ext = os.path.splitext(full)[1].lower()
        kind = classify(ext)
        out_path = output_path(root, rel)
        if kind == "text":
            state = "already text"
        elif kind == "opaque":
            state = f"not extractable ({OPAQUE_EXT.get(ext, ext or 'unknown')})"
        elif not os.path.exists(out_path):
            state = "NOT EXTRACTED"
        else:
            fm = read_front_matter(out_path)
            flags = fm.get("flags", "")
            state = flags if flags else "extracted"
            if not is_current(out_path, os.stat(full)):
                state += " — STALE"
        rows.append((rel, state))
    if not rows:
        print(f"No files under {' / '.join(SOURCE_DIRS)}.")
        return 0
    width = max(len(r[0]) for r in rows)
    print(f"{'source'.ljust(width)}  state")
    print(f"{'-' * width}  {'-' * 40}")
    for rel, state in rows:
        print(f"{rel.ljust(width)}  {state}")
    if reader_cls is None and any(r[0].lower().endswith(".pdf") for r in rows):
        print("\npypdf is not installed — PDFs cannot be read. `pip install pypdf`.")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="Extract the frozen zones into a searchable text layer.")
    ap.add_argument("root", nargs="?",
                    help="repo root (default: this script's parent's parent)")
    ap.add_argument("--force", action="store_true",
                    help="re-extract even when the output is current")
    ap.add_argument("--report", action="store_true",
                    help="list SoT files and their extraction state; write nothing")
    ap.add_argument("--max-rows", type=int, default=200,
                    help="rows per spreadsheet sheet to render (default 200)")
    args = ap.parse_args()

    root = (os.path.abspath(os.path.expanduser(args.root)) if args.root
            else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not any(os.path.isdir(os.path.join(root, z)) for z in SOURCE_DIRS):
        sys.exit(f"No frozen zones ({' / '.join(SOURCE_DIRS)}) under {root}")

    reader_cls = load_pypdf()
    if args.report:
        return report(root, reader_cls)

    written = skipped = 0
    flagged = []
    for full, rel in sources(root):
        kind = classify(os.path.splitext(full)[1].lower())
        if kind in ("text", "opaque"):
            continue
        out_path = output_path(root, rel)
        st = os.stat(full)
        if not args.force and os.path.exists(out_path) and is_current(out_path, st):
            skipped += 1
            continue
        res = extract_one(full, kind, args.max_rows, reader_cls)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(front_matter(rel, st, res) + [""] + res.body) + "\n")
        written += 1
        if res.flags:
            flagged.append((rel, ", ".join(res.flags)))

    print(f"Extracted {written} file(s), {skipped} already current → {OUT_DIR}/")
    if flagged:
        print("\nFlagged — record these in the dataset's context md (R2):")
        for rel, flags in flagged:
            print(f"  {rel}  [{flags}]")
    if written:
        print("\nRun update_index.py to bring INDEX.md and MANIFEST.json up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
