#!/usr/bin/env python3
"""Install this local, adapted pack without downloading or overwriting skills."""

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = tuple("replica-" + name for name in (
    "recon", "architect", "design", "build", "backend", "test", "diff",
    "entrepreneur", "brand", "launch", "deploy"))
IGNORED = {"__pycache__", ".DS_Store"}


def payload(folder, license_path):
    files = {}
    for path in folder.rglob("*"):
        if path.is_symlink():
            raise ValueError("Symbolic link in skill: %s" % path)
        if path.is_file() and not any(p in IGNORED for p in path.parts) and path.suffix != ".pyc":
            files[path.relative_to(folder)] = path.read_bytes()
    files[Path("LICENSE")] = license_path.read_bytes()
    return files


def install(dest, check=False, source=ROOT):
    dest = Path(dest).expanduser().resolve()
    source = Path(source).resolve()
    plans = []
    for name in SKILLS:
        folder = source / name
        if not (folder / "SKILL.md").is_file() or not (folder / "agents/openai.yaml").is_file():
            raise ValueError("Incomplete Codex skill: %s" % name)
        if dest == folder or folder in dest.parents:
            raise ValueError("Destination must not be inside a source skill")
        files = payload(folder, source / "LICENSE")
        target = dest / name
        if target.is_symlink() or target.resolve().parent != dest:
            raise ValueError("Destination skill must be a direct regular folder: %s" % target)
        present = target.exists()
        if present:
            if not target.is_dir():
                raise ValueError("Destination exists and is not a folder: %s" % target)
            current = payload(target, source / "LICENSE")
            # Compare the actual installed license as well, rather than replacing it in memory.
            current.pop(Path("LICENSE"), None)
            if (target / "LICENSE").is_file():
                current[Path("LICENSE")] = (target / "LICENSE").read_bytes()
            if current != files:
                raise ValueError("Existing skill differs; refusing to overwrite: %s" % target)
        elif check:
            raise ValueError("Skill not installed: %s" % target)
        plans.append((target, files, present))

    # Validate every collision before writing any skill.
    results = []
    for target, files, present in plans:
        if not present:
            target.mkdir(parents=True, exist_ok=False)
            for rel, data in files.items():
                out = target / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
        results.append({"name": target.name, "path": str(target),
                        "status": "verified" if present else "installed"})
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    default = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex") / "skills"
    ap.add_argument("--dest", type=Path, default=default,
                    help="skills folder; e.g. ~/.agents/skills or PROJECT/.agents/skills")
    ap.add_argument("--check", action="store_true", help="verify installed bytes without writing")
    args = ap.parse_args(argv)
    try:
        print(json.dumps(install(args.dest, args.check), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print("install: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
