#!/usr/bin/env python3
"""Create label-masked report copies; not a protected or fully blind experiment."""
from pathlib import Path
import hashlib, json, re, secrets

base = Path(__file__).resolve().parent
out = base / 'adjudication-inputs'
if out.exists():
    raise SystemExit('Refusing to change an existing adjudication input set')
out.mkdir()
conditions = ['baseline', 'candidate']
secrets.SystemRandom().shuffle(conditions)
assignment = dict(zip(['Q', 'R'], conditions))
records = []
for label, condition in assignment.items():
    folder = out / label
    folder.mkdir()
    files = sorted(p for p in base.glob(condition + '-*') if p.is_file()
                   and not p.name.endswith('skill-manifest.json'))
    names = {p.name: re.sub(condition, 'report', p.name, flags=re.I) for p in files}
    for p in files:
        text = p.read_text()
        for original, masked in sorted(names.items(), key=lambda kv: -len(kv[0])):
            text = text.replace(original, masked)
        text = re.sub(r'baseline|candidate', 'assigned condition', text, flags=re.I)
        text = text.replace('anything-frontend-design-qa', '[assigned QA method]')
        text = text.replace('anything-frontend-art-direction', '[assigned source method]')
        text = text.replace('（Candidate D）', '')
        target = folder / names[p.name]
        target.write_text(text)
        records.append({'label': label, 'derivative_path': str(target.relative_to(base)),
                        'source_sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                        'derivative_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                        'derivative_not_original': True})
subjects = out / 'subjects'
subjects.mkdir()
root = base.parents[2]
for name in ['registration.html','requests.html','task-brief.md']:
    p = root / 'extensions/D/tests/fixtures' / name
    (subjects / name).write_bytes(p.read_bytes())
(out / 'rubric.json').write_bytes((base / 'predeclared-rubric.json').read_bytes())
(out / 'logic-probes.json').write_bytes((base / 'logic-probes.json').read_bytes())
(out / 'manifest.json').write_text(json.dumps({'schema':'design-qa-masked-inputs/v1','artifacts':records,
    'limits':['Only explicit condition names and artifact prefixes were masked.',
              'Report structure and cited methods may reveal the method; full blinding is not established.',
              'Derived text paths/hashes inside records may refer to original artifacts; do not claim integrity of masked bytes from original hashes.',
              'Shared filesystem with prompt-scoped access, no protected oracle or OS isolation.',
              'Rubric was frozen after the first review; this is exploratory adjudication.']}, ensure_ascii=False, indent=2)+'\n')
(out / 'README.md').write_text('''# Masked review inputs\n\nQとRは条件名を隠した派生コピーです。どちらが追加Skill条件かは提示していません。\n原文の構造・方法から推測できるため、完全なblind試験ではありません。\n原文は変更せず保存しています。表示用の名前置換で派生コピーのbytesは変化しています。\n元artifactのhash宣言を派生コピーのhashとして検証してはいけません。\nsubjects/ は同一評価対象、logic-probes.jsonは最小DOM上の限定的な観察です。\nブラウザ観察・人間のタスク完了率・保護されたholdoutはありません。\n''')
(base / 'adjudication-assignment.json').write_text(json.dumps({'assignment': assignment,
    'randomization': 'secrets.SystemRandom shuffle, single presentation order Q then R',
    'raw_outputs': [{'path': str(p.relative_to(base)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                    for c in ['baseline','candidate'] for p in sorted(base.glob(c+'-*')) if p.is_file()],
    'not_provided_to_adjudicator': True}, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'assignment':assignment,'masked_artifacts':len(records),'output':str(out)}, ensure_ascii=False))
