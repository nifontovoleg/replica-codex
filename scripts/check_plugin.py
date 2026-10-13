#!/usr/bin/env python3
"""Install and verify the Codex plugin in an isolated profile, without model calls."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from build_plugin import build
from check_codex_discovery import discover
from install_codex import ROOT, install


def check(codex, out):
    plugin_id = "replica-codex@replica-codex-local"
    tool_report = out.with_name(out.stem + "-tools.json").resolve()
    with tempfile.TemporaryDirectory(prefix="replica plugin test ") as tmp:
        test_root = Path(tmp)
        build(test_root / "package")
        catalog = test_root / ".agents/plugins/marketplace.json"
        catalog.parent.mkdir(parents=True)
        catalog.write_text(json.dumps({"name": "replica-codex-local", "plugins": [{
            "name": "replica-codex", "source": {"source": "local", "path": "./package"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity"}]}), encoding="utf-8")
        test_home = test_root / "profile"
        test_home.mkdir()
        env = dict(os.environ, CODEX_HOME=str(test_home))

        def command(args):
            result = subprocess.run(args, cwd=ROOT, env=env, capture_output=True,
                                    text=True, encoding="utf-8", timeout=35,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if result.returncode:
                raise RuntimeError(result.stderr.strip() or result.stdout.strip())
            return result.stdout

        command([codex, "plugin", "marketplace", "add", str(test_root), "--json"])
        installed = json.loads(command([codex, "plugin", "add", plugin_id, "--json"]))
        installed_root = Path(installed["installedPath"])
        if test_root not in installed_root.resolve().parents:
            raise RuntimeError("Plugin was not installed in the isolated profile")
        integrity = install(installed_root / "skills", check=True)
        discovery = discover(ROOT, codex, env=env, plugin_id=plugin_id)
        if not discovery["passed"]:
            raise RuntimeError("Codex did not discover the 11 packaged skills")
        command([sys.executable, str(ROOT / "scripts/smoke_codex.py"),
                 "--skills-dir", str(installed_root / "skills"), "--out", str(tool_report)])
        tools = json.loads(tool_report.read_text(encoding="utf-8"))
        report = {"passed": bool(tools["passed"]), "plugin_id": plugin_id,
                  "version": installed["version"], "isolated_profile": True,
                  "model_calls": 0, "integrity_count": len(integrity),
                  "discovery_count": discovery["count"], "tool_checks": len(tools["checks"])}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--codex", default=shutil.which("codex"))
    ap.add_argument("--out", type=Path, default=ROOT / ".test-artifacts/plugin-check.json")
    args = ap.parse_args()
    if not args.codex:
        ap.error("Codex executable not found; provide --codex")
    try:
        return check(args.codex, args.out)
    except (OSError, ValueError, RuntimeError, TimeoutError, subprocess.TimeoutExpired) as exc:
        print("plugin-check: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
