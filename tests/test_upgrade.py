"""Regression tests for the upgrade path: bin/upgrade_project.py and the
TEMPLATE.json stamp that bin/new_project.py writes.

    python3 -m unittest discover tests          # from the repository root

Standard library only. Each test instantiates a real template with
bin/new_project.py, then simulates a newer template release by copying the
template into a temporary toolbox and editing the copy — COWORK_TEMPLATES_DIR
points upgrade_project.py at it. What is tested is what a project gets, and
above all what a project must never lose: the tests fill projects with user
work and assert, byte for byte, that upgrades leave it alone.
"""

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW_PROJECT = os.path.join(ROOT, "bin", "new_project.py")
UPGRADE = os.path.join(ROOT, "bin", "upgrade_project.py")


def load(name):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(ROOT, "bin", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(*argv, env_extra=None):
    env = os.environ.copy()
    env.update(env_extra or {})
    proc = subprocess.run([sys.executable, *argv], capture_output=True,
                          text=True, env=env)
    return proc.returncode, proc.stdout + proc.stderr


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def append(path, text):
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)


class Stamp(unittest.TestCase):
    """What new_project.py records, and that both tools agree on the rule."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.proj = os.path.join(self.tmp, "proj")
        code, out = run(NEW_PROJECT, self.proj, "--name", "Fixture",
                        "--client", "ACME", "--template", "cowork-consultant")
        self.assertEqual(code, 0, out)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def stamp(self):
        with open(os.path.join(self.proj, "00_AI_context", "TEMPLATE.json"),
                  encoding="utf-8") as f:
            return json.load(f)

    def test_stamp_records_template_version_mapping_and_hashes(self):
        stamp = self.stamp()
        with open(os.path.join(ROOT, "templates", "cowork-consultant",
                               "VERSION"), encoding="utf-8") as f:
            version = f.read().strip()
        self.assertEqual(stamp["template"], "cowork-consultant")
        self.assertEqual(stamp["version"], version)
        self.assertEqual(stamp["created"]["version"], version)
        self.assertEqual(stamp["mapping"]["PROJECT_NAME"], "Fixture")
        self.assertEqual(stamp["mapping"]["CLIENT"], "ACME")
        self.assertEqual(stamp["upgrades"], [])
        self.assertEqual(
            set(stamp["scaffolding"]),
            {"CLAUDE.md", "README.md", "04_tools/extract_text.py",
             "04_tools/update_index.py", "00_AI_context/datasets/_TEMPLATE.md"})
        for rel, digest in stamp["scaffolding"].items():
            self.assertEqual(
                digest, sha(os.path.join(self.proj, *rel.split("/"))), rel)

    def test_both_tools_apply_the_same_scaffolding_rule(self):
        # The classification is duplicated in new_project.py and
        # upgrade_project.py so each script stays standalone; this is the test
        # that pins the two copies to each other.
        template = os.path.join(ROOT, "templates", "cowork-consultant")
        self.assertEqual(load("upgrade_project").scaffolding_files(template),
                         set(self.stamp()["scaffolding"]))

    def test_contractor_stamp_covers_its_own_scaffolding(self):
        proj = os.path.join(self.tmp, "contractor")
        code, out = run(NEW_PROJECT, proj, "--name", "Works",
                        "--template", "cowork-contractor")
        self.assertEqual(code, 0, out)
        with open(os.path.join(proj, "00_AI_context", "TEMPLATE.json"),
                  encoding="utf-8") as f:
            stamp = json.load(f)
        self.assertEqual(
            set(stamp["scaffolding"]),
            {"CLAUDE.md", "README.md", "05_tools/extract_text.py",
             "05_tools/log.py", "05_tools/update_index.py",
             "00_AI_context/datasets/_TEMPLATE.md",
             "00_AI_context/registers/_TEMPLATE.md"})

    def test_author_stamp_covers_its_own_scaffolding(self):
        proj = os.path.join(self.tmp, "author")
        code, out = run(NEW_PROJECT, proj, "--name", "Report",
                        "--template", "cowork-author")
        self.assertEqual(code, 0, out)
        with open(os.path.join(proj, "00_AI_context", "TEMPLATE.json"),
                  encoding="utf-8") as f:
            stamp = json.load(f)
        self.assertEqual(stamp["template"], "cowork-author")
        self.assertEqual(
            set(stamp["scaffolding"]),
            {"CLAUDE.md", "README.md", "05_tools/draft_diff.py",
             "05_tools/extract_text.py", "05_tools/update_index.py",
             "00_AI_context/datasets/_TEMPLATE.md",
             "00_AI_context/documents/_TEMPLATE.md"})
        self.assertEqual(load("upgrade_project").scaffolding_files(
            os.path.join(ROOT, "templates", "cowork-author")),
            set(stamp["scaffolding"]))


class Upgrade(unittest.TestCase):
    """upgrade_project.py against a simulated newer template release."""

    template = "cowork-consultant"

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.proj = os.path.join(self.tmp, "proj")
        code, out = run(NEW_PROJECT, self.proj, "--name", "Fixture",
                        "--client", "ACME", "--template", self.template)
        self.assertEqual(code, 0, out)
        # A newer toolbox: the real template, copied and then edited.
        self.templates = os.path.join(self.tmp, "templates")
        os.makedirs(self.templates)
        shutil.copytree(os.path.join(ROOT, "templates", self.template),
                        os.path.join(self.templates, self.template))
        with open(os.path.join(self.templates, self.template, "VERSION"),
                  encoding="utf-8") as f:
            self.base_version = f.read().strip()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def tpl(self, *parts):
        return os.path.join(self.templates, self.template, *parts)

    def prj(self, *parts):
        return os.path.join(self.proj, *parts)

    def set_version(self, version):
        with open(self.tpl("VERSION"), "w", encoding="utf-8") as f:
            f.write(version + "\n")

    def next_minor(self):
        major, minor, _ = self.base_version.split(".")
        version = f"{major}.{int(minor) + 1}.0"
        self.set_version(version)
        return version

    def upgrade(self, *extra):
        return run(UPGRADE, self.proj, *extra,
                   env_extra={"COWORK_TEMPLATES_DIR": self.templates})

    def stamp(self):
        with open(self.prj("00_AI_context", "TEMPLATE.json"),
                  encoding="utf-8") as f:
            return json.load(f)

    def test_replaces_untouched_scaffolding_and_nothing_else(self):
        # User work of every kind that must survive an upgrade untouched.
        with open(self.prj("01_basis", "survey.docx"), "wb") as f:
            f.write(b"\x00frozen bytes\x01")
        with open(self.prj("03_working", "drafts", "report.md"), "w") as f:
            f.write("draft in progress\n")
        with open(self.prj("04_tools", "my_helper.py"), "w") as f:
            f.write("# user's own script\n")
        append(self.prj("00_AI_context", "WORKLOG.md"),
               "\n## 2026-08-19 — A user decision\n\n- Kept.\n")
        append(self.prj("00_AI_context", "PROJECT.md"), "\nEdited brief.\n")
        untouched = {rel: sha(self.prj(*rel.split("/"))) for rel in (
            "01_basis/survey.docx", "03_working/drafts/report.md",
            "04_tools/my_helper.py", "00_AI_context/PROJECT.md")}

        version = self.next_minor()
        append(self.tpl("04_tools", "update_index.py"), "\n# next-version marker\n")
        append(self.tpl("CLAUDE.md"), "\nA new rule for {{PROJECT_NAME}}.\n")
        with open(self.tpl("04_tools", "brand_new.py"), "w") as f:
            f.write("#!/usr/bin/env python3\nprint('new tool')\n")

        code, out = self.upgrade()
        self.assertEqual(code, 0, out)

        for rel, digest in untouched.items():
            self.assertEqual(sha(self.prj(*rel.split("/"))), digest, rel)
        self.assertIn("# next-version marker",
                      read(self.prj("04_tools", "update_index.py")))
        claude = read(self.prj("CLAUDE.md"))
        self.assertIn("A new rule for Fixture.", claude)
        self.assertNotIn("{{", claude)
        self.assertTrue(os.path.exists(self.prj("04_tools", "brand_new.py")))
        if os.name == "posix":
            self.assertTrue(os.access(self.prj("04_tools", "brand_new.py"),
                                      os.X_OK))

        readme = read(self.prj("README.md"))
        self.assertIn(f"template **v{self.base_version}**", readme)
        self.assertIn(f"Upgraded to **v{version}**", readme)
        worklog = read(self.prj("00_AI_context", "WORKLOG.md"))
        self.assertIn("A user decision", worklog)
        self.assertIn("Template upgraded", worklog)
        stamp = self.stamp()
        self.assertEqual(stamp["version"], version)
        self.assertEqual(stamp["created"]["version"], self.base_version)
        self.assertEqual(len(stamp["upgrades"]), 1)
        self.assertIn("04_tools/brand_new.py", stamp["upgrades"][0]["added"])

    def test_locally_modified_scaffolding_is_proposed_not_overwritten(self):
        append(self.prj("CLAUDE.md"), "\nLocal note the user added.\n")
        before = sha(self.prj("CLAUDE.md"))
        version = self.next_minor()
        append(self.tpl("CLAUDE.md"), "\nA new rule.\n")

        code, out = self.upgrade()
        self.assertEqual(code, 0, out)
        self.assertEqual(sha(self.prj("CLAUDE.md")), before)
        proposal = self.prj("05_temp", f"template-upgrade-v{version}",
                            "CLAUDE.md")
        self.assertTrue(os.path.exists(proposal), out)
        self.assertIn("A new rule.", read(proposal))
        self.assertIn("CLAUDE.md", self.stamp()["upgrades"][0]["proposed"])

    def test_dry_run_writes_nothing(self):
        version = self.next_minor()
        append(self.tpl("CLAUDE.md"), "\nA new rule.\n")
        before = {rel: sha(self.prj(*rel.split("/")))
                  for rel in self.stamp()["scaffolding"]}
        code, out = self.upgrade("--dry-run")
        self.assertEqual(code, 0, out)
        for rel, digest in before.items():
            self.assertEqual(sha(self.prj(*rel.split("/"))), digest, rel)
        self.assertNotEqual(self.stamp()["version"], version)
        self.assertFalse(os.path.exists(
            self.prj("05_temp", f"template-upgrade-v{version}")))

    def test_no_longer_shipped_is_retired_to_to_delete_never_deleted(self):
        original = sha(self.prj("04_tools", "extract_text.py"))
        self.next_minor()
        os.remove(self.tpl("04_tools", "extract_text.py"))
        code, out = self.upgrade()
        self.assertEqual(code, 0, out)
        self.assertFalse(os.path.exists(self.prj("04_tools", "extract_text.py")))
        retired = self.prj("_to_delete", "extract_text.py")
        self.assertTrue(os.path.exists(retired), out)
        self.assertEqual(sha(retired), original)

    def test_no_longer_shipped_but_edited_stays_in_place(self):
        append(self.prj("04_tools", "extract_text.py"), "\n# user tweak\n")
        before = sha(self.prj("04_tools", "extract_text.py"))
        self.next_minor()
        os.remove(self.tpl("04_tools", "extract_text.py"))
        code, out = self.upgrade()
        self.assertEqual(code, 0, out)
        self.assertEqual(sha(self.prj("04_tools", "extract_text.py")), before)
        self.assertFalse(os.path.exists(self.prj("_to_delete",
                                                 "extract_text.py")))

    def test_cross_major_is_refused_and_nothing_changes(self):
        self.set_version("99.0.0")
        append(self.tpl("CLAUDE.md"), "\nA v99 rule.\n")
        before = sha(self.prj("CLAUDE.md"))
        code, out = self.upgrade()
        self.assertNotEqual(code, 0)
        self.assertIn("crosses", out)
        self.assertEqual(sha(self.prj("CLAUDE.md")), before)
        self.assertEqual(self.stamp()["version"], self.base_version)

    def test_toolbox_older_than_project_is_refused(self):
        self.set_version("0.0.1")
        code, out = self.upgrade()
        self.assertNotEqual(code, 0)
        self.assertIn("Update the toolbox", out)

    def test_same_version_restores_missing_scaffolding(self):
        os.remove(self.prj("04_tools", "extract_text.py"))
        code, out = self.upgrade()
        self.assertEqual(code, 0, out)
        restored = self.prj("04_tools", "extract_text.py")
        self.assertTrue(os.path.exists(restored), out)
        self.assertEqual(sha(restored),
                         self.stamp()["scaffolding"]["04_tools/extract_text.py"])

    def test_same_version_is_a_noop(self):
        before = {rel: sha(self.prj(*rel.split("/")))
                  for rel in self.stamp()["scaffolding"]}
        code, out = self.upgrade()
        self.assertEqual(code, 0, out)
        self.assertIn("nothing to do", out.lower())
        for rel, digest in before.items():
            self.assertEqual(sha(self.prj(*rel.split("/"))), digest, rel)

    def test_project_without_a_stamp_is_adopted_conservatively(self):
        # Simulates a project created before TEMPLATE.json existed. The
        # temporary toolbox has no git history, so nothing can be proven
        # unmodified — the upgrade must propose everything and replace nothing.
        os.remove(self.prj("00_AI_context", "TEMPLATE.json"))
        before = {rel: sha(self.prj(*rel.split("/"))) for rel in (
            "CLAUDE.md", "README.md", "04_tools/update_index.py")}
        version = self.next_minor()
        append(self.tpl("CLAUDE.md"), "\nA new rule.\n")

        code, out = self.upgrade()
        self.assertEqual(code, 0, out)
        self.assertIn("adopting", out)
        for rel, digest in before.items():
            self.assertEqual(sha(self.prj(*rel.split("/"))), digest, rel)
        self.assertTrue(os.path.exists(
            self.prj("05_temp", f"template-upgrade-v{version}", "CLAUDE.md")))
        stamp = self.stamp()
        self.assertIn("adopted", stamp)
        self.assertEqual(stamp["version"], version)
        self.assertEqual(stamp["mapping"]["PROJECT_NAME"], "Fixture")
        self.assertEqual(stamp["mapping"]["CLIENT"], "ACME")

    def test_refuses_a_folder_that_is_not_a_project(self):
        code, out = run(UPGRADE, self.tmp,
                        env_extra={"COWORK_TEMPLATES_DIR": self.templates})
        self.assertNotEqual(code, 0)
        self.assertIn("does not look like a cowork project", out)


class ContractorBoundary(unittest.TestCase):
    """Below 1.0.0 the minor is the compatibility boundary; patches upgrade."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.proj = os.path.join(self.tmp, "proj")
        code, out = run(NEW_PROJECT, self.proj, "--name", "Works",
                        "--template", "cowork-contractor")
        self.assertEqual(code, 0, out)
        self.templates = os.path.join(self.tmp, "templates")
        os.makedirs(self.templates)
        shutil.copytree(os.path.join(ROOT, "templates", "cowork-contractor"),
                        os.path.join(self.templates, "cowork-contractor"))
        with open(os.path.join(self.templates, "cowork-contractor", "VERSION"),
                  encoding="utf-8") as f:
            self.base_version = f.read().strip()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def set_version(self, version):
        with open(os.path.join(self.templates, "cowork-contractor", "VERSION"),
                  "w", encoding="utf-8") as f:
            f.write(version + "\n")

    def upgrade(self):
        return run(UPGRADE, self.proj,
                   env_extra={"COWORK_TEMPLATES_DIR": self.templates})

    def test_pre_1_0_minor_is_refused_but_patch_upgrades(self):
        major, minor, patch = (int(x) for x in self.base_version.split("."))
        if major != 0:
            self.skipTest("cowork-contractor has reached 1.0")
        self.set_version(f"0.{minor + 1}.0")
        code, out = self.upgrade()
        self.assertNotEqual(code, 0)
        self.assertIn("pre-1.0 minor", out)

        patch_version = f"0.{minor}.{patch + 1}"
        self.set_version(patch_version)
        code, out = self.upgrade()
        self.assertEqual(code, 0, out)
        with open(os.path.join(self.proj, "00_AI_context", "TEMPLATE.json"),
                  encoding="utf-8") as f:
            self.assertEqual(json.load(f)["version"], patch_version)
        with open(os.path.join(self.proj, "00_AI_context", "WORKLOG.md"),
                  encoding="utf-8") as f:
            self.assertIn("Template upgraded", f.read())


if __name__ == "__main__":
    unittest.main()
