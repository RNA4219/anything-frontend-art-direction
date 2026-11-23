#!/usr/bin/env python3
"""Replay the original report gates without modifying the recorded output bytes.

Rebuild only recorded relative paths in a temporary directory from this checkout.
This verifies artifact identity and contracts; it does not repeat UI evaluation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[3]
EVALUATION = ROOT / 'evidence/D/evaluation'


def source_path(recorded: str) -> Path:
    prefixes = (
        ('evaluation/common/subject/', ROOT / 'extensions/D/tests/fixtures'),
        ('evaluation/common/art-direction/', ROOT),
        ('anything-frontend-D/', ROOT),
    )
    for prefix, target in prefixes:
        if recorded.startswith(prefix):
            suffix = Path(recorded[len(prefix):])
            if suffix.is_absolute() or '..' in suffix.parts:
                raise ValueError('unsafe recorded path')
            resolved = (target / suffix).resolve()
            if not resolved.is_relative_to(target.resolve()):
                raise ValueError('recorded path escapes its mapping')
            return resolved
    raise ValueError('unsupported recorded prefix: ' + recorded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Refusing to overwrite a prior replay observation')
    manifest = json.loads((EVALUATION / 'candidate-manifest.json').read_text())
    observations = []
    with tempfile.TemporaryDirectory(prefix='design-qa-replay-') as temporary:
        mirror = Path(temporary)
        for entry in manifest['artifacts']:
            source = source_path(entry['path'])
            raw = source.read_bytes()
            if hashlib.sha256(raw).hexdigest() != entry['sha256'] or len(raw) != entry['size_bytes']:
                raise ValueError('snapshot changed: ' + entry['path'])
            destination = mirror / entry['path']
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        mirrored_evaluation = mirror / 'anything-frontend-D/evidence/D/evaluation'
        for name in ('candidate-registration-desktop.json', 'candidate-requests-desktop.json',
                     'candidate-requests-narrow.json'):
            command = [sys.executable, str(ROOT / 'extensions/D/checks/qa_gate.py'),
                       'report', str(mirrored_evaluation / name), '--root', str(mirror)]
            process = subprocess.run(command, capture_output=True, text=True)
            observations.append({'report': name, 'exit_code': process.returncode,
                                 'stdout': json.loads(process.stdout), 'stderr': process.stderr,
                                 'report_sha256': hashlib.sha256((EVALUATION / name).read_bytes()).hexdigest()})
        shutil.copyfile(EVALUATION / 'candidate-manifest.json', mirrored_evaluation / 'candidate-manifest.json')
        command = [sys.executable, str(ROOT / 'extensions/D/checks/qa_gate.py'), 'verify-manifest',
                   str(mirrored_evaluation / 'candidate-manifest.json'), '--root', str(mirror)]
        process = subprocess.run(command, capture_output=True, text=True)
        integrity = {'exit_code': process.returncode, 'stdout': json.loads(process.stdout),
                     'stderr': process.stderr}
    result = {'schema': 'design-qa-portable-replay/v1', 'mapped_artifacts': len(manifest['artifacts']),
              'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'raw_reports_modified': False, 'report_gates': observations, 'manifest_gate': integrity,
              'limitations': ['Artifact and contract verification only; no browser or new model evaluation.',
                             'The original absolute execution paths remain in raw provenance records.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    expected_targets = ['REJECT', 'REJECT', 'HOLD']
    ok = (integrity['exit_code'] == 0 and all(r['exit_code'] == 2 and r['stdout']['contract_valid']
          and r['stdout']['promotion_decision'] == 'HOLD' and r['stdout']['target_decision'] == expected
          for r, expected in zip(observations, expected_targets)))
    print(json.dumps({'replay_matches_recorded_gates': ok, 'mapped_artifacts': result['mapped_artifacts'],
                      'output': str(args.output)}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
