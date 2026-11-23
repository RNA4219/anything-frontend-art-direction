# SESSION B evaluation protocol

## Frozen scope and provenance

- Base: `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f`.
- Branch: `campaign/B-interaction-ux-flow`.
- Changed paths: `extensions/B/**`, `evidence/B/**` only.
- Baseline: current Art Direction skill and referenced assets at the base SHA.
- Candidate: identical base plus the B extension. No replacement of visual intent.
- Two task families: transactional workshop reservation and asynchronous import with partial failure.
- The same input content, visual tokens, API simulation, runtime and task requirements apply to both arms.
- Generation will use fresh agents with the same inherited model/effort. Exact server model revision and sampling seed are not exposed; do not claim bitwise model equivalence or reproducibility of stochastic generation.

## What is measured

1. Normal task completion with server-authoritative confirmation.
2. Invalid inputs and service failure with preservation of user work.
3. Boundary events: repeated submission, unknown outcome, stale response, back/cancel, partial completion.
4. Visible status and recovery affordances through a real browser where available.
5. Flow contract checks: schema, reachable states, completion paths, dead ends, wait exits, explicit guards and side-effect semantics.

Issues are classified as functional design / information structure / interaction / visual / implementation. B fixes interaction contracts; it records other categories for A/C/D without silently redesigning them.

## Integrity and gate

- Synthetic task fixtures and deterministic tests are development evidence, not a human usability study.
- Record original generated outputs before any repair. Report repair iterations separately.
- Do not introduce a broken baseline by deleting recovery logic or selectively weakening requirements.
- Any author review, non-blind review or reused evaluator is explicitly labelled; none is an independent oracle.
- A fresh agent may review anonymized outputs after they are frozen. Shared workspace access is not an enforced secret holdout boundary. If independent blind evaluation is not established, formal promotion is HOLD even when mechanical tests pass.
- R-ASI records actual external evidence only. Its structural CLI checks do not count as execution, UX validation or promotion.
