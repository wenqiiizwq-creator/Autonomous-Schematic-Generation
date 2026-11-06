# ASG calibration benchmarks

Circuit cases live in the evaluation set shared with schematic-review (`原理图设计规范/评测集/`, located by `evals/eval_set.py`, override with `CIRCUIT_EVAL_SET`). `python3 evals/circuit_cases/run.py prepare --case <id> --out <new dir> --guideline-release <selected release>` gives ASG one circuit's requirements only; results go to `运行结果/ASG/` in that set. The benchmarks below are separate and stay here.

Three independent runners, with all third-party sources and outputs outside Git:

- `overstrict_bench/prepare.py --cache <scratch-cache>` copies and verifies SHA256-pinned historical originals. If absent, recover from the pinned GitHub commit and accept only exact SHA256. Derived native sources require the original historical cache. Actual per-item labels are in `labels.json`, with per-round extraction notes in `mapping.json`. `run.py --cache ... --out <new-scratch-output>` produces the G1/G2 matrix. Unavailable source/report, conflicting adjudications or indistinguishable coordinate entities stay UNMAPPED. Identical-verdict duplicate raw gate rows are retained as diagnostic units, not unique defects.
- `mutation_bench/prepare.py --cache ...` copies frozen candidate inputs including contract sources. `run.py --cache ... --out ...` runs all 17 defect types on all 10 candidate circuits. It compares every gate to an unmodified baseline. A baseline FAIL needs a new target-specific finding; PASS→FAIL also counts. Invalid native no-op probes and missing topology/contract preconditions are separate from misses. UUIDs are deterministic. `recompute.py --run ...` may repair measurement parsing on preserved raw reports with hashes, without rerunning native verification or editing drawings.
- `delivery_replay/prepare.py --cache ...` verifies and caches prior audited replay helpers, whose dependencies are the archived local historical deliveries/tasks. `run.py --cache ... --out ...` records helper/path adaptations, literal rebuild results, raw gates, and frozen-native component identities/partitions. Round 02's known inherited AREF collision is separate. Missing historical input is NOT_RUN; no source is silently substituted. This bench is locally reproducible from this archive, not yet a remotely portable delivery fetcher.

Run with any Python 3 interpreter (`-B`, `PYTHONDONTWRITEBYTECODE=1`); child steps reuse the same interpreter. `--out`, `--cache` and scratch paths may be anywhere outside this skill (default: `$ASG_WORK_DIR`, else the system temp dir); each `--out` is fresh. Native outputs are measurement evidence, not human SR or hardware acceptance. Third-party CAD/PDF files never enter this repository.

`compare_calibration_runs.py --before <suite-result> --after <suite-result> --out <report> --before-commit <expected-sha> --after-commit <expected-sha>` expects `overstrict`, `mutation`, `delivery` result subdirectories. It requires the same benchmark input fingerprint and per-row source repository/commit/page/gate/rule/objects/coordinates. Mapping repairs require a separately versioned baseline. It rejects G2 loss, measured-set shrinkage or remapping to UNMAPPED, missing sources/reports, mutation catch regressions, or historical native netlist changes. It does not grant publishing authorization.

The frozen d43 baseline G1 is the number still reported, not the full historical label count. Previously absent historical false positives are not improvements by this batch. The mapped REAL set excludes historical REAL labels which remain UNMAPPED; retain that coverage gap explicitly.

Revision 2 requires external expected ASG HEADs, actual command ROOT provenance, identical mutation baseline source hashes/plans/changed inputs, and identical delivery original helper/frozen XML hashes. Geometry INSUFFICIENT with normal exit 2 supports exact positive findings only; missing findings remain unmeasured. Unknown schema, missing report, mismatched exit code are unmeasured and reject guards. Revision-1 frozen evidence remains retained.

Revision 3 is an explicitly selected, new baseline: use `--revision 3` on the
mutation/delivery prepare and run commands. Default revision 2 preserves the
old ten circuits and frozen 170-cell results; never rewrite them. Incremental
`incremental_deliveries.json` pins the rehearsal's own `designer/delivery`
archive subset and batch-2 original frozen deliveries `b2-r01-v1` through
`b2-r03-v1`, with distinct IDs. Keep both outer final freeze and design freeze
hashes. Copy verified payloads to fresh scratch caches; no third-party original
CAD, archived answers, review ledgers or current task enter the repository.

The additional delivery mode is **frozen-native replay**, not generator build
replay: it runs current gates on an unchanged copy and compares native physical
pin partitions/component identity with the explicitly pinned frozen XML.
`generator_build` stays `NOT_RUN`. Missing package files are listed individually;
the rehearsal archive omits some frozen PDFs, so a whole-freeze or reference
source verification claim is unavailable. Batch-2 round 02 has no functional
CAD: its complete functional native comparison and all mutation cells remain
`NOT_RUN`; System_block XML cannot stand in for the missing board.

Revision-3 native probes distinguish `TOPOLOGY`, `IDENTITY`, `NAME_ONLY` and
`NATIVE_NO_OP`. Unchanged physical groups with changed actual XML net names are
`NAME_ONLY`, including changed label or power names; an edit with no native
change remains `INVALID_PROBE`. A NAME_ONLY row is CAUGHT only by a new,
partition-attributable `intent_netlist/net_name_mismatch` on the changed actual
name. An unrelated inherited FAIL, ERC failure or generic PASS-to-FAIL does not
catch it. Keep probe kind separate from CAUGHT/MISSED outcome. Missing native
evidence stays `NOT_RUN`.

The old rounds 04/05/06/09 M-PIN-SWAP NAME_ONLY cells must be listed in the new
revision's evidence; retain their old revision-2 INVALID_PROBE records and old
170 counts. Establish revision-3 before/after on the **same** verified input
fingerprint and fixed ASG commit per run. A comparison across revisions or
different incremental fingerprints is rejected. Root must run the full suite
and all three benchmarks, review changed names/encoding/hierarchy boundaries,
then approve applying this benchmark revision; this patch does not publish a
new score or activate G1 glyph/label changes.

### Revision-3 measurement protocol: immutable output binding

The rejected first revision-3 proposal allowed an output created under revision
2 to be resumed and relabelled as revision 3. Keep those outputs and the failure
report; establish a fresh baseline under this corrected protocol. Never reuse
or recompute those rows as the new baseline.

All three runners exclusively create `run-binding.json` before executing any
measurement. It records the actual Git HEAD, tracked and non-ignored untracked
source bytes, all cache bytes and prepared manifest SHA, corpus fingerprint,
revision, suite and requested types. Mutation resume verifies that exact
binding **before any output write or cached report reuse**. Legacy unbound
outputs and changes to revision, inputs, types, HEAD or same-HEAD dirty source
must use a fresh output. Cache/output directories must be outside the checkout.
Final summary creation rechecks source/cache snapshots and the binding SHA
remembered at invocation start. This is not continuous filesystem monitoring;
the controller must hold the source lock and never commit during measurement.
Bound outputs cannot be reparsed with in-place `recompute.py`.

Revision-3 comparisons require all three immutable binding receipts, verify
their actual files/SHA, and check HEAD, suite, revision and input fingerprint
against each summary. The historical unbound revision-2 protocol remains
readable separately; it cannot supply a corrected revision-3 baseline.

Native identity schema 2 checks value, footprint, MPN, libsource and actual XML
marker properties for DNP, BOM exclusion and board exclusion. These flags are
not child text fields in KiCad 10.0.6 XML. Contradictory/unknown flag encodings
raise a qualification error. Arbitrary user fields and all library pin
definitions are outside this finite identity schema; do not call it complete
assembly or electrical correctness. Native pin partition equality and semantic
name delta remain independent measurements.

#### Optional automatic-looking manual-name probe

Revision 3 supports an explicitly requested `--types M-NAME-AUTO-LIKE` extension.
The default `TYPES` list remains the original 17 operators; revision-2 selection
rejects this extra type. Unknown type names are rejected before outputs are
created. The incremental corpus fingerprint is unchanged.

The operator changes one existing unique, quoted scalar local/global/hierarchical
label literal to a hand-written `Net-(ASG-PROBE-SDO/SAO)` name. Every other source
byte, UUID, placement and style is preserved; the rendered text extent may change.
Bus/encoded names and sheet-linked hierarchical interfaces are unsupported;
missing eligible labels produce `OUT_OF_SCOPE`. It never edits intent or rewrites
native evidence. Actual exports must show NAME_ONLY with the same physical
partitions and finite component/assembly identity. Capture requires a new,
attributable `intent_netlist/net_name_mismatch` for the renamed native partition;
an inherited failure, ERC error or generic PASS→FAIL does not count.

Run optional Before and After into fresh, separate outputs using the same source
cache and operator bytes. Their immutable run bindings must record different
actual verifier source snapshots. Do not resume a Before directory with After
code or relabel an old matrix. Keep these extension measurements separate from
the default 14×17 matrix (238 cells), old 170 rows and the corrected-before freeze.


External circuit runs require an explicit release package; IDs/status come from it, never the adjacent current registry. The package must match the installed skill payload. prepare writes run-context.json with the release version/fingerprint/format, E HEAD and actual dirty workspace digest, case/source hashes and skill HEAD/source digest. It discloses no answers; route cases stop at the documented step-① scope. score requires that recorded context and rejects changed or unbound inputs. Missing E prints status=skip/scope=external_evaluation separately from the local code gate. Current instructions: the evaluation set's 发布绑定.md. Native/code regression fixtures remain local.
