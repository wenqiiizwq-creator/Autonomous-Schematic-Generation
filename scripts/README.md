# ASG scripts — developer reference

## Deterministic generation and geometry

`build_circuit.py` compiles Circuit IR v2, resolves named pins/physical units,
automatically places and packs functional blocks, retries with bounded spacing,
and supports baseline diffs plus locked-block regeneration. See
[`circuit-ir.md`](../references/circuit-ir.md). `import_circuit_synth.py` imports
audited upstream JSON; `schematic_layout.importers.skidl_to_ir` reads an already
built SKiDL Circuit. Neither executes an input Python file.

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
optional reference and change contracts) and writes `summary.json`. Usage, options and
`AUTOMATED_PASS` semantics are in SKILL.md task 4.1; the low-level single-page
generator is described in [`schematic-generation.md`](../references/schematic-generation.md).

`deliver.py <delivery>` runs one delivery end to end in a fixed order (prepare,
closure audit, preflight, generation, `verify_schematic.py`, report, delivery
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
`schematic_layout.citations` checks `datasheet:<library path>#p<page>` citations
for the closure audit, the report and the ledger: a missing file or a page
beyond the document fails; a cited value the page text does not show is listed
for a person to check.

Native tests compare exact pin partitions. Tests are in `tests/`; optional
upstream source probes do not require installing the complete MCP server.
