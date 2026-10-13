#!/usr/bin/env python3
"""Ask the installed Codex app-server to discover Replica skills, without a model run."""

import argparse
import json
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading

from install_codex import SKILLS


def discover(cwd, executable, env=None, plugin_id=None):
    proc = subprocess.Popen([executable, "app-server", "--stdio"], cwd=cwd,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), env=env)
    incoming = queue.Queue()

    def read():
        for line in proc.stdout:
            try:
                incoming.put(json.loads(line))
            except ValueError:
                continue
        incoming.put({"closed": True})

    threading.Thread(target=read, daemon=True).start()

    def send(value):
        proc.stdin.write(json.dumps(value) + "\n")
        proc.stdin.flush()

    def receive(request_id):
        import time
        deadline = time.monotonic() + 30
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Codex discovery timed out")
            try:
                message = incoming.get(timeout=remaining)
            except queue.Empty as exc:
                raise TimeoutError("Codex discovery timed out") from exc
            if message.get("closed"):
                raise RuntimeError("Codex app-server closed before responding")
            if message.get("id") == request_id:
                if "error" in message:
                    raise RuntimeError("Codex rejected discovery: %s" % message["error"])
                return message["result"]

    try:
        send({"id": 1, "method": "initialize", "params": {
            "clientInfo": {"name": "replica_skill_check", "version": "1.0.0"}}})
        receive(1)
        send({"method": "initialized", "params": {}})
        send({"id": 2, "method": "skills/list", "params": {
            "cwds": [str(Path(cwd).resolve())], "forceReload": True}})
        response = receive(2)
        available_skills = [s for entry in response["data"] for s in entry["skills"]]
        skills = [s for s in available_skills
                  if s["name"].split(":")[-1] in SKILLS]
        if plugin_id:
            plugin_name, _, marketplace = plugin_id.partition("@")
            cache_marker = "/plugins/cache/%s/%s/" % (marketplace, plugin_name)
            skills = [s for s in skills if s.get("pluginId") == plugin_id or (
                s["name"].startswith(plugin_name + ":")
                and cache_marker in s["path"].replace("\\", "/"))]
        errors = [e for entry in response["data"] for e in entry["errors"]
                  if "replica-" in e.get("path", "")]
        found = [s["name"].split(":")[-1] for s in skills]
        valid = sorted(found) == sorted(SKILLS) and not errors
        valid = valid and all(s["enabled"] and (s.get("interface") or {}).get("displayName")
                              and (s.get("interface") or {}).get("defaultPrompt") for s in skills)
        diagnostics = [{"name": s["name"], "pluginId": s.get("pluginId"), "path": s["path"]}
                       for s in available_skills
                       if "replica" in s["name"] or "replica" in s["path"]]
        return {"passed": bool(valid), "count": len(skills), "skills": skills,
                "errors": errors, "candidates": diagnostics}
    finally:
        if proc.poll() is None:
            proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        proc.stdin.close()
        proc.stdout.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cwd", type=Path, default=Path.cwd())
    ap.add_argument("--codex", default=shutil.which("codex"))
    ap.add_argument("--out", type=Path)
    ap.add_argument("--plugin", help="verify skills from this installed plugin ID only")
    args = ap.parse_args()
    if not args.codex:
        ap.error("Codex executable not found; provide --codex")
    try:
        result = discover(args.cwd, args.codex, plugin_id=args.plugin)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Codex discovery: %d/11, %s" % (result["count"], "PASS" if result["passed"] else "FAIL"))
        return 0 if result["passed"] else 1
    except (OSError, RuntimeError, TimeoutError) as exc:
        print("discovery: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
