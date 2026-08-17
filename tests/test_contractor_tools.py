"""Regression tests for templates/cowork-contractor/05_tools/.

    python3 -m unittest discover tests          # from the repository root

Standard library only. Every test instantiates the template into a temporary
directory with bin/new_project.py and drives the real scripts, so what is
tested is what a project actually gets. The extraction engine is shared with
cowork-consultant and pinned by test_consultant_tools.py; this file covers the
exchange log (log.py), and the parts of the scan that only this template has —
the inbox, the log exemption, the temp skip, the contract zone.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "templates", "cowork-contractor", "05_tools")
NEW_PROJECT = os.path.join(ROOT, "bin", "new_project.py")


def load(name):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(TOOLS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


log = load("log")
index = load("update_index")


def run(*argv, cwd=None):
    proc = subprocess.run([sys.executable, *argv], cwd=cwd, capture_output=True,
                          text=True)
    return proc.returncode, proc.stdout + proc.stderr


class Project(unittest.TestCase):
    """A freshly instantiated contractor project, per test."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.proj = os.path.join(self.tmp, "proj")
        code, out = run(NEW_PROJECT, self.proj, "--name", "Fixture",
                        "--template", "cowork-contractor", "--client", "ACME Ltd")
        self.assertEqual(code, 0, out)
        self.tools = os.path.join(self.proj, "05_tools")
        self.jsonl = os.path.join(self.proj, "03_exchange", "LOG.jsonl")
        self.md = os.path.join(self.proj, "03_exchange", "LOG.md")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    # -- helpers ------------------------------------------------------------

    def path(self, *parts):
        return os.path.join(self.proj, *parts)

    def touch(self, rel, content=b"x"):
        full = self.path(*rel.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as f:
            f.write(content)
        return rel

    def log(self, *args):
        return run(os.path.join(self.tools, "log.py"), *args, cwd=self.proj)

    def add(self, *args, expect=0):
        code, out = self.log("add", *args)
        self.assertEqual(code, expect, out)
        return out

    def rows(self):
        with open(self.jsonl, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]

    def read(self, rel):
        with open(self.path(*rel.split("/")), encoding="utf-8") as f:
            return f.read()

    def diff(self):
        return run(os.path.join(self.tools, "update_index.py"), self.proj, "--diff")

    def reindex(self):
        return run(os.path.join(self.tools, "update_index.py"), self.proj)

    def add_party(self, label):
        """Append a party row to PARTIES.md's Register table."""
        p = self.path("00_AI_context", "PARTIES.md")
        with open(p, encoding="utf-8") as f:
            text = f.read()
        marker = "| Label | Full name | Tier | Role | Contract | Typical traffic | Notes |\n|---|---|---|---|---|---|---|\n"
        self.assertIn(marker, text)
        text = text.replace(marker, marker + f"| {label} | {label} plc | upstream | | | | |\n")
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)

    def letter_in(self, party="ACME", name="2026-03-04_letter.pdf", **kw):
        rel = self.touch(f"03_exchange/received/{party}/{name}")
        args = ["--date", "2026-03-04", "--dir", "in", "--party", party,
                "--type", "letter", "--doc", "A letter", "--path", rel]
        for k, v in kw.items():
            args += [f"--{k}", v]
        return rel, args


# --------------------------------------------------------------------------
# instantiation
# --------------------------------------------------------------------------

class Instantiation(Project):

    def test_fresh_project_is_clean_and_seeded(self):
        code, out = self.diff()
        self.assertEqual(code, 0, out)
        self.assertIn("Clean", out)
        self.assertEqual(index.missing_dirs(self.proj), [])
        for rel in ("VERSION", "02_basis/.gitkeep", "_inbox/.gitkeep"):
            self.assertFalse(os.path.exists(self.path(*rel.split("/"))), rel)
        for rel in ("CLAUDE.md", "README.md", "00_AI_context/PARTIES.md",
                    "03_exchange/LOG.md", "00_AI_context/INDEX.md"):
            self.assertNotIn("{{", self.read(rel), rel)
        # The seeded descriptions survive the first regeneration.
        idx = self.read("00_AI_context/INDEX.md")
        self.assertIn("- `05_tools/log.py` — add, set, query, check", idx)
        self.assertIn("- `CLAUDE.md` — session bootstrap", idx)
        # The client is a full name, not a label — labels are chosen once.
        parties = self.read("00_AI_context/PARTIES.md")
        self.assertIn("|  | ACME Ltd | upstream |", parties)

    def test_empty_log_is_a_healthy_state(self):
        code, out = self.log("query", "--action", "open")
        self.assertEqual(code, 0, out)
        self.assertIn("No matching events", out)
        code, out = self.log("check")
        self.assertEqual(code, 0, out)
        self.assertIn("consistent", out)
        code, out = self.log("query", "--json")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out), [])


# --------------------------------------------------------------------------
# log.py — what add refuses
# --------------------------------------------------------------------------

class AddRefuses(Project):

    def refused(self, *args, saying=""):
        before_jsonl = os.path.getsize(self.jsonl)
        before_md = self.read("03_exchange/LOG.md")
        code, out = self.log("add", *args)
        self.assertEqual(code, 1, out)
        self.assertIn("nothing was written", out)
        if saying:
            self.assertIn(saying, out)
        # Refusal is total: neither file moved.
        self.assertEqual(os.path.getsize(self.jsonl), before_jsonl)
        self.assertEqual(self.read("03_exchange/LOG.md"), before_md)
        return out

    def test_path_is_required(self):
        self.refused("--date", "2026-03-04", "--dir", "in", "--party", "ACME",
                     "--doc", "x", saying="--path is required")

    def test_date_is_required_and_real(self):
        rel, args = self.letter_in()
        code, out = self.log("add", *[a for a in args if a not in ("--date", "2026-03-04")])
        self.assertEqual(code, 2, out)          # argparse: required argument
        for bad in ("2026-99-99", "2026-02-30", "4/3/2026", "yesterday"):
            args[1] = bad
            self.refused(*args, saying="real ISO date")

    def test_status_and_action_are_controlled(self):
        rel, args = self.letter_in()
        self.refused(*args, "--status", "banana", saying="--status must be")
        self.refused(*args, "--action", "maybe", saying="--action must be")
        self.refused(*args, "--due", "2026-13-01", saying="--due must be")

    def test_path_must_stay_inside_the_repository(self):
        rel, args = self.letter_in()
        for bad in ("/etc/hostname", "../outside.pdf",
                    "03_exchange/../../outside.pdf", "C:/x/y.pdf"):
            args[-1] = bad
            self.refused(*args, saying="inside the repository")

    def test_path_must_exist_unless_pending(self):
        rel, args = self.letter_in()
        args[-1] = "03_exchange/received/ACME/not-there.pdf"
        self.refused(*args, saying="no file at")
        self.add(*args, "--pending")
        self.assertEqual(self.rows()[0]["path"], "03_exchange/received/ACME/not-there.pdf")

    def test_direction_and_party_must_match_the_folder(self):
        # The row and the tree agree by construction (R1): received/ is in,
        # issued/ is out, and the party folder is the party.
        rel = self.touch("03_exchange/received/ACME/x.pdf")
        base = ["--date", "2026-03-04", "--doc", "x", "--path", rel]
        self.refused("--dir", "out", "--party", "ACME", *base,
                     saying="direction is the folder")
        self.refused("--dir", "in", "--party", "BOB", *base,
                     saying="label and the folder must agree")
        rel2 = self.touch("03_exchange/stray.pdf")
        self.refused("--dir", "in", "--party", "ACME", *base[:-1], rel2,
                     saying="received/<party>/")

    def test_supersedes_and_answers_are_preflighted(self):
        # The bug this pins: the new row used to be appended, and only then
        # did the missing target fail — half an operation, and a retry
        # double-logged.
        rel, args = self.letter_in()
        self.refused(*args, "--supersedes", "99", saying="--supersedes #99: no such event")
        self.refused(*args, "--answers", "7", saying="--answers #7: no such event")
        self.assertEqual(self.rows(), [])


# --------------------------------------------------------------------------
# log.py — what add and set do
# --------------------------------------------------------------------------

class AddAndSet(Project):

    def test_open_answered_superseded_chain(self):
        self.add_party("ACME")
        rel, args = self.letter_in(action="open", due="2026-04-01", thread="delay")
        out = self.add(*args)
        self.assertNotIn("warning", out)         # party is in PARTIES.md
        a = self.touch("03_exchange/issued/ACME/L-001-A.pdf")
        self.add("--date", "2026-03-10", "--dir", "out", "--party", "ACME",
                 "--type", "letter", "--doc", "Reply", "--rev", "A", "--path", a,
                 "--thread", "delay", "--answers", "1")
        b = self.touch("03_exchange/issued/ACME/L-001-B.pdf")
        out = self.add("--date", "2026-03-12", "--dir", "out", "--party", "ACME",
                       "--type", "letter", "--doc", "Reply", "--rev", "B", "--path", b,
                       "--thread", "delay", "--supersedes", "2", "--backfilled")
        self.assertIn("#2 → superseded by #3", out)
        r1, r2, r3 = self.rows()
        self.assertEqual(r1["action"], "answered by #2")
        self.assertEqual(r1["status"], "current")           # still current
        self.assertEqual(r2["status"], "superseded by #3")
        self.assertEqual(r2["history"][0]["field"], "status")
        self.assertEqual(r2["history"][0]["from"], "current")
        self.assertTrue(r3["backfilled"])
        self.assertFalse(r1["backfilled"])
        for r in (r1, r2, r3):
            self.assertRegex(r["recorded"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        md = self.read("03_exchange/LOG.md")
        self.assertIn("| 1 | 2026-03-04 | in | ACME | letter | A letter |", md)
        self.assertIn("current · answered by #2", md)
        self.assertIn("superseded by #3", md)
        self.assertIn("2026-03-12 †", md)
        self.assertIn("† backfilled", md)
        self.assertIn("Nothing open.", md)
        # Prose outside the generated block survives rendering.
        self.assertIn("**This file is a view. `LOG.jsonl` is the record.**", md)

    def test_outstanding_is_split_by_who_owes(self):
        rel, args = self.letter_in(action="open", due="2026-05-01")
        self.add(*args)
        q = self.touch("03_exchange/issued/ACME/Q-1.pdf")
        self.add("--date", "2026-03-05", "--dir", "out", "--party", "ACME",
                 "--doc", "Question", "--path", q, "--action", "open")
        md = self.read("03_exchange/LOG.md")
        we = md.index("### We owe a reply")
        they = md.index("### They owe a reply")
        self.assertLess(we, md.index("**#1** 2026-03-04 ACME: A letter — due 2026-05-01"))
        self.assertLess(md.index("**#1**"), they)
        self.assertLess(they, md.index("**#2** 2026-03-05 ACME: Question"))
        code, out = self.log("query", "--action", "open")
        self.assertIn("2 event(s)", out)

    def test_warnings_do_not_block(self):
        rel, args = self.letter_in()
        out = self.add(*args, "--type", "carrier-pigeon")
        self.assertIn("warning: 'carrier-pigeon' is not one of the usual types", out)
        self.assertIn("warning: 'ACME' is not a label", out)
        self.assertEqual(len(self.rows()), 1)

    def test_set_changes_only_what_may_change(self):
        rel, args = self.letter_in(action="open")
        self.add(*args)
        # A path is fixed once set.
        code, out = self.log("set", "1", "--path", "03_exchange/received/ACME/other.pdf")
        self.assertEqual(code, 1, out)
        self.assertIn("already has a path", out)
        # Notes append; status/action/due are validated; history records all.
        code, out = self.log("set", "1", "--note", "first")
        self.assertEqual(code, 0, out)
        code, out = self.log("set", "1", "--note", "second", "--action", "closed",
                             "--due", "")
        self.assertEqual(code, 0, out)
        r = self.rows()[0]
        self.assertEqual(r["note"], "first | second")
        self.assertEqual(r["action"], "closed")
        # Within one call fields apply in a fixed order: status, action, due,
        # path, note. --due "" on an empty due is no change and is not recorded.
        self.assertEqual([h["field"] for h in r["history"]],
                         ["note", "action", "note"])
        code, out = self.log("set", "1", "--status", "superseded by #40")
        self.assertEqual(code, 1, out)
        self.assertIn("cites #40, which does not exist", out)
        code, out = self.log("set", "1", "--action", "done")
        self.assertEqual(code, 1, out)
        code, out = self.log("set", "1")
        self.assertEqual(code, 1, out)
        self.assertIn("Nothing to change", out)
        code, out = self.log("set", "9")
        self.assertEqual(code, 1, out)
        self.assertIn("No event #9", out)

    def test_pending_path_is_filled_once(self):
        self.add("--date", "2026-03-04", "--dir", "out", "--party", "ACME",
                 "--doc", "Coming", "--pending")
        self.assertEqual(self.rows()[0]["path"], "")
        code, out = self.log("check")
        self.assertIn("NO PATH", out)
        # Filling it is validated like any path: folder must match the row.
        wrong = self.touch("03_exchange/received/ACME/coming.pdf")
        code, out = self.log("set", "1", "--path", wrong)
        self.assertEqual(code, 1, out)
        self.assertIn("direction is the folder", out)
        right = self.touch("03_exchange/issued/ACME/coming.pdf")
        code, out = self.log("set", "1", "--path", right)
        self.assertEqual(code, 0, out)
        self.assertEqual(self.rows()[0]["path"], right)
        self.assertEqual(self.rows()[0]["history"][0]["field"], "path")

    def test_query_filters_and_json(self):
        rel, args = self.letter_in(action="open", due="2020-01-01", thread="t1")
        self.add(*args)
        b = self.touch("03_exchange/received/BOB/b.pdf")
        self.add("--date", "2026-03-06", "--dir", "in", "--party", "BOB",
                 "--doc", "Other", "--path", b, "--thread", "t2")
        code, out = self.log("query", "--party", "acme")     # case-insensitive
        self.assertIn("1 event(s)", out)
        code, out = self.log("query", "--overdue")
        self.assertIn("#1", out)
        self.assertNotIn("#2", out)
        code, out = self.log("query", "--since", "2026-03-05", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual([r["id"] for r in data], [2])
        code, out = self.log("query", "--grep", "other", "--paths")
        self.assertIn(b, out)
        code, out = self.log("query", "--thread", "nope")
        self.assertEqual(code, 0, out)


# --------------------------------------------------------------------------
# log.py — check, and the record's integrity
# --------------------------------------------------------------------------

class Check(Project):

    def test_unlogged_files_and_folder_coverage(self):
        self.add_party("ACME")
        self.touch("03_exchange/received/ACME/stray.pdf")
        self.touch("01_contract/upstream/contract.pdf")
        self.touch("02_basis/BS-EN-1992.pdf")            # basis: no row expected
        code, out = self.log("check")
        self.assertEqual(code, 1, out)
        self.assertIn("UNLOGGED (2)", out)
        self.assertIn("03_exchange/received/ACME/stray.pdf", out)
        self.assertIn("01_contract/upstream/contract.pdf", out)
        self.assertNotIn("02_basis", out)
        # A folder as path covers everything under it — one transmittal, many
        # drawings.
        self.touch("03_exchange/received/ACME/T-014/dwg-1.pdf")
        self.touch("03_exchange/received/ACME/T-014/dwg-2.pdf")
        self.add("--date", "2026-03-04", "--dir", "in", "--party", "ACME",
                 "--type", "transmittal", "--doc", "T-014",
                 "--path", "03_exchange/received/ACME/T-014")
        self.add("--date", "2026-03-01", "--dir", "in", "--party", "ACME",
                 "--type", "contract", "--doc", "Executed contract",
                 "--path", "01_contract/upstream/contract.pdf")
        code, out = self.log("check")
        self.assertIn("UNLOGGED (1)", out)
        self.assertNotIn("T-014/dwg", out)
        # An issued PDF's source, beside it under the same stem (R10), is part
        # of the same event — not a second, unlogged file.
        pdf = self.touch("03_exchange/issued/ACME/L-0088-A.pdf")
        self.touch("03_exchange/issued/ACME/L-0088-A.docx")
        self.touch("03_exchange/issued/ACME/L-0088-B.docx")
        self.add("--date", "2026-03-09", "--dir", "out", "--party", "ACME",
                 "--type", "letter", "--doc", "Reply", "--rev", "A", "--path", pdf)
        code, out = self.log("check")
        self.assertNotIn("L-0088-A.docx", out)
        self.assertIn("L-0088-B.docx", out)

    def test_drift_after_the_fact(self):
        rel, args = self.letter_in(action="open", due="2020-01-01")
        self.add(*args)
        os.remove(self.path(*rel.split("/")))
        code, out = self.log("check")
        self.assertEqual(code, 1, out)
        self.assertIn("PATH MISSING (1)", out)
        self.assertIn("OVERDUE (1)", out)
        self.assertIn("UNKNOWN PARTY (1)", out)
        self.add_party("ACME")
        code, out = self.log("check")
        self.assertNotIn("UNKNOWN PARTY", out)

    def test_hand_damage_is_reported_not_repaired(self):
        rel, args = self.letter_in()
        self.add(*args)
        r = self.rows()[0]
        dup = dict(r, doc="Duplicate id")
        bad = dict(r, id=2, status="superseded by #77", action="answered by #78",
                   dir="out", path="03_exchange/received/ACME/2026-03-04_letter.pdf")
        with open(self.jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(dup) + "\n" + json.dumps(bad) + "\n")
        code, out = self.log("check")
        self.assertEqual(code, 1, out)
        self.assertIn("DUPLICATE ID (1)", out)
        self.assertIn("#1 appears 2 times", out)
        self.assertIn("DANGLING (2)", out)
        self.assertIn("cites #77", out)
        self.assertIn("ROW/TREE DISAGREE", out)
        self.assertEqual(len(self.rows()), 3)          # nothing was rewritten

    def test_malformed_jsonl_is_fatal_and_untouched(self):
        rel, args = self.letter_in()
        self.add(*args)
        with open(self.jsonl, "a", encoding="utf-8") as f:
            f.write("{not json\n")
        size = os.path.getsize(self.jsonl)
        for cmd in (["query"], ["check"], ["render"], ["set", "1", "--action", "closed"]):
            code, out = self.log(*cmd)
            self.assertEqual(code, 1, cmd)
            self.assertIn("LOG.jsonl:2 is not valid JSON", out)
            self.assertIn("do not delete it", out)
        self.assertEqual(os.path.getsize(self.jsonl), size)

    def test_writes_are_atomic_and_leave_no_temp_file(self):
        rel, args = self.letter_in()
        self.add(*args)
        self.log("set", "1", "--action", "closed")
        listing = os.listdir(self.path("03_exchange"))
        self.assertNotIn("LOG.jsonl.tmp", listing)
        self.assertNotIn("LOG.md.tmp", listing)
        code, out = self.diff()
        # The log changing is the ordinary case, never the frozen-zone alarm.
        self.assertNotIn("FROZEN ZONE MOVED", out)
        self.assertIn("CHANGED  03_exchange/LOG.jsonl", out)


class Units(unittest.TestCase):

    def test_valid_date(self):
        for ok in ("2026-01-01", "2024-02-29"):
            self.assertTrue(log.valid_date(ok), ok)
        for bad in ("2026-13-01", "2026-02-30", "2023-02-29", "26-01-01",
                    "2026-1-1", "", None):
            self.assertFalse(log.valid_date(bad), bad)

    def test_party_labels_reads_the_register_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "00_AI_context"))
            p = os.path.join(tmp, "00_AI_context", "PARTIES.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write("# PARTIES\n\n## Tier\n\n| not | a | register |\n|---|---|---|\n"
                        "| X | y | z |\n\n## Register\n\n"
                        "| Label | Full name | Tier |\n|---|---|---|\n"
                        "|  | ACME Ltd | upstream |\n| ACME | ACME Ltd | upstream |\n"
                        "| SUB-1 | Sub One | downstream |\n\n## Changes\n\n| Q | |\n")
            self.assertEqual(log.party_labels(tmp), {"ACME", "SUB-1"})
            self.assertIsNone(log.party_labels(os.path.join(tmp, "nowhere")))

    def test_norm_path(self):
        self.assertEqual(log.norm_path("03_exchange\\received\\A\\x.pdf"),
                         "03_exchange/received/A/x.pdf")
        self.assertEqual(log.norm_path("./03_exchange//a/../b.pdf"), "03_exchange/b.pdf")
        self.assertEqual(log.norm_path(" "), "")


# --------------------------------------------------------------------------
# update_index.py — what only this template's scan does
# --------------------------------------------------------------------------

class Scan(Project):

    def test_inbox_is_counted_temp_is_ignored(self):
        self.touch("_inbox/a.pdf")
        self.touch("_inbox/b.pdf")
        self.touch("06_temp/scratch.txt")
        code, out = self.diff()
        self.assertEqual(code, 1, out)
        self.assertIn("2 file(s) in _inbox/ awaiting triage", out)
        self.assertIn("NEW      _inbox/a.pdf", out)
        self.assertNotIn("06_temp", out)
        code, out = self.reindex()
        self.assertIn("2 file(s) in _inbox/", out)
        idx = self.read("00_AI_context/INDEX.md")
        self.assertIn("_inbox/a.pdf", idx)
        self.assertNotIn("06_temp/scratch.txt", idx)
        # Baselined, the inbox files are no longer NEW but are still counted.
        code, out = self.diff()
        self.assertNotIn("NEW", out)
        self.assertIn("2 file(s) in _inbox/", out)

    def test_log_growth_is_not_an_alarm_but_loss_is(self):
        with open(self.jsonl, "a", encoding="utf-8") as f:
            f.write("{}\n")
        code, out = self.diff()
        self.assertEqual(code, 1)
        self.assertNotIn("FROZEN ZONE MOVED", out)
        self.assertIn("0 in a frozen zone", out)
        os.remove(self.jsonl)
        code, out = self.diff()
        self.assertIn("FROZEN ZONE MOVED", out)
        self.assertIn("MISSING  03_exchange/LOG.jsonl", out)

    def test_frozen_change_and_missing_schema_dir(self):
        rel = self.touch("03_exchange/received/ACME/x.pdf")
        self.reindex()
        with open(self.path(*rel.split("/")), "ab") as f:
            f.write(b"tampered")
        os.remove(self.path("00_AI_context", "registers", "_TEMPLATE.md"))
        os.rmdir(self.path("00_AI_context", "registers"))
        os.rmdir(self.path("01_contract", "downstream"))
        code, out = self.diff()
        self.assertEqual(code, 1, out)
        self.assertIn("FROZEN ZONE MOVED", out)
        self.assertIn("CHANGED  03_exchange/received/ACME/x.pdf", out)
        self.assertIn("MISSING DIR  00_AI_context/registers/", out)
        self.assertIn("MISSING DIR  01_contract/downstream/", out)
        self.assertIn("2 schema directories missing", out)

    def test_extractor_treats_the_log_as_text_and_covers_three_zones(self):
        self.touch("01_contract/upstream/c.dwg")
        code, out = run(os.path.join(self.tools, "extract_text.py"), self.proj, "--report")
        self.assertEqual(code, 0, out)
        self.assertIn("03_exchange/LOG.jsonl", out)
        self.assertIn("already text", out)
        self.assertIn("01_contract/upstream/c.dwg", out)
        self.assertIn("not extractable (CAD drawing)", out)


if __name__ == "__main__":
    unittest.main()
