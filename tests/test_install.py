import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/install.py"
SPEC = importlib.util.spec_from_file_location("install_skills", SCRIPT)
INSTALL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALL)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repository = self.base / "source"
        self.project = self.base / "project with spaces"
        self.project.mkdir()
        for name in INSTALL.SKILLS:
            directory = self.repository / "skills" / name
            directory.mkdir(parents=True)
            (directory / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
        shared = self.repository / "skills/learn-start/references"
        shared.mkdir()
        (shared / "project-contract.md").write_text("Shared contract", encoding="utf-8")
        self.root = INSTALL.destination("codex", "project", self.project)

    def installed_files(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def test_five_agents_install_the_complete_bundle_with_shared_resources(self):
        for agent in INSTALL.PROJECT_PATHS:
            with self.subTest(agent=agent):
                root = INSTALL.destination(agent, "project", self.project)
                INSTALL.apply(root, self.repository, "install")
                self.assertTrue(INSTALL.apply(root, self.repository, "check")["ok"])
                for name in INSTALL.SKILLS:
                    self.assertTrue((root / name / "SKILL.md").is_file())
                self.assertEqual((root / "learn-start/references/project-contract.md").read_text(), "Shared contract")

    def test_user_destinations_are_under_injected_home(self):
        home = self.base / "home"
        for agent, relative in INSTALL.USER_PATHS.items():
            self.assertEqual(INSTALL.destination(agent, "user", home=home), home / relative)
        self.assertEqual(INSTALL.destination("opencode", "user", home=home), home / ".config/opencode/skills")

    def test_dry_run_creates_nothing(self):
        INSTALL.apply(self.root, self.repository, "install", dry_run=True)
        self.assertFalse(self.root.parent.exists())

    def test_reinstall_is_idempotent(self):
        INSTALL.apply(self.root, self.repository, "install")
        before = self.installed_files()
        INSTALL.apply(self.root, self.repository, "install")
        self.assertEqual(self.installed_files(), before)

    def test_conflict_blocks_whole_bundle_before_any_write(self):
        directory = self.root / "learn-review"
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text("My own skill")
        before = self.installed_files()
        with self.assertRaisesRegex(ValueError, "conflicting skills"):
            INSTALL.apply(self.root, self.repository, "install")
        self.assertEqual(self.installed_files(), before)

    def test_identical_manual_install_can_be_adopted(self):
        import shutil
        shutil.copytree(self.repository / "skills", self.root)
        self.assertFalse(INSTALL.apply(self.root, self.repository, "check")["ok"])
        INSTALL.apply(self.root, self.repository, "install")
        self.assertTrue(INSTALL.apply(self.root, self.repository, "check")["ok"])

    def test_update_requires_flag_and_preserves_local_modifications(self):
        INSTALL.apply(self.root, self.repository, "install")
        source = self.repository / "skills/learn-start/SKILL.md"
        source.write_text("New upstream version", encoding="utf-8")
        self.assertFalse(INSTALL.apply(self.root, self.repository, "check")["ok"])
        before = self.installed_files()
        with self.assertRaisesRegex(ValueError, "--update"):
            INSTALL.apply(self.root, self.repository, "install")
        self.assertEqual(self.installed_files(), before)
        installed = self.root / "learn-review/SKILL.md"
        installed.write_text("My edits", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Local changes"):
            INSTALL.apply(self.root, self.repository, "install", update=True)
        self.assertNotEqual((self.root / "learn-start/SKILL.md").read_text(), source.read_text())
        installed.write_bytes((self.repository / "skills/learn-review/SKILL.md").read_bytes())
        INSTALL.apply(self.root, self.repository, "install", update=True)
        self.assertEqual((self.root / "learn-start/SKILL.md").read_text(), "New upstream version")

    def test_update_removes_obsolete_managed_files(self):
        obsolete = self.repository / "skills/learn-start/old.txt"
        obsolete.write_text("Old resource")
        INSTALL.apply(self.root, self.repository, "install")
        obsolete.unlink()
        INSTALL.apply(self.root, self.repository, "install", update=True)
        self.assertFalse((self.root / "learn-start/old.txt").exists())

    def test_uninstall_preserves_unrelated_skills_and_rejects_modified_bundle(self):
        INSTALL.apply(self.root, self.repository, "install")
        unrelated = self.root / "another-skill"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_text("Unrelated")
        local = self.root / "learn-test/local-notes.md"
        local.write_text("Keep this")
        with self.assertRaisesRegex(ValueError, "Local changes"):
            INSTALL.apply(self.root, self.repository, "uninstall")
        local.unlink()
        INSTALL.apply(self.root, self.repository, "uninstall")
        self.assertEqual((unrelated / "SKILL.md").read_text(), "Unrelated")
        self.assertFalse((self.root / INSTALL.MANIFEST).exists())
        self.assertTrue(all(not (self.root / name).exists() for name in INSTALL.SKILLS))

    def test_unmanaged_skills_are_not_removed(self):
        with self.assertRaisesRegex(ValueError, "unmanaged"):
            INSTALL.apply(self.root, self.repository, "uninstall")
        self.assertFalse(self.root.exists())

    def test_filesystem_failure_rolls_back_all_skills_and_manifest(self):
        INSTALL.apply(self.root, self.repository, "install")
        before = self.installed_files()
        for name in INSTALL.SKILLS:
            (self.repository / "skills" / name / "SKILL.md").write_text(f"Updated {name}")
        rename = Path.rename

        def failing_rename(path, destination):
            if path.parent.name == "fresh" and path.name == "learn-next":
                raise OSError("Simulated write failure")
            return rename(path, destination)

        with patch.object(Path, "rename", failing_rename):
            with self.assertRaisesRegex(OSError, "Simulated"):
                INSTALL.apply(self.root, self.repository, "install", update=True)
        self.assertEqual(self.installed_files(), before)

    def test_linked_skill_is_refused(self):
        self.root.mkdir(parents=True)
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "SKILL.md").write_text("Keep outside data")
        try:
            (self.root / "learn-start").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Creating symlinks is unavailable on this host")
        with self.assertRaisesRegex(ValueError, "Linked"):
            INSTALL.apply(self.root, self.repository, "install")
        self.assertEqual((outside / "SKILL.md").read_text(), "Keep outside data")

    def test_cli_project_install_and_check(self):
        command = [sys.executable, "-B", str(SCRIPT), "install", "--agent", "opencode",
                   "--scope", "project", "--project", str(self.project)]
        run = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(json.loads(run.stdout)["ok"])
        command[3] = "check"
        run = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)

    def test_cli_requires_explicit_existing_project(self):
        run = subprocess.run([sys.executable, "-B", str(SCRIPT), "install", "--agent", "codex",
                              "--scope", "project"], capture_output=True, text=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("--project", json.loads(run.stderr)["error"])


if __name__ == "__main__":
    unittest.main()
