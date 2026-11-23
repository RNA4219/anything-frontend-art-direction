# SESSION D — actual R-ASI recording

**Decision: HOLD.** This is an actual use of R-ASI's supported recording plane.
No autonomous LLM improvement, independent evaluation, or promotion is claimed.
The initial `README.md` and `external-campaign.json` describe the earlier
preparation state; this record documents the subsequent supported invocations.

## Input provenance and candidate packaging

`inputs/source-decomposition.md` is a byte-identical frozen copy of
`evidence/D/decomposition.md`: 213 lines, SHA-256
`08f82dee513f5faf8f2c8fb2c3fa19ebc1304b4c5271520d812bb04c83129e6a`.

This input is a composed document containing sankai extraction of existing
instructions and explicitly labelled D operational additions. It is **not** a
primary-source paper or guideline. Its `title`, `scope`, `verification_notes`,
and dependencies preserve that distinction and the original source indexes:
`evidence/D/source-index.md` and `evidence/D/research/sources.json`.

`inputs/decomposition.json` uses the actual observed sankai revision
`0e2521453ad758cfb680110da0fdddc994d000be`. `prepare_actual.py` packages the ten
existing D sections, common conditions, exceptions, and unresolved constraints
without performing another LLM inference. Every quote points to the frozen
source's actual line interval. R-ASI verified 10 units, 1 common-condition
record, 3 unresolved records, and 14 source references.

| Command | Observed exit | Meaning |
|---|---:|---|
| `verify` | 0 | Source hash, line count, quotes, and extraction contract match |
| `pipeline` | 0 | Untrusted candidate packaged and stored; CAS rechecked |
| `cas-verify` | 0 | Actual CAS object integrity and candidate contract match |
| `experience-add` | 0 | Preliminary external evidence and HOLD recorded |
| `cost-add` × 4 | 0 each | One measured wall-time record and three explicitly unknown usage records stored |
| `campaign-check` | 2 | Runtime image digest and frozen evaluation policy are genuinely unavailable |
| `cost-report` | 2 | Unmeasured usage prevents budget assessment |

Actual candidate ID:
`1778284f75f9d348edfb33f41fe17aa725ef3be9597eb035053087609f9d186b`.

Actual CAS object SHA-256:
`37b43571a69d9a6eccb2f6a17e011baafa425738d014fc7649a201412c387358`.

The object is `UNTRUSTED_CANDIDATE`, `quarantined`, and `promoted=false`.
All execution/evaluation/promotion connections remain false. Native receipts
are under `.ga/receipts/`; the exact command transcripts are under `logs/`.

## External evidence observed

`external-evidence-manifest.json` records 16 immutable snapshots with their
original repository path, snapshot path, SHA-256, and byte count. The manifest
was validated using the actual D artifact verifier; the output is retained in
`logs/external-evidence-integrity.json`.

| External evidence | Observation | Limitation |
|---|---|---|
| Gate mutation tests | 56 tests passed | Synthetic integrity/decision tests, not independent skill effectiveness |
| Node VM logic probes | 10 probe assertions passed | Minimal DOM doubles; no real layout, focus, native validation, or accessibility tree |
| Local candidate fixture browser run | BLOCKED; all 8 cases `not_run` | Browser launch was denied by the execution environment |
| Published examples | Two existing public examples observed | No established equality to local candidate fixtures; no controlled Skill effect trial |
| Final baseline/candidate outputs | Still in progress at this snapshot | Excluded from the current evidence claim |

Screenshots and test logs are ordinary artifacts in the external manifest.
R-ASI CAS accepts candidate JSON only. The experience record
`D-preliminary-evidence-20261123-01` references the manifest and its actual hash.
Its `active` state means that the observation record is active; it does not
represent approval or promotion of the skill.

## Cost and campaign contract limitations

`inputs/campaign-recording-only.json` is a native `campaign/v1` in `hold` state.
The CLI supports cost recording from this structural record independently of
`campaign-check`. Its draft lock intentionally contains `image_digest: null`,
and its draft evaluation policy explicitly retains unconfigured fields. The
observed campaign gate therefore fails, rather than accepting invented values.
This is a recording-only record, not an authorized ready campaign.

The measured event sums **1.4102408359999572 seconds** of child-process wall time
from exactly 16 completed CLI observations listed in
`inputs/cost-observations.json`. It excludes parent/model time, GPU work, and
the cost-recording calls themselves. No total campaign cost is inferred.

Input tokens, output tokens, and USD billing are unknown. The actual
`cost-event/v1` implementation requires a numeric `amount_raw` even when
`measured=false`; those three records therefore use an explicitly documented
numeric placeholder of 0, with `measurement_status: unknown`,
`actual_value: null`, and `measured: false`. These are **not measured zeroes**.
`cost-report` was actually executed and returned exit 2 because unmeasured cost
exists. Budget limits are zero additional authorization, conversion is
unconfigured, and no funded budget or cost-effectiveness result is asserted.

## Reproduction and later evidence

Run `prepare_actual.py` to verify or reproduce the frozen adapter outputs; it
refuses to overwrite different source bytes. Use `record_cli.py` with a fresh
label to preserve each subsequent invocation. For the native verification path:

```bash
python evidence/D/rasi/record_cli.py --label verify-repeat --expect-exit 0 -- \
  verify --sankai inputs/decomposition.json
python evidence/D/rasi/record_cli.py --label pipeline-repeat --expect-exit 0 -- \
  pipeline --sankai inputs/decomposition.json --store cas
python evidence/D/rasi/record_cli.py --label cas-repeat --expect-exit 0 -- \
  cas-verify --sha256 37b43571a69d9a6eccb2f6a17e011baafa425738d014fc7649a201412c387358 --store cas
```

Final baseline/candidate comparison results can be recorded in a new experience
and manifest version after they are frozen. Do not mutate these snapshots to
make the earlier observation appear more complete. Formal promotion remains
HOLD until the specified independent and protected evaluation exists.
