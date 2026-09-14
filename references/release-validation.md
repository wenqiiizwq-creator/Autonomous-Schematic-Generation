# Publication validation — 2026-09-14

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
