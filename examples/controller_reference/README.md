# Controller reference-driven validation samples

These samples repair specific failures found in a rejected board generator. They use the skill's native symbol resolver, functional placements, explicit local wire groups, geometry QA, and KiCad CLI exports. They do **not** implement or qualify a complete ACU/TCU board.

```sh
python3 examples/controller_reference/build_power_pair.py --out /absolute/new-output
python3 examples/controller_reference/build_phy.py --out /absolute/new-output
python3 examples/controller_reference/verify_peripherals.py /absolute/new-output/TCU-Ethernet/native/netlist.xml --out /absolute/new-output/TCU-Ethernet/peripheral-check.json
```

`build_reference.py` additionally retains the isolated U201 buck probe. Generated native files are hash protected on subsequent runs; use a fresh output directory for modifications. Each result has a native schematic/project, electrical intent, layout, source-library hashes, native XML, raw ERC, PDF and geometry report. A generation failure is recorded as `failure.json`; a later successful generation clears the stale failure record.

Sources and intended changes:

- TI TPS62130, SLVSAG7F Fig9-1. Same physical net partitions as the source U201/U202 circuits. Stock shared-pad symbol replaces the numeric box; output setpoints are 5.000 V and 3.296 V nominal. MLCC package candidates enlarged; MPN and effective capacitance remain open.
- Microchip KSZ8081RNA, DS00002199D pp6-9/23-24/43-44. Correct 2.2uF core bypass, separate analog ferrite/22uF+100nF and I/O 22uF+100nF, 1k MDIO/IRQ pulls. External address-0 and RXER low bias are deliberate reset-robustness choices, still contingent on host behavior. Crystal loading and ferrite impedance are candidates, not guaranteed application values.
- `reference_roles.json` declares exactly which capacitors serve each local supply pin. `verify_peripherals.py` checks 17 listed facts against the native netlist and excludes DNP. It cannot borrow a remote capacitor from a shared board supply to satisfy a local bypass requirement. Run `tests/test_reference_peripherals.py` for negative mutations.

All unselected MPNs, capacitance bias, reset/clock timing, load/thermal/transient limits, EMC and full-board integration remain open. Isolated sample exports intentionally retain external-source/host ERC findings; no power flags or exclusions were inserted just to clear them. Geometry/netlist/peripheral PASS states are independent and never mean production release.

Private engineer PDFs used to study composition are excluded. The reusable lessons are in `references/reference-driven-board-design.md`.
