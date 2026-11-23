#!/usr/bin/env python3
"""Freeze actual D analysis/evidence and adapt it to observed R-ASI contracts.

This is a deterministic packaging adapter, not an LLM improvement/evaluation
engine. Existing frozen outputs are preserved; changed inputs require a new
snapshot/version rather than silently overwriting evidence.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CAMPAIGN = "anything-frontend-D-20261123"
SANKAI_REVISION = "0e2521453ad758cfb680110da0fdddc994d000be"


def canonical(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def freeze(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != raw:
            raise RuntimeError(f"frozen artifact differs; create a new version: {path}")
        return
    path.write_bytes(raw)


def freeze_json(path, value):
    freeze(path, canonical(value))


def main():
    original = REPO / "evidence/D/decomposition.md"
    raw = original.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines()
    freeze(HERE / "inputs/source-decomposition.md", raw)
    common_start = lines.index("## 共通条件") + 2
    common_end = lines.index("## 取り出した指示とDへの接続")
    common_text = "\n".join(lines[common_start:common_end]).strip()
    starts = [(i, re.match(r"### (D\d{2}) — (.+)", line)) for i, line in enumerate(lines) if re.match(r"### D\d{2} — ", line)]
    units = []
    for j, (start, match) in enumerate(starts):
        end = starts[j + 1][0] if j + 1 < len(starts) else lines.index("## 分解後の照合")
        section = lines[start:end]
        rows = {}
        for line in section:
            parts = line.split("|", 2)
            if len(parts) == 3 and parts[1].strip() in {"Trigger", "Inputs", "Decision Rules", "Procedure", "Output Contract", "Failure Modes", "Verification", "Sources"}:
                rows[parts[1].strip()] = parts[2].rsplit("|", 1)[0].strip()
        extracted = next(line for line in section if line.startswith("**抽出した指示本文:**")).removeprefix("**抽出した指示本文:**").strip()
        tail = next(line for line in section if line.startswith("制約・例外:"))
        instructions = "\n".join([extracted, "Decision Rules: " + rows["Decision Rules"], "Procedure: " + rows["Procedure"], "Failure Modes: " + rows["Failure Modes"], "Verification: " + rows["Verification"]])
        units.append({
            "id": match.group(1), "title": match.group(2), "instructions": instructions,
            "when": rows["Trigger"], "inputs": [rows["Inputs"]], "outputs": [rows["Output Contract"]],
            "conditions": [rows["Decision Rules"]], "exceptions": [tail],
            "dependencies": [rows["Sources"], "Repository provenance index: evidence/D/source-index.md", "Research source records: evidence/D/research/sources.json", "Frozen source records: evidence/D/rasi/external-evidence-manifest.json"],
            "common_refs": ["D-COMMON"],
            "reason": "同じD節の抽出本文・契約表・例外を一単位として保持する。既存指示の抽出とD追加の契約は原文のラベルどおり区別する。",
            "changeable": "当該節の例外・依存に従う。変更可否が未定義の部分へ新たな裁量を追加しない。",
            "unknowns": ["R-ASIによるこの包装は、原典の真偽・Skill実行・独立評価・昇格の完了を示さない。"],
            "sources": [{"start": start + 1, "end": end, "quote": "\n".join(section).strip()}],
        })
    if len(units) != 10:
        raise RuntimeError(f"expected the completed D01-D10 decomposition; got {len(units)}")
    unresolved = []
    for kind, needle, impact in [
        ("evaluation_independence", "このCampaignで厳密な隔離が成立しない場合", "正式なblind評価・昇格はHOLD。"),
        ("model_settings_unobserved", "生成設定にアクセスできない場合", "同一条件による因果効果の断言は不可。"),
        ("runtime_unconnected", "R-ASIのexecute/evaluate/promoteが未接続なら", "外部実行器の証拠だけを記録し、自動改善完了としない。"),
    ]:
        number, line = next((i + 1, line) for i, line in enumerate(lines) if needle in line)
        unresolved.append({"kind": kind, "text": line, "impact": impact, "sources": [{"start": number, "end": number, "quote": line}]})
    extraction = {
        "schema": "rasi-sankai/v1",
        "source": {"path": "inputs/source-decomposition.md", "sha256": digest(raw), "line_count": len(lines), "original_repository_path": "evidence/D/decomposition.md", "kind": "compiled_sankai_extraction_and_D_operational_contracts_not_primary_source"},
        "skill_revision": SANKAI_REVISION,
        "title": "SESSION D — 既存指示のsankai抽出＋D運用契約の構成文書（原典そのものではない）",
        "scope": "D01-D10を構成文書の実bytes・行・引用へ接続して記録する。一次資料の代替、LLM自動改善、実行・独立評価・昇格ではない。原典追跡先はevidence/D/source-index.mdおよびevidence/D/research/sources.json。",
        "common_conditions": [{"id": "D-COMMON", "text": common_text, "sources": [{"start": common_start + 1, "end": common_end, "quote": common_text}]}],
        "units": units, "unresolved": unresolved,
        "excluded": "A/B/Cの設計実装、Art Directionの再設計、独立評価の捏造、自動改善器・昇格への未実装接続。",
        "verification_notes": [
            "入力はsankaiで既存指示を抽出しD運用契約を加えた構成文書であり、一次原典そのものではない。",
            "このadapterは既存の抽出本文・契約表・共通条件・例外を決定的に包装する。新しいLLM実行を行っていない。",
            "原典の観察事実・著者見解・セッション推論はevidence/D/source-index.mdとevidence/D/research/sources.jsonで追跡する。",
            "source-decomposition.mdはevidence/D/decomposition.mdのbyte-identical snapshot。",
            "skill_revisionは実際に読んだsankaiのGit revision。候補Skillの品質評価を意味しない。",
            "R-ASI成功は構造・原文hash・引用・CASの整合性に限定する。execution/evaluation/promotionは未接続。",
        ],
    }
    freeze_json(HERE / "inputs/decomposition.json", extraction)

    evidence_paths = ["evidence/D/decomposition.md", "evidence/D/source-index.md", "evidence/D/research/sources.json", "evidence/D/evaluation/logic-probes.json", "evidence/D/tooling/gate-tests.log", "evidence/D/browser-fixtures/result.json", "evidence/D/browser-public/trace.json"]
    for path in sorted((REPO / "evidence/D/browser-public").glob("*")):
        rel = str(path.relative_to(REPO))
        if path.is_file() and path.suffix in {".jpg", ".png", ".txt"} and rel not in evidence_paths:
            evidence_paths.append(rel)
    artifacts = []
    for rel in evidence_paths:
        source = REPO / rel
        copied = HERE / "snapshots" / Path(rel).relative_to("evidence/D")
        observed = source.read_bytes()
        freeze(copied, observed)
        artifacts.append({"path": str(copied.relative_to(REPO)), "sha256": digest(observed), "size_bytes": len(observed), "original_repository_path": rel})
    manifest = {
        "schema": "design-qa-artifacts/v1", "campaign_id": CAMPAIGN, "phase": "actual-decomposition-and-preliminary-external-evidence",
        "artifacts": artifacts, "gate_decision": "HOLD", "baseline_candidate_comparison": "final outputs still in progress; not included or claimed here",
        "limitations": ["Logic probes use Node vm and minimal DOM doubles, not real browser layout/focus/native validation.", "Local candidate fixture browser run is BLOCKED; all 8 cases are not_run.", "Public browser observations cover two pre-existing examples only; not candidate fixture validation.", "Gate unit tests verify contracts, not independent effectiveness.", "Independent blind evaluation and protected holdout are not established."],
    }
    freeze_json(HERE / "external-evidence-manifest.json", manifest)
    print(json.dumps({"source_sha256": digest(raw), "source_lines": len(lines), "units": len(units), "common_conditions": 1, "unresolved": len(unresolved), "external_artifacts": len(artifacts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
