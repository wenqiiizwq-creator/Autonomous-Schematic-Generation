# Publication validation — 2026-09-15

## Current local integration: symbol and reference contracts

| Check | Result |
| --- | --- |
| Full regression suite | 136 tests passed, no skips: prior 101 plus 35 attachment/source/pin/peripheral/stage and native gate tests. KiCad 10.0.4. |
| Native failure probe | An intentionally shortened internal resistor leg, with the electrical tip unchanged, retained exact native netlist agreement but failed the new symbol gate. A supplied incompatible reference contract also blocked acceptance despite passing native pin partitions and symbol checks. |
| Local project reproduction | All 44 active pages, 915 physical components and 3253 pins covered. Before repair: 35 attachment candidates; after repair: 2. The 33 corrected candidates match the previous audit. Remaining isolated NC terminals retain candidates pending explicit disposition; no blanket NC suppression. |
| Source/peripheral mutations | Reject changed document hash, exact package/MPN or electrical type mismatch, incomplete pin map, removed required capacitor, wrong return/value, DNP required endpoint, shorted rails and absent declared stage. Missing document/scope stays INSUFFICIENT. |
| Geometry distinctions | Regressions include thick capacitor plates, sloped triangles, clockwise/counterclockwise arc sweeps, reused hierarchy instances, missing annotation, hidden/zero-length pins, separate bodyless supply units, unsupported geometry and stale exceptions. |
| Runtime integration | Shared native verification invokes symbol audit. Both generation entrypoints accept optional `--reference-contract`; supplied contract failures block automated acceptance. Datasheet/native visual review remains pending. |
| Skill/package checks | Skill structure validator passed; 74 Python files parsed; links in changed documentation resolve. Changed public files contain no concrete private user paths or board names. |

These checks verify bounded facts, not source authority, adequate requirements,
semantic stage implementation, footprint dimensions, zero-ohm/alternate assembly
behavior or electrical performance. The new public fixture uses fictional parts
and a synthetic specification. Private full-board regression inputs stay local.

## Previous local publication: hierarchy and electrical changes

Current publication extends the previous revision with read-only hierarchy and
native electrical-change verification. The existing layout/router backend is
retained. These checks are not a production review of a board.

| Current check | Result |
| --- | --- |
| Complete test suite | 101 tests passed, no skips: the existing 69 plus 32 hierarchy/change-contract regressions. |
| Native change probe | KiCad 10.0.4 exported a before/after RC fixture with an explicitly changed resistor value and swapped physical terminal connections. The independent intended change passed; an undeclared change failed. |
| Delivery check on a local project | 44 hierarchy instances, 915 physical components and the actual 44-page PDF agreed; no missing child files or cached-definition conflicts. Private source files are not distributed. |
| Wrong-version PDF | Pairing that root with an old 36-page PDF returned FAIL and a page-count mismatch. This tests count detection, not arbitrary PDF content equivalence. |
| Skill structure | `quick_validate.py`: passed. |
| Python syntax | 68 source files in scripts/tests/examples parsed successfully. |
| Independent forward check | 20 bounded cases found four defects involving malformed-child report overwrite, hardlink aliases, absent symbol units and missing XML pin attributes. All were fixed; five targeted reproductions were rerun and every input hash was unchanged. |
| Packaging | No existing runtime script removed or changed; staged diff and relative links checked. No concrete private user paths or recognized credential patterns in published files. Generic `/home/user/` documentation examples are retained. |

Native XML, logs and private-project audit outputs remain local under `output/`;
public neutral failure fixtures are in the test suite. The current full suite
also exercises the earlier generation, population and native-export cases.
The four standalone commands listed in the historical entry below were not
individually repeated for this update; their underlying code was unchanged.
CopperPilot live service submission, arbitrary multi-page generation, newly
generalized hierarchy/global-label geometry and electrical performance are not
claimed as tested features of this release.

## Previous publication — 2026-09-14

Environment: macOS, KiCad CLI **10.0.4**, installed KiCad symbol libraries,
Python virtual environment, Poppler `pdftoppm`. These results cover the
published generation code and examples, not every existing analysis script or
an electrical/production review of a board.

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | 69 tests passed, no skips. Includes native XML/ERC/PDF checks, bad-geometry fixtures, physical pins, multi-unit/shared terminals, imports, protected regeneration and population/peripheral mutations. |
| Skill frontmatter/structure validator | Passed. |
| Python source compilation | 62 files parsed successfully. |
| README quickstart: dual RC modules | `AUTOMATED_PASS`; geometry and exact native netlist passed; ERC 0 errors / 0 warnings. |
| TPS53355 compact recipe | Re-prepared portable inputs and generated successfully; geometry and native netlist passed; ERC 0 errors / 0 warnings; default population check passed. Electrical and final design review remain pending. |
| TPS62130 two-stage power recipe | Geometry and native netlist passed; `REVIEW_ONLY`, with 3 `power_pin_not_driven` errors / 0 warnings in the isolated sample. |
| KSZ8081RNA PHY recipe | Geometry and native netlist passed; 17 scoped peripheral checks passed against exported XML. `REVIEW_ONLY`, with 7 errors / 7 warnings for undriven host/power connections and isolated interface labels. |
| Native rendering | All four generated PDFs rasterized and inspected at full-page scale. This publication check is not a full electrical review or detailed visual acceptance of every region. |
| Source and packaging | Recorded upstream file hashes matched the local pinned checkouts; retained all four MIT license texts. No private user paths or recognized credential patterns in the publication tree. Private project outputs, reference PDFs and caches excluded. |

ERC numbers are the native report with its recorded default rule settings;
they are not a claim that every possible rule is enabled. The two isolated
reference samples retain their findings and do not add power flags or exclusions
to clear them. A successful process exit is not equivalent to an ERC PASS.
Raw ERC, XML, PDF and verification JSON are produced locally by the commands
below; transient output folders are not part of the skill package.

Run from the repository root, using fresh output directories:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_circuit.py \
  tests/fixtures/generation/dual_filter.circuit.json \
  tests/fixtures/generation/dual_filter.presentation.json \
  --output-dir output/publication/dual-filter
python3 examples/tps53355_compact/prepare_design.py
python3 examples/tps53355_compact/build_compact.py \
  --out output/publication/tps53355
python3 examples/controller_reference/build_power_pair.py \
  --out output/publication/power
python3 examples/controller_reference/build_phy.py \
  --out output/publication/phy
python3 examples/controller_reference/verify_peripherals.py \
  output/publication/phy/TCU-Ethernet/native/netlist.xml \
  --out output/publication/phy/TCU-Ethernet/peripheral-check.json
```

The optional upstream-source probes were not rerun for this publication. They
require separately downloaded pinned repositories and extra runtimes; ordinary
generation and the 69-test suite do not need those checkouts. Existing analyzer
Python syntax was checked, but this is not a behavioral regression of every
schematic/PCB/Gerber analyzer. New hardware designs still need their exact
datasheets, requirement coverage and independent verification.
