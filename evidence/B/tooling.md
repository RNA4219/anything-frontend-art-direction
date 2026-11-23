# SESSION B — tool provenance and capability boundary

Checked: 2026-11-23 (Asia/Tokyo). This file records actual inspection and execution, not a claim of independent UX evaluation.

## Pinned inputs

| Component | Repository revision | Acquisition | Actual interface |
| --- | --- | --- | --- |
| Existing Art Direction | `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f` | Isolated Git worktree, branch `campaign/B-interaction-ux-flow` | `SKILL.md` and its references/templates |
| imozuru | `30c3b59a076ce228f05aa3036809297422f23dee` | Normal-permission clone of [MaryCache/imozuru](https://github.com/MaryCache/imozuru) | `skills/imozuru/SKILL.md`, Python fetch/chain/report/digest helpers; not a single research API |
| sankai | `0e2521453ad758cfb680110da0fdddc994d000be` | Normal-permission clone of [RNA4219/sankai](https://github.com/RNA4219/sankai) | `skills/sankai/SKILL.md`; no dedicated extraction CLI |
| R-ASI | `f5b638085dece1f997210f9b653aceb8fe9b32d4` | Private clone failed without credentials; authenticated GitHub connector retrieved 34 needed source, schema, documentation and test files at this exact SHA | `python -m rasi`, version `0.0.2`, Python standard library runtime |

All 34 retrieved R-ASI files were compared against Git blob SHA-1 values from the pinned tree; 34/34 match. SHA-256 inventory: [rasi-source-integrity.json](rasi-source-integrity.json). R-ASI private source code is not copied into this extension. Locally it is under the session's separate `tools-B/R-ASI` directory. Public tools are likewise separate checkouts.

## imozuru and sankai scope

The campaign uses imozuru for a bounded source map, link/citation tracing and source retrieval. Query text contains only public interaction-design topics. Full downloaded external texts remain outside the Git changeset; the committed evidence contains URLs, retrieval metadata, hashes, short quotations and derived principles. A fetch success is not automatically a relevant or valid source: actual contents and authority are checked.

sankai performs decomposition, understanding and dissolution. Its `references/decompose.md`, `understand.md` and `dissolve.md` preserve input/output, conditions, exceptions, dependencies, source location and differences between original claims and inference. It does not generate/install/run the final Skill. SESSION B performs subsequent reconstruction and implementation.

## Executed R-ASI discovery

Raw command, return code and output: [rasi/discovery-cli.json](rasi/discovery-cli.json).

| Action | Result | Interpretation |
| --- | --- | --- |
| `--version` | exit 0, `0.0.2` | CLI actually runs in this executor |
| `--help` | exit 0, 18 subcommands | Interface inspected, not inferred from roadmap |
| `lock` with truthful draft | exit 2 | Actual runtime OCI image digest is unavailable; no synthetic digest substituted |
| `policy-check` with truthful draft | exit 2 | Evaluation policy is not frozen; independent noise calibration/holdout absent |
| `campaign-check` with truthful draft | exit 2 | Cost settings are unconfigured; lock/policy would also remain incomplete |
| `execute`, `evaluate`, `promote` | exit 3 each | Explicitly unconnected, fail closed; no execution/evaluation/promotion claimed |

Drafts: [rasi-input/campaign.json](rasi-input/campaign.json), [lock.json](rasi-input/lock.json), [policy.json](rasi-input/policy.json), [task.json](rasi-input/task.json), [model.json](rasi-input/model.json), [environment.json](rasi-input/environment.json). Candidate identity is initially null until final artifacts are frozen. Baseline root Skill SHA-256 and base Git SHA are recorded. Unknown model/billing costs are [explicitly unmeasured](rasi-input/cost-unmeasured.json), not zero.

## Capability boundary confirmed in code

- `verify` checks `rasi-sankai/v1`, source bytes SHA-256, line count and literal quote presence in declared ranges. It does not establish that a derived claim is sound.
- `candidate`/`pipeline` package verified sankai units into `skill-candidate/v1`. This is a descriptor with `UNTRUSTED_CANDIDATE`, `quarantined`, and execution/evaluation/promotion flags false. Packaging is not the LLM's implementation run.
- `cas-store`/`cas-verify` accept that candidate schema, not arbitrary screenshots or test logs. General artifact hashes belong to a separate manifest; they must not be described as stored by native R-ASI CAS.
- `experience-add` records content and an `evidence_ref`; it checks structure/dependencies, not whether the referenced evaluation is true or independent. It can point to actual external test results after they exist.
- Receipts (`rasi-receipt/v1`) are immutable canonical JSON under the selected root's `.ga/receipts`. The receipt hash concerns its bytes. Failed commands do not write receipts, so their observed outputs are saved by the external runner.
- `lock` validates component/runtime fields, not live checkout identity. `policy-check` validates policy completeness, not statistical correctness. `campaign-check` checks lock/policy references and structure, not candidate quality.
- `resume-check` checks stage identity, artifact bytes and cost completeness. `zones.vault` is a logical path policy, not process/filesystem/network isolation.
- `cost-add`/`cost-report` support measured and unmeasured events, but require an explicit valid campaign budget. There is no invented budget/conversion merely to make a check green. Incomplete costs remain unavailable and prevent a meaningful cost gate.
- No independent evaluator, secret holdout, actual LLM inference, Hermit/Harness²/KCO execution or promotion is supplied by this R-ASI revision.

Formal decision remains **HOLD** until the required independent evidence and complete runtime/evaluation identities exist. Working local tests and descriptor/CAS registration can still be performed and reported separately.

## Upstream tool verification

The pinned R-ASI upstream tests were executed without source changes in a dedicated temporary virtual environment (Python 3.12.14, pytest 9.2.0, Linux). Result: **147 passed, 2 failed**, exit 1, 11.86 seconds. Both failures expect the literal error text `深すぎ` for deeply nested invalid JSON; this runtime instead returns a top-level/schema validation error. Both inputs still receive exit 2 without a CLI traceback. Runtime-specific parser depth behavior is a plausible cause, not a demonstrated root cause. The suite is **not reported as passing**. This differs from the upstream README's historical Windows/Python 3.11 test result; current execution is authoritative here. Details: [rasi/upstream-tests.json](rasi/upstream-tests.json). These are tool tests, separate from B's design-flow tests.

## Actual sankai registration

[sankai-extraction.md](sankai-extraction.md) extracts 10 B units with 3 common conditions and 3 unresolved dependencies. It distinguishes current-file inheritance, source-index paraphrases and editorial operationalization. The machine representation is [rasi-input/sankai.json](rasi-input/sankai.json); its single source snapshot preserves campaign-authored notes and the current-file audit, not copyrighted external full texts.

`verify` → `pipeline` → `cas-verify` were actually executed, all exit 0. R-ASI verified 44 quote occurrences against the snapshot (286 lines). It did not independently verify that the campaign paraphrases faithfully represent the original publications. Execution log: [rasi/sankai-registration-cli.json](rasi/sankai-registration-cli.json).

- Native CAS object SHA-256: `5b35eb5daf879cffdb54114faa4b89af64b6094c008de756c49c4c1f8ed1da34`.
- R-ASI candidate content ID: `57d1b2372555c5493ab91e5ae679e2441581795c1998c1681fdc050b1abb7552`.
- Stored descriptor: `rasi/cas/objects/5b/5b35eb5daf879cffdb54114faa4b89af64b6094c008de756c49c4c1f8ed1da34.json`.
- Native immutable receipts: `.ga/receipts/verify-fe36fdf4f387bdd32827d72d149bc499fb23f6e50c17ef72421c51cef398cc5a.json`, `.ga/receipts/pipeline-03edde585a739a7cc3ee0befc66cddd8fdf79da592c6b470e08f812263c67634.json`, `.ga/receipts/cas-verify-5dfdd3e031bcae5b9f41291963b3c4144450da4d5b25a2da584d35626781732e.json`.

The descriptor remains `UNTRUSTED_CANDIDATE` / `quarantined`; `execution_connected`, `evaluation_connected`, `promotion_connected`, `promoted` and `registered` remain false. These identities concern the sankai packaging artifact. The actual Skill tree and runnable implementation require separate hashes and test evidence. Formal gate remains **HOLD**.

## Final external evidence recorded in native R-ASI

After the final Skill and comparison artifacts were frozen, native `experience-add` completed with exit 0. It recorded experience `B-UXFLOW-20261123-62f6f5075ca9-r1`. Exact command/output and pre/post integrity verification are in [rasi-final/registration-cli.json](rasi-final/registration-cli.json); [rasi-final/registration-summary.md](rasi-final/registration-summary.md) explains the result. The native record is `.ga/experiences/B-UXFLOW-20261123-62f6f5075ca9-r1.json`; native receipt SHA-256 is `59822d0433b98d0efdc0b6c14a0d7bacd322453e528745fb07a1a5181e63bcb4`.

The record points to `rasi-final/evaluation-evidence.json`, SHA-256 `c53da7c072a8a40f2c2b594bf023f28df8743943310a628e83bdc0e63a2501e9`. Its 78 referenced artifacts and the final Skill's 12 files were checked before and after native registration. R-ASI itself only validates the nonempty evidence reference, so these referenced-byte checks were performed by the external recorder and recorded separately. The receipt is proof of record storage, not independent evaluation or promotion.

Final implementation identity: commit `6fc0c3dd6c82c4dd2f77764c5da512fbfdbaa911`, Skill tree SHA-256 `62f6f5075ca97e48a4d811d6039cd27ce2488425915e1bd4c41a62da6619d1bf`. Generation used the earlier commit `58bed659cc7f39d316794625ad0475084b38df7e`, tree `1fba407c2a0452ad1f458c75bb6590cdc22e7c8a98bf04e2cc2554a317fb8ee5`. Neither identity is the sankai descriptor's content ID or CAS hash. The old `rasi-input` drafts remain historical records of the unconfigured formal campaign; final implementation/evaluation identities are in `rasi-final`.

Recorded external evidence includes final unittest 70/70, bundled Flow contracts 2/2, shared API simulation 9/9, generated Flow revalidation 2/2, and both original submitted arms at 40/40 in the common comparison. The score difference is zero: added efficacy is not established. Replaying those same generated modules does not establish the efficacy of the later corrected Skill. The limited separate-agent review resolved two findings but was not blind. Browser execution remained blocked. Formal gate remains **HOLD**, with no promotion.

Trial/cost histories preserve the reported intermediate 69/70 fixture correction and distinguish the later author-reported 66/67→67/67 development history from saved final evidence. Unknown token/billing/model/seed values remain null. Immutable pre-registration history snapshots remain hash-linked; native-registration timing and the late history supplement are recorded separately. No native cost ledger success is claimed.

## Reproduction

Use a checkout of R-ASI at the pinned revision. Set `PYTHONPATH` to that checkout. To keep all receipts within B, run the module with `--root evidence/B` from the extension repository. All path arguments after the subcommand are relative to this root; `--root` must precede the subcommand.

```sh
PYTHONPATH=/absolute/path/to/R-ASI python -m rasi --root evidence/B --version
PYTHONPATH=/absolute/path/to/R-ASI python -m rasi --root evidence/B lock --manifest rasi-input/lock.json
PYTHONPATH=/absolute/path/to/R-ASI python -m rasi --root evidence/B policy-check --policy rasi-input/policy.json
PYTHONPATH=/absolute/path/to/R-ASI python -m rasi --root evidence/B campaign-check --campaign rasi-input/campaign.json
```

The last three commands intentionally reject the incomplete drafts. Completing missing measured evidence is required before changing these results. Do not rewrite their saved failure output as success.
