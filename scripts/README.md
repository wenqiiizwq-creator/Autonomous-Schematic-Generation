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
`AUTOMATED_PASS` semantics are in references/module-c6-schematic.md task C6.4; the low-level single-page
generator is described in [`schematic-generation.md`](../references/schematic-generation.md).

`blocks.py merge <design>` merges the block designs in `record/blocks/` by board net name into
`record/electrical-intent.json`, checking each against `record/architecture.json` (ports from the flows'
`nets`, internal nets off board names, reference numbers in the block's `ref_range`); `blocks.py roundtrip` splits an
existing whole-board netlist by the page plan's blocks and merges it back pin for pin. `import_netlist.py`
turns a KiCad XML netlist into a design netlist, with the source's embedded
symbols as project libraries, for a redraw. See [`modules.md`](../references/modules.md).

`fill_pin_maps.py <delivery>` reads each part's datasheet pin table and fills
`datasheet_name`/`datasheet_type`/`datasheet_page` in `record/reference-input.json`
(`--write`); pins it cannot read stay unfilled and are listed with the reason. See
[`symbol-and-peripheral-contracts.md`](../references/symbol-and-peripheral-contracts.md).
`make_symbol.py` writes a rectangular KiCad symbol from a datasheet pin table (JSON/CSV) that passes the
symbol-integrity and native pin-text checks; `complete_pin_coverage.py` writes every pad of a stacked pin (KiCad
`[a,b]` or a library's hidden same-point copies) into the net that names one of them and a library's
no_connect pins into `no_connect`.
`schematic_layout.citations` checks `datasheet:<library path>#p<page>` citations
for the component checks: a missing file or a page
beyond the document fails; a cited value the page text does not show is listed
for a person to check.

Native tests compare exact pin partitions. Tests are in `tests/`; optional
upstream source probes do not require installing the complete MCP server.
