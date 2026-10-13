#!/usr/bin/env python3
"""Run the six installed tools on synthetic fixtures in a separate project folder."""

import argparse
import csv
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib


def png(path, offset=0):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
    rows = []
    for y in range(64):
        row = bytearray([0])
        for x in range(64):
            value = 20 if 12 + offset <= x < 32 + offset and 12 <= y < 32 else 255
            row.extend([value] * 3)
        rows.append(bytes(row))
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 64, 64, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(b"".join(rows))) + chunk(b"IEND", b""))


def run(skills_dir, out):
    skills_dir = Path(skills_dir).resolve()
    checks = []
    with tempfile.TemporaryDirectory(prefix="replica smoke ") as tmp:
        project = Path(tmp) / "Проект с пробелами"
        project.mkdir()
        matrix = "feature,priority,clone\nBook,must,yes\n"
        (project / "done.csv").write_text(matrix, encoding="utf-8")
        (project / "missing.csv").write_text(matrix.replace("must,yes", "must,no"), encoding="utf-8")
        shutil.copyfile(skills_dir / "replica-design/tokens.json", project / "tokens.json")
        shutil.copyfile(skills_dir / "replica-launch/listing.example.json", project / "listing.json")
        with (project / "reviews.csv").open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["source", "url", "date", "rating", "text"])
            writer.writerow(["synthetic", "https://example.test/review/1", "2026-10-01", "1", "Too expensive."])
            writer.writerow(["synthetic", "", "2026-10-01", "1", "No source, must be dropped."])
        (project / "clean").mkdir()
        (project / "dirty").mkdir()
        (project / "clean/index.html").write_text("<h1>New App</h1>")
        (project / "dirty/index.html").write_text("<h1>OldExampleBrand</h1>")
        png(project / "a.png")
        png(project / "b.png", offset=20)

        def check(label, skill, tool, args, expected=0, predicate=None):
            result = subprocess.run([sys.executable, str(skills_dir / skill / tool), *args],
                                    cwd=project, capture_output=True, text=True, encoding="utf-8", timeout=30)
            passed = result.returncode == expected
            if predicate and passed:
                passed = bool(predicate(json.loads(result.stdout)))
            checks.append({"check": label, "passed": passed, "exit_code": result.returncode,
                           "expected_exit_code": expected, "stdout": result.stdout, "stderr": result.stderr})

        check("complete required parity", "replica-diff", "parity.py",
              ["done.csv", "--require-must-have", "--fail-under", "80", "--json"],
              predicate=lambda d: d["feature_score"] == 100)
        check("missing required parity is rejected", "replica-diff", "parity.py",
              ["missing.csv", "--require-must-have"], expected=1)
        check("token contrast", "replica-design", "contrast.py", ["tokens.json"])
        check("low contrast is rejected", "replica-design", "contrast.py", ["#ffffff", "#ffffff"], expected=1)
        check("store listing", "replica-launch", "listing.py", ["listing.json"])
        check("old name in listing is rejected", "replica-launch", "listing.py",
              ["listing.json", "--avoid", "Slotwise"], expected=1)
        check("clean brand", "replica-brand", "sweep.py", ["clean", "--avoid", "OldExampleBrand"])
        check("leftover brand is rejected", "replica-brand", "sweep.py",
              ["dirty", "--avoid", "OldExampleBrand"], expected=1)
        check("review evidence filtering", "replica-entrepreneur", "reviews.py",
              ["reviews.csv", "--json", "--today", "2026-10-14"], predicate=lambda d: d["dropped"] == 1)
        check("identical image layout", "replica-diff", "imgdiff.py",
              ["a.png", "a.png", "--json"], predicate=lambda d: d["score"] == 100)
        check("moved element is detected", "replica-diff", "imgdiff.py",
              ["a.png", "b.png", "--json"], predicate=lambda d: d["score"] < 100)
    report = {"fixtures": "synthetic; not a real app, rendered UI or real user reviews",
              "skills_dir": str(skills_dir), "passed": all(c["passed"] for c in checks), "checks": checks}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Installed tool smoke: %d/%d passed" % (sum(c["passed"] for c in checks), len(checks)))
    return 0 if report["passed"] else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skills-dir", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=Path(".test-artifacts/installed-smoke.json"))
    args = ap.parse_args()
    return run(args.skills_dir, args.out)


if __name__ == "__main__":
    sys.exit(main())
