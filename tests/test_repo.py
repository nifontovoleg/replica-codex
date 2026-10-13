import json
import os
import re
import unittest
from pathlib import Path

from _load import ROOT

SKILLS = ["replica-recon", "replica-architect", "replica-design", "replica-build",
          "replica-backend", "replica-test", "replica-diff", "replica-entrepreneur",
          "replica-brand", "replica-launch", "replica-deploy"]


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1) if m else ""), text


class Repo(unittest.TestCase):
    def test_eleven_skill_folders_at_the_root(self):
        found = sorted(d for d in os.listdir(ROOT)
                       if os.path.isfile(os.path.join(ROOT, d, "SKILL.md")))
        self.assertEqual(found, sorted(SKILLS))

    def test_frontmatter_name_and_description(self):
        for s in SKILLS:
            fm, text = frontmatter(os.path.join(ROOT, s, "SKILL.md"))
            self.assertIn("name: %s\n" % s, fm + "\n", s)
            self.assertRegex(fm, r"description: ", s)
            description = json.loads(fm.split("description: ", 1)[1])
            self.assertTrue(description.strip(), s)
            self.assertLessEqual(len(description), 1024, s)
            self.assertTrue(text.split("---", 2)[2].strip(), s)

    def test_installer_packages_all_codex_skills_and_their_tools(self):
        import importlib.util
        path = os.path.join(ROOT, "scripts", "install_codex.py")
        spec = importlib.util.spec_from_file_location("repo_installer", path)
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        self.assertEqual(sorted(installer.SKILLS), sorted(SKILLS))
        for name in installer.SKILLS:
            files = installer.payload(
                Path(ROOT) / name, Path(ROOT) / "LICENSE")
            self.assertIn(Path("SKILL.md"), files)
            self.assertIn(Path("agents/openai.yaml"), files)
            self.assertIn(Path("LICENSE"), files)

    def test_readme_documents_codex_install_and_all_skills(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            readme = " ".join(fh.read().split())
        self.assertTrue(readme.startswith("# Replica Codex"))
        for line in ("scripts/install_codex.py", "scripts/check_codex_discovery.py",
                     "scripts/smoke_codex.py", "## Fine print"):
            self.assertIn(line, readme)
        for s in SKILLS:
            self.assertIn("`$%s`" % s, readme)

    def test_codex_interface_metadata_and_tool_locations(self):
        for s in SKILLS:
            path = os.path.join(ROOT, s, "agents", "openai.yaml")
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
            self.assertEqual(lines[0], "interface:")
            values = dict((key.strip(), json.loads(value.strip()))
                          for key, value in (line.split(":", 1) for line in lines[1:]))
            self.assertTrue(values["display_name"].startswith("Replica:"))
            self.assertTrue(25 <= len(values["short_description"]) <= 64)
            self.assertIn("$" + s, values["default_prompt"])
            with open(os.path.join(ROOT, s, "SKILL.md"), encoding="utf-8") as fh:
                text = fh.read()
            self.assertNotIn("/replica-", text.replace("<skills-dir>/replica-", ""))
            self.assertNotIn("python3 ", text)

    def test_no_em_dashes_anywhere(self):
        bad = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in (
                ".git", "__pycache__", ".test-artifacts", ".test-deps")]
            for fn in filenames:
                if fn.endswith((".md", ".py", ".json", ".ts", ".csv")):
                    path = os.path.join(dirpath, fn)
                    with open(path, encoding="utf-8") as fh:
                        if chr(0x2014) in fh.read():
                            bad.append(os.path.relpath(path, ROOT))
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
