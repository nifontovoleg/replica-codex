import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from _load import ROOT

spec = importlib.util.spec_from_file_location("build_plugin", Path(ROOT) / "scripts/build_plugin.py")
builder = importlib.util.module_from_spec(spec)
import sys
sys.path.insert(0, str(Path(ROOT) / "scripts"))
spec.loader.exec_module(builder)


class CodexPlugin(unittest.TestCase):
    def test_bundle_contains_all_skills_tools_and_no_workspace_artifacts(self):
        with tempfile.TemporaryDirectory(prefix="plugin test ") as tmp:
            dest = builder.build(Path(tmp) / "package")
            manifest = json.loads((dest / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["name"], "replica-codex")
            self.assertEqual(manifest["skills"], "./skills/")
            self.assertTrue(manifest["requires_local_executor"])
            self.assertEqual(sorted(p.name for p in (dest / "skills").glob("replica-*") if p.is_dir()),
                             sorted(builder.SKILLS))
            for name in builder.SKILLS:
                self.assertTrue((dest / "skills" / name / "SKILL.md").is_file())
                self.assertTrue((dest / "skills" / name / "agents/openai.yaml").is_file())
                self.assertEqual((dest / "skills" / name / "LICENSE").read_bytes(), (Path(ROOT) / "LICENSE").read_bytes())
            self.assertEqual(len(list(dest.rglob("*.py"))), 6)
            for name in (".git", ".test-artifacts", ".test-deps", "tests", "scripts", ".env"):
                self.assertFalse((dest / name).exists())

    def test_build_is_idempotent_and_preserves_conflicting_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = builder.build(Path(tmp) / "package")
            self.assertEqual(builder.build(dest), dest)
            extra = dest / "user.txt"
            extra.write_text("custom")
            with self.assertRaisesRegex(ValueError, "differs"):
                builder.build(dest)
            self.assertEqual(extra.read_text(), "custom")
