# Schematic Drawing Standards — Readable LM5013-Style Layout

## Purpose

This is the canonical drawing standard for **auto-generated and auto-redrawn
schematics** in both KiCad and EasyEDA Pro. It formalizes the rules that
produced the accepted LM5013 33.6V→12V block (`STANDARD_SCHEMATIC_NOTES.md`
in that project): a continuous left-to-right power bus, visible branches for
parallel parts, a common GND bus, and labels used only where they add clarity.

Read this file **before creating, editing, or redrawing any schematic**.

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Power-Stage Layout Standard](#2-power-stage-layout-standard)
3. [Component Placement & Orientation](#3-component-placement--orientation)
4. [Net & Label Policy](#4-net--label-policy)
5. [Wiring Rules (KiCad)](#5-wiring-rules-kicad)
6. [EasyEDA Pro Implementation](#6-easyeda-pro-implementation)
7. [Verification Gate](#7-verification-gate-mandatory-before-reporting-success)
8. [Canonical Example: LM5013 Block](#8-canonical-example-lm5013-block)
9. [Redrawing Existing Schematics](#9-redrawing-existing-schematics)
10. [Failure Modes to Avoid](#10-failure-modes-to-avoid)

## 1. Core Principles

1. **Power path is king.** A power schematic must let the reader trace the
   energy flow at a glance: input → switch → inductor → output. If the power
   path is not obvious, the drawing fails even if the netlist is correct.
2. **Readability gate before "done".** Connectivity is necessary, not
   sufficient. A circuit that passes ERC/netlist but looks like stacked
   components is not finished.
3. **Datasheet is ground truth for values.** Component values and topology
   come from the datasheet typical application / design equations; the drawing
   standard only governs how they are placed and connected visually.
4. **Tool behavior is a constraint, not a style choice.** Rules in this
   document that look "defensive" (split wires, stubs, labels at nodes) exist
   because KiCad/EasyEDA connectivity is coordinate-exact. Follow them
   mechanically.

## 2. Power-Stage Layout Standard

For every regulator / power block:

1. **Continuous power bus, left to right**, on a single horizontal line:
   `INPUT → IC → SW → L → OUTPUT`.
2. **Input caps, output caps, UVLO, feedback, enable, PGOOD** use **visible
   branch wires** to the bus — never hidden inside a pile of overlapping parts.
3. **Catch diode** connects with a short vertical stub: cathode to SW bus,
   anode to GND (symbol rotated so K is on top).
4. **GND uses a common bus** at the bottom of the block, with GND power
   symbols at the rail ends and an explicit `PWR_FLAG` stubbed into the
   relevant rail. Control-component grounds may use local GND symbols.
5. **Only key nets keep names**: power rails, switch node, feedback, enable,
   and other named functional nets (VIN, SW, VOUT, FB, EN, COMP, BOOT, ...).
   Use labels for remote connections only when a wire would cross the power
   area or another block.
6. **BOOT cap** routes above the IC between BOOT and SW (short top rail).
7. **Test points** sit on the rail they monitor (junction + pin), one per
   monitored rail.

## 3. Component Placement & Orientation

1. **IC anchors the block.** Input pins face left, output pins face right,
   control pins face down/left, GND/thermal pad at the bottom of the symbol
   (redesign the symbol if the stock symbol fights this).
2. **Power passives** (input/output caps, inductor) sit on or directly below
   the power bus.
3. **Control passives** (dividers, RT, COMP, filter networks) sit in an
   orderly band **between the power bus and the GND bus**, one column per
   function, aligned on shared X or Y coordinates.
4. **No component body overlaps.** Keep at least 1.27 mm clearance between
   symbol bodies; labels must not sit inside an IC body.
5. **Connectors**: input connector left, output connector right, pin 1 =
   power, pin 2 = GND.
6. **Orientation conventions**: capacitors vertical (pin1 top), resistors
   vertical or horizontal per net flow, inductors horizontal on the power bus,
   diodes vertical with K up.
7. **Functional blocks are separated**: each converter gets its own horizontal
   band; blocks never interleave.

## 4. Net & Label Policy

1. Name rails by voltage: `VIN_33V6`, `VOUT_12V`, `VOUT_5V`, `GND`.
2. Name functional nets by role: `SW`, `FB`, `EN`, `COMP`, `BOOT`, `RT`,
   `PGOOD`, `RIPPLE_INJ`.
3. **Suffix block-specific names** when two converters share a sheet:
   `SW_5V`, `FB_5V`, `COMP_5V`, `EN_5V` — never reuse `FB`/`SW`/`BST`
   unqualified for a second block (they would short the two circuits).
4. Label **only** the nets listed in §2.5 plus cross-block signals. Do not
   label every wire stub.
5. A label must sit at a wire endpoint (or directly on a pin, like the BST
   label in the LM5013 block) so it names exactly one net.

## 5. Wiring Rules (KiCad)

These rules are empirical, verified against KiCad 9.0.9:

1. **Every wire segment must terminate at a pin, junction, label, or power
   symbol.** A segment whose **both endpoints are component pins is dropped
   from the netlist** — never connect two pins with a lone wire.
2. **Split wires at every connection point.** A junction placed in the middle
   of a continuous wire does not reliably connect a stub; make the junction a
   wire endpoint instead. This is why the accepted LM5013 file breaks rails
   into segments at every cap/pin/junction.
3. **Pin-to-pin direct contact does not connect** in KiCad 9 (the skill's
   analyzer may say it does — KiCad's own netlist is the authority). Put a
   label or power symbol at the shared point (e.g., `COMP_NODE` label at
   R13.pin2 + C15.pin1).
4. **PWR_FLAG must enter the rail via a short branch wire**, not by being
   stacked on a wire.
5. **Work on the 1.27 mm grid.** Every pin, wire endpoint, junction, and label
   anchor must be a multiple of 1.27 mm to avoid off-grid warnings.
6. **Exact coordinates**: pin-to-wire contact requires exact equality; a
   0.001 mm difference is a disconnection.
7. After generating, the file must be re-read by KiCad itself
   (`kicad-cli sch erc` and `kicad-cli sch export netlist`) — never trust a
   third-party parser alone.

## 6. EasyEDA Pro Implementation

The same visual standard applies. For automated drawing in EasyEDA Pro,
**hand off execution to the `easyeda-schematic-draw` skill**, which already
implements a compatible layout engine:

- three-column grid layout (left input / center components / right output),
- short net-labeled stubs instead of long wires,
- per-pin readback verification after drawing.

Before that handoff, supply the EasyEDA runner with this standard's
requirements: continuous power flow ordering, explicit branch stubs, key-net
labeling, and the mandatory verification gate below.

## 7. Verification Gate (mandatory before reporting success)

A generated schematic is **not finished** until every item passes:

1. `kicad-cli sch erc` → **0 errors, 0 warnings**.
2. `kicad-cli sch export netlist` → every new pin is on the expected net
   (compare pin-by-pin against the design intent).
3. Schematic analyzer run → regulator/divider detection is sane; when the
   analyzer's Vout estimate is heuristic, verify against the datasheet Vref
   and report the corrected value.
4. No floating labels, no orphan wire endpoints, no wires crossing symbol
   bodies, no overlapping elements (geometry check).
5. PDF/PNG render + visual review: power bus is one continuous line, control
   band is readable, no component stacking.
6. Datasheet values confirmed (feedback divider, RT/frequency, caps, diode
   rating) with equations shown.

Never report success based on ERC alone, analyzer JSON alone, or API success.

## 8. Canonical Example: LM5013 Block

The accepted `lm5013_33v6_to_12v_wired` schematic is the reference
implementation:

- Power bus at one Y level: `J1 → C1/C2/C3 branches → U1 → SW → L1 → J2`,
  with C5/C6 branches on VOUT.
- GND bus at the bottom spanning the block width, GND symbols at both ends,
  `PWR_FLAG` stubbed into VIN and GND.
- D1: short vertical stub from SW rail to a local GND.
- Control (R1 RON, R5/R6 UVLO, R2/R3 FB, R7 PGOOD, R4/C7/C8 ripple) in an
  orderly band between the rails, each with a single labeled net.
- Only FB's remote connection uses a label; everything else is visible wire.

New blocks must replicate this structure, not just "be connected".

## 9. Redrawing Existing Schematics

1. Preserve electrical intent: refs, values, footprints, and net topology
   must not change unless the user asks.
2. Only geometry changes: positions, rotations, wire routing, label
   placement.
3. If a value looks wrong, flag it with a datasheet citation; do not silently
   change it during a redraw.
4. Apply the same verification gate after the redraw.

## 10. Failure Modes to Avoid

- Component stacking / cramming control parts into a narrow band.
- Off-grid coordinates (57 off-grid warnings = layout not finished).
- Two pins joined by a lone wire, or relying on pin-on-wire visual
  intersection.
- Labeling every stub (noise) or reusing block-shared names like `FB`/`SW`
  for a second converter (short circuit).
- Trusting the analyzer's "connected" verdict over KiCad's own netlist.
- Iterating by patching coordinates in place; when a layout is wrong,
  recompute the whole block geometry on grid and regenerate.
