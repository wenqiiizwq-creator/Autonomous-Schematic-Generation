# TPS53355 compact comparison draft

A4 synchronous Buck drawing: regulated 4.75–5.25 V to nominal 0.85 V, 15 A
comparison target, 500 kHz nominal in CCM, auto-skip, Rev C with 47 physical
components: 40 fitted and 7 DNP by default.

This is a presentation/regression example, not a production reference design.
Read `../../references/engineer-template-comparison.md` and the assumptions in
`calculations.json`. Input capacitor MPNs and effective capacitance/ESR,
production footprints/connectors, temperature and load-transient behavior need
engineering closure. Preserve the original 10 A baseline when comparing.

```sh
cd examples/tps53355_compact
python3 prepare_design.py
python3 calculate.py
python3 calculate_options.py
python3 verify_population.py electrical_intent.json --output population.json
python3 build_compact.py --out /path/to/new/TPS53355-Test-RevC
```

Run the commands from the repository root with the `cd` shown above.
The prepared `compiled.json` records library hashes and portable paths:
`example_directory` means this example folder, and `kicad_symbol_directory`
means the installed KiCad symbol folder. The writer records the actual resolved
library locations again in each output directory.

The writer rejects an existing output folder. `AUTOMATED_PASS` is only the
native/geometry gate; inspect the exported full page and crowded regions.
Default enable is automatic: R7 fitted, R9 DNP. External sequencing requires
R7 DNP, R9 fitted, and an externally driven/pulled EN signal meeting the TI
thresholds. Do not leave EN floating or connect a 5 V pull-up to an incompatible
upstream driver. Snubber C15/R11 and bleeder R12 are DNP tuning provisions.

RF pin 22 is now wired to option pads, not a no-connect marker. R13 (866k to
VREG) and R14 (187k to GND) are BOTH DNP for default 500 kHz (TI Rev G Table
7-1). Fit at most one; 650/300 kHz are documented setting codes, not released
alternate designs. The engineer image's two 100k/NC resistors are treated as
unpopulated placeholders, not supported default frequency-setting values.
`option-calculations.json` demonstrates the coupling: unchanged 300 kHz parts
give a conditional minimum ripple-network inequality margin below 1. Rework
the network and divider before using that option. Neither calculation proves
stability, transient response or component behavior over temperature.

MODE defaults to R5 fitted and R15 DNP. FCCM after PG requires swapping those
states and reviewing light-load/negative-current behavior. R10 (PG isolation),
R16 (VDD feed) and R17 (VREG external-bias link) are fitted 0-ohm links in all
supported profiles. This is external regulated 5 V bias, not a 10-ohm VDD RC
filter or a qualified internal-LDO alternate. C20/C21 add local VIN bypass;
C22/C23 add load bypass without crediting them toward minimum Ceff.

`verify_population.py` rejects conflicting RF/MODE/EN population, incomplete
snubbers, wrong option values/endpoints and unsupported bias-link changes. The
writer runs this default-population gate before drawing. `--baseline <intent>`
also compares the active baseline pins after removing DNP and collapsing fitted
zero-ohm resistors. This checks assembly connectivity, not analog equivalence
or arbitrary circuit validity; the usual pin/identity/ERC/geometry gates remain
required. Refer to TI pin Table 5-1, ceramic application Figure 8-2 and Section
8.2.1.2.3 for topology and calculations; values and control choices are adapted
for this operating point, not copied unchanged from one application figure.
