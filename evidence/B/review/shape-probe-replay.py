#!/usr/bin/env python3
"""Replay the original review's single-field shape probe.

Provenance: the first review executed this body as an in-memory shell here-document;
no script file or complete per-case log was saved then. The body below is preserved
from that tool invocation during the resolution review. It was not rerun during
the resolution review.

Run with extensions/B as the working directory:
    python -B ../../evidence/B/review/shape-probe-replay.py

The recorded 1,947-case result belongs to the original checker and fixture hashes
in reviewed-snapshot.json. Running this against another revision is a new result,
not reproduction of the historical version. This probe changes only one existing
field at a time; it is not exhaustive over field combinations or arbitrary JSON.
"""

import copy, importlib.util, json
from pathlib import Path
p=Path('checks/check_flow.py')
s=importlib.util.spec_from_file_location('cf',p); cf=importlib.util.module_from_spec(s); s.loader.exec_module(cf)
doc=json.loads(Path('tests/fixtures/report.json').read_text())
values=[None,True,False,0,1,1.5,'',[],{},['x'],{'x':1}]
crashes=[]; count=0
for scope in ['root','operations','states','transitions','scenarios']:
    objects=[doc] if scope=='root' else doc[scope]
    for i,obj in enumerate(objects):
        for field in obj:
            for value in values:
                m=copy.deepcopy(doc); target=m if scope=='root' else m[scope][i]; target[field]=value; count+=1
                try: cf.validate(m)
                except Exception as exc: crashes.append({'scope':scope,'index':i,'field':field,'value':value,'exception':type(exc).__name__,'message':str(exc)})
print(json.dumps({'case_count':count,'crashes':crashes},ensure_ascii=False,indent=2))
