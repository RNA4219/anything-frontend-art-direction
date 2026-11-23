#!/usr/bin/env python3
"""Run the observed R-ASI CLI and retain exact, bounded command evidence.

This helper records external invocations. It does not implement R-ASI contracts,
create an evaluation oracle, or replace failed commands with synthetic receipts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


DEFAULT_TOOL = Path("/workspace/scratch/1acf7c2e1e4d/tooling/R-ASI")
DEFAULT_ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_identity(tool: Path) -> dict:
    files = []
    for path in sorted((tool / "rasi").glob("*.py")):
        files.append({"path": str(path.relative_to(tool)), "sha256": sha256(path)})
    return {
        "path": str(tool),
        "files": files,
        "manifest_sha256": hashlib.sha256(
            json.dumps(files, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def invoke(tool: Path, root: Path, label: str, args: list[str], expected: int | None) -> dict:
    if not label or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in label):
        raise ValueError("label must contain only letters, digits, underscore, or hyphen")
    tool = tool.resolve(strict=True)
    root = root.resolve(strict=True)
    if not (tool / "rasi" / "cli.py").is_file():
        raise ValueError("the selected directory does not contain rasi/cli.py")
    logs = root / "logs"
    logs.mkdir(exist_ok=True)
    target = logs / f"{label}.json"
    transcript = logs / f"{label}.txt"
    if target.exists() or transcript.exists():
        raise FileExistsError(f"preserve existing command observation: {target}; choose a new label")
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONPATH"] = str(tool)
    command = [sys.executable, "-m", "rasi", "--root", str(root), *args]
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    timer = time.monotonic()
    result = subprocess.run(
        command, cwd=tool, env=env, text=True, encoding="utf-8",
        capture_output=True, timeout=60, check=False,
    )
    elapsed = time.monotonic() - timer
    finished = dt.datetime.now(dt.timezone.utc).isoformat()
    record = {
        "schema": "external-cli-observation/v1",
        "label": label,
        "started_at": started,
        "finished_at": finished,
        "command": command,
        "cwd": str(tool),
        "rasi_root": str(root),
        "tool_identity": package_identity(tool),
        "exit_code": result.returncode,
        "expected_exit_code": expected,
        "expectation_met": None if expected is None else result.returncode == expected,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "wall_seconds_measured": elapsed,
        "llm_cost": None,
        "evaluation_result": "not_an_evaluation",
    }
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    transcript.write_text(
        f"started_at: {started}\nfinished_at: {finished}\n"
        f"command: {json.dumps(command, ensure_ascii=False)}\n"
        f"cwd: {tool}\nexit_code: {result.returncode}\n"
        f"expected_exit_code: {expected}\nwall_seconds_measured: {elapsed:.6f}\n"
        f"--- stdout ---\n{result.stdout}--- stderr ---\n{result.stderr}",
        encoding="utf-8",
    )
    print(json.dumps({"log": str(target), "exit_code": result.returncode,
                      "expectation_met": record["expectation_met"]}, ensure_ascii=False))
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", type=Path, default=DEFAULT_TOOL)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--label", required=True)
    parser.add_argument("--expect-exit", type=int)
    parser.add_argument("rasi_args", nargs=argparse.REMAINDER)
    ns = parser.parse_args()
    args = ns.rasi_args
    if args[:1] == ["--"]:
        args = args[1:]
    if not args:
        parser.error("provide R-ASI arguments after --")
    result = invoke(ns.tool, ns.root, ns.label, args, ns.expect_exit)
    if ns.expect_exit is None:
        return result["exit_code"]
    return 0 if result["expectation_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
