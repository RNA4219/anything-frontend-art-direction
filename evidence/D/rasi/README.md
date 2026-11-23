# SESSION D: R-ASI control-plane evidence

## Scope

R-ASI `0.0.2` is used for contract verification, untrusted candidate packaging,
CAS integrity checks, receipts, cost events, and experience records. It does not
execute the design skill, independently evaluate it, or promote it. The observed
`execute`, `evaluate`, and `promote` commands each fail closed with exit code 3.

`external-campaign.json` is D's external campaign identity and status. It is
explicitly **not** a fabricated `campaign/v1` success. The runtime container image
digest has not been observed, and an independent blind evaluator and holdout are
not yet available. No `campaign-check` success is claimed.

## Reproduce command observations

The R-ASI source is an isolated copy outside the change set. Override `--tool`
when its location differs. Every invocation fixes `--root` to this D-specific
directory. Use a fresh log label to preserve earlier observations.

```bash
python evidence/D/rasi/record_cli.py --label version-recheck --expect-exit 0 -- --version
python evidence/D/rasi/record_cli.py --label help-recheck --expect-exit 0 -- --help
python evidence/D/rasi/record_cli.py --label execute-recheck --expect-exit 3 -- execute
```

The helper's own successful exit means the observed CLI exit matched the stated
expectation. In particular, observing exit 3 is evidence of an unconnected
capability, not a successful execution or evaluation. JSON and text logs retain
the actual R-ASI return code and output.

## Pending actual decomposition and test evidence

`examples/decomposition.json` is a mechanically valid **illustrative input**.
Its source is an explicitly synthetic four-line example. It has not been passed
off as the D skill's decomposition or as an experiment result. Replace it with
the actual, verified sankai extraction before packaging a candidate.

Commands for the actual extraction, once available:

```bash
python evidence/D/rasi/record_cli.py --label verify-actual --expect-exit 0 -- \
  verify --sankai inputs/decomposition.json
python evidence/D/rasi/record_cli.py --label pipeline-actual --expect-exit 0 -- \
  pipeline --sankai inputs/decomposition.json --store cas
python evidence/D/rasi/record_cli.py --label cas-verify-actual --expect-exit 0 -- \
  cas-verify --sha256 ACTUAL_OBJECT_SHA256 --store cas
python evidence/D/rasi/record_cli.py --label experience-actual --expect-exit 0 -- \
  experience-add --experience inputs/experience.json
```

`source.path` in a sankai input resolves inside the D-specific R-ASI root. Copy
the actual decomposition source into `inputs/` and calculate its raw-byte
SHA-256 and `splitlines()` count. Every citation must be present in the declared
line range. `skill_revision` identifies the actual sankai tool revision.

## Artifact and cost boundaries

R-ASI CAS accepts only validated `skill-candidate/v1` JSON. It is not a generic
image, test-log, or report store. Save screenshots and external test artifacts in
D's evidence directory with a normal SHA-256 manifest. An R-ASI experience record
can reference those artifacts through `provenance.evidence_ref`.

R-ASI receipts are emitted on successful supported commands. Failed commands do
not produce a native receipt, so `logs/` retains their observations. The logs here
are `external-cli-observation/v1`, not native R-ASI receipts.

Measured command wall time is recorded. LLM tokens, GPU time, billing cost,
evaluation outcomes, and skill quality remain unmeasured until actual evidence
exists. Do not encode unknown monetary or token cost as measured zero.

The cost ledger requires a `campaign/v1` input. Do not fabricate its required
runtime lock or approval fields to obtain a passing gate. If recorded cost events
contain `measured: false`, `cost-report` correctly refuses budget assessment.
