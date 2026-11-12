# ASG scripts — developer reference

## Deterministic generation and geometry

`generate_schematic.py` consumes separate electrical intent and layout JSON,
writes a new single-sheet project, and runs native ERC/XML/PDF verification.
`check_schematic_geometry.py` inspects a serialized native schematic read-only.
Both use `schematic_layout/` (standard-library runtime).

Readable pages are drawn with `schematic_layout.recipes.Sheet`
([`drawing-recipes.md`](../references/drawing-recipes.md));
`schematic_layout.pages.page_intents()` splits one board intent into page
intents with their external nets and rails, and `schematic_layout.root.Root`
assembles the built pages under a hierarchical root with the System_block
cover. `verify_schematic.py` runs every
automated drawing gate on a saved root sheet (ERC, intent partitions and
identity, hierarchy/PDF, symbol integrity, readability, per-sheet geometry,
an optional reference contract) and writes `summary.json`. Usage, options and
`AUTOMATED_PASS` semantics are in SKILL.md task C6.4; the low-level single-page
generator is described in [`schematic-generation.md`](../references/schematic-generation.md).

`blocks.py merge <design>` merges the block designs in `record/blocks/` (task C4.4) by board net name into
`record/electrical-intent.json` (task C5.1), checking each against `record/architecture.json` (ports from the flows'
`nets`, internal nets off board names, reference numbers in the block's `ref_range`); `blocks.py roundtrip` splits an
existing whole-board netlist by the page plan's blocks and merges it back pin for pin. See
[`modules.md`](../references/modules.md).

`knowledge_checklist.py build|check <design>` lists the items of the knowledge entries the
design used (requirement conditions, a selected scheme's must-calculate items, required
peripherals and pitfalls, a calculation method's steps) in `record/knowledge-checklist.json`
and checks each has a disposition; the C1 and C4 gates run the check.

`knowledge_gaps.py <delivery>` extracts `record/knowledge-gaps.json`, the places
where the design ran short of knowledge, from the module records.

`check_module.py <C1..C6> <design>` runs one capability module's gate on the
parts it owns (SKILL.md 架构, P7) and records the input/output fingerprints in
`record/modules.json`; `check_module.py return <design> --from C4.2 --to C3.3 …` records a
return to an upstream task; `check_module.py status <design>` lists the recorded
modules as OK, STALE or MODIFIED; `report` writes `模块报告.md` and `pack`
checks the delivery of a module run (task.json `modules`). `import_netlist.py`
turns a KiCad XML netlist into a design netlist, with the source's embedded
symbols as project libraries, for a C6-only run. `block_circuits.py <design>`
extracts module C3's product, one `record/block-circuits/<block>.json` per
architecture block, from `scheme-criteria.json` and `selection.json` (each
block and core role names its `block_id`), and checks the files against them. See
[`modules.md`](../references/modules.md).

`deliver.py <delivery>` runs one delivery end to end in a fixed order (prepare,
closure audit, generation, `verify_schematic.py`, report, delivery
evidence, freshness, packing) from the arguments in `record/deliver.json`; it
reads each step's status from its output and goes on only on PASS, DONE,
CONDITIONAL, INCOMPLETE, AUTOMATED_PASS or FRESH.
See [`delivery-report.md`](../references/delivery-report.md).
`operating_inputs.py` is the closure audit's check that a calculation's external
conditions (startup load, source impedance, ambient temperature...) have a source, and
its review list; see `design-closure.md` 工况输入的来源.
`object_matrices.py skeleton --intent … [--closure …] --out …` lists, from the design
netlist, every cell of the closure record's `matrix_version: 1` tables (supervised
rail threshold × each load, each part's operating/storage temperature × the
requirement, each port stress × each part on its path and the ground paths a
switched return opens, protection-state rows per latch/shutdown/reset block); the
closure audit calls its `audit()` and reports missing and failed cells. See
`design-closure.md` matrix_version.
`fill_pin_maps.py <delivery>` reads each part's datasheet pin table and fills
`datasheet_name`/`datasheet_type`/`datasheet_page` in `record/reference-input.json`
(`--write`); pins it cannot read stay unfilled and are listed with the reason. See
[`symbol-and-peripheral-contracts.md`](../references/symbol-and-peripheral-contracts.md).
`make_symbol.py` writes a rectangular KiCad symbol from a datasheet pin table (JSON/CSV) that passes the
symbol-integrity and native pin-text checks; `complete_pin_coverage.py` writes every pad of a stacked pin (KiCad
`[a,b]` or a library's hidden same-point copies) into the net that names one of them and a library's
no_connect pins into `no_connect`; `select_guidelines.py`
is the many-values wrapper of the shared `guideline_criteria.py select`.
`schematic_layout.citations` checks `datasheet:<library path>#p<page>` citations
for the closure audit, the report and the ledger: a missing file or a page
beyond the document fails; a cited value the page text does not show is listed
for a person to check.

Native tests compare exact pin partitions. Tests are in `tests/`; optional
upstream source probes do not require installing the complete MCP server.
