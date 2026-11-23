# SESSION D — tool inventory

Observed on 2026-11-23. File bytes and the exact command observations are recorded
in [`inventory.json`](inventory.json) and [`../rasi/logs/`](../rasi/logs/).

## Versions and isolation

| Component | Observed revision | Execution form |
|---|---|---|
| imozuru | `30c3b59a076ce228f05aa3036809297422f23dee` | Prompt skill plus Python source fetching, citation-chain, and logging scripts |
| sankai | `0e2521453ad758cfb680110da0fdddc994d000be` | Prompt skill with decomposition, understanding, and dissolution references; no CLI |
| R-ASI | `f5b638085dece1f997210f9b653aceb8fe9b32d4`, version `0.0.2` | Python CLI control and recording plane |

The initial imozuru and sankai checkouts were located in
`/workspace/scratch/a50c340f4e5f/tooling/`. They were inspected without editing
their source. R-ASI was copied into
`/workspace/scratch/1acf7c2e1e4d/tooling/R-ASI` before the recorded D invocations.
All D command output is directed to D's `evidence/D/rasi/` root. No R-ASI source
or another session's evidence is modified by the D recording helper.

R-ASI's retrieval manifest records authenticated connector retrieval and the
original Git blob SHA-1 of 29 source/schema/test/document files. Recomputing those
blob hashes from the isolated copy produced **29/29 matches**. SHA-256 and byte
size for each inspected tool file are stored in `inventory.json`. This verifies
the snapshot's provenance; it does not establish the skill's behavioral quality.

The D base is `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f`, on branch
`campaign/D-design-qa-20261123`.

## Actual API and command boundaries

### imozuru

Read `skills/imozuru/SKILL.md` before using the exploration workflow. Its
`scripts/fetch.py` accepts exactly `<sources_dir> <name> <url>` and prints an
`OK` or `FAIL` TSV result. When `sources_dir` ends in `sources`, the parent
directory receives an automatic `fetch-log.jsonl`. A failed or blocked fetch is
not a verified local original. The script's usage path exits 2 rather than
offering argparse-style `--help`.

`scripts/chain.py` supports `find`, `refs`, `cites`, and `author`, using OpenAlex.
`--log <topic_dir> --round N` preserves returned records.
`scripts/digest.py add <topic_dir> --round N --by <name>` imports actual search
result arrays from stdin. Neither script is an autonomous model executor.

### sankai

The entry point and `references/{decompose,understand,dissolve}.md` specify how
to extract instruction text while preserving conditions, dependencies,
exceptions, and provenance. Applying that workflow is an LLM analysis operation.
It is not a CLI invocation, installation, execution, or evaluation of the
resulting skill. Reconstructing the D skill is a separate D implementation step.

### R-ASI

The actual `--version` and command help outputs are retained in D logs. The CLI
exposes 18 commands. `--root` is a global argument before the subcommand.

| Capability | Observed state |
|---|---|
| `verify`, `candidate`, `pipeline` | Supported contract and packaging operations; not model execution |
| `cas-store`, `cas-verify` | Supports canonical `skill-candidate/v1` JSON only |
| `lock`, `policy-check`, `campaign-check`, `resume-check` | Contract, hash, and eligibility checks; not an independent evaluation oracle |
| `cost-add`, `cost-report` | Supported ledger operations; unknown measurements prevent budget assessment |
| `experience-add`, `experience-invalidate`, `experience-restore` | Supported provenance and experience-state operations |
| `query-check` | Query policy checking; no outbound research execution |
| `execute`, `evaluate`, `promote` | Executed probes all returned **exit 3**, explicitly unconnected |

Successful supported commands write native `rasi-receipt/v1` receipts under
`.ga/receipts/`. Failed commands do not write native receipts. D's external log
helper therefore records exact stdout, stderr, exit code, tool hashes, and
measured wall time independently.

## Evidence and missing capabilities

Screenshots, browser traces, test logs, and reports remain ordinary artifacts
with a SHA-256 manifest. They cannot be sent directly to R-ASI CAS. The actual
sankai extraction will be packaged into an untrusted candidate JSON, and an
experience record may reference the external artifact manifest.

The runtime container image digest was not observed. R-ASI's `rsi-lock/v1`
contract requires that digest, so no fabricated lock or successful
`campaign-check` is produced. [`external-campaign.json`](../rasi/external-campaign.json)
records D's identity and **HOLD** in an explicitly external schema.

No actual candidate quality, independent blind result, token usage, GPU usage,
or billing cost is asserted in this preparation step. A command expectation
matching exit 3 means that an unavailable feature correctly remained
unavailable. It is not a design evaluation pass.

## Reproduction

See [`record_cli.py`](../rasi/record_cli.py) and its
[`usage notes`](../rasi/README.md). The helper fixes the execution root, refuses
to overwrite existing observation labels, preserves actual R-ASI exit codes,
and emits no invented native receipt. The illustrative sankai input is kept in
`../rasi/examples/` and is explicitly excluded from effectiveness evidence.
