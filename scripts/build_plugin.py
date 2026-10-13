#!/usr/bin/env python3
"""Build a Codex plugin with only the manifest, skill files and MIT license."""

import argparse
from pathlib import Path
import sys

from install_codex import ROOT, SKILLS, payload


def build(destination, source=ROOT):
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    files = {Path(".codex-plugin/plugin.json"):
             (source / ".codex-plugin/plugin.json").read_bytes(),
             Path("LICENSE"): (source / "LICENSE").read_bytes()}
    for name in SKILLS:
        for rel, data in payload(source / name, source / "LICENSE").items():
            files[Path("skills") / name / rel] = data
    if destination.exists():
        current = {}
        for p in destination.rglob("*"):
            if p.is_symlink():
                raise ValueError("Plugin output contains a symbolic link")
            if p.is_file():
                current[p.relative_to(destination)] = p.read_bytes()
        if current != files:
            raise ValueError("Plugin output differs; choose a new --out directory")
        return destination
    destination.mkdir(parents=True, exist_ok=False)
    for rel, data in files.items():
        out = destination / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
    return destination


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "dist/replica-codex")
    args = ap.parse_args()
    try:
        print("Codex plugin built: %s" % build(args.out))
        return 0
    except (OSError, ValueError) as exc:
        print("build: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
