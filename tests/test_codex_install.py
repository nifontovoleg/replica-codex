import importlib.util
from pathlib import Path
import tempfile
import unittest

from _load import ROOT

spec = importlib.util.spec_from_file_location("install_codex", Path(ROOT) / "scripts/install_codex.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class CodexInstall(unittest.TestCase):
    def test_install_to_path_with_spaces_and_verify_all_payloads(self):
        with tempfile.TemporaryDirectory(prefix="replica test ") as tmp:
            dest = Path(tmp) / "skills"
            result = installer.install(dest)
            self.assertEqual(len(result), 11)
            self.assertTrue(all(r["status"] == "installed" for r in result))
            self.assertTrue(all(r["status"] == "verified" for r in installer.install(dest, check=True)))
            for name in installer.SKILLS:
                self.assertEqual((dest / name / "SKILL.md").read_bytes(),
                                 (Path(ROOT) / name / "SKILL.md").read_bytes())
                self.assertEqual((dest / name / "LICENSE").read_bytes(),
                                 (Path(ROOT) / "LICENSE").read_bytes())
            self.assertEqual(list(dest.rglob("*.pyc")), [])

    def test_rerun_preserves_identical_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            installer.install(tmp)
            skill = Path(tmp) / "replica-recon/SKILL.md"
            before = skill.stat().st_mtime_ns
            installer.install(tmp)
            self.assertEqual(skill.stat().st_mtime_ns, before)

    def test_collision_leaves_existing_and_other_skills_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / "replica-deploy"
            changed.mkdir()
            (changed / "SKILL.md").write_text("user's own skill", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                installer.install(tmp)
            self.assertEqual((changed / "SKILL.md").read_text(), "user's own skill")
            self.assertFalse((Path(tmp) / "replica-recon").exists())

    def test_check_missing_does_not_create_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "absent"
            with self.assertRaisesRegex(ValueError, "not installed"):
                installer.install(dest, check=True)
            self.assertFalse(dest.exists())

    def test_check_detects_modified_license(self):
        with tempfile.TemporaryDirectory() as tmp:
            installer.install(tmp)
            (Path(tmp) / "replica-recon/LICENSE").write_text("changed")
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                installer.install(tmp, check=True)
