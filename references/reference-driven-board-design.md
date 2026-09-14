# Reference-driven board generation

Use this workflow when a generated board has incomplete IC peripherals or an unreadable multi-page layout. A datasheet URL, a pinout table, or an ERC pass does not establish application-circuit completeness.

## Establish a reference contract before placing the IC

For each exact IC/package/operating mode, record the manufacturer document revision, file hash, pages/figures actually read, and these circuits where applicable:

- Every supply domain, exposed pad, internal regulator output, local bypass/filter and return.
- Clock source, load/ESR/drive assumptions, reset timing, boot/address/mode straps and host behavior during reset.
- The complete functional path: feedback and energy storage for converters; divider/burden/filter and bias for measurement; magnetics/termination/protection for interfaces.
- Required, conditional, optional/DNP and inapplicable branches. Explain every departure from the reference and verify its coupled constraints.
- Real reference and pin numbers, values, tolerances, voltage/current/power limits, assembly state and component-selection unknowns.

Store a machine-checkable contract beside the electrical intent. Test it against the native exported netlist, then deliberately remove a required capacitor, move a return to another ground, fit a DNP or change a resistor value. The check must reject these mutations. A contract only establishes the explicitly listed facts; uncovered ICs, timing, physical margins and silicon behavior remain unverified.

`examples/controller_reference/verify_peripherals.py` demonstrates narrowly scoped KSZ8081RNA power/pull-up/strap/clock/magnetics checks. It is not a general electronics approval engine.

## Learn engineering composition from actual PDF images

Inventory the actual PDF page count and titleblock identity. Render a contact sheet of all pages, then inspect full-size power, MCU/configuration, memory, interface/protection and repeated-channel examples. Do not substitute text extraction for visual inspection. If a PDF's drawing occupies only part of its MediaBox, measure the drawing frame, not the blank page margin.

Record project-local source/page evidence; keep proprietary PDFs and screenshots out of a public skill bundle. Transfer these presentation rules, not another IC's circuit values:

- Place a complete functional circuit as a block. Power flows toward the load; feedback returns visibly to the correct input. Put local bypass banks beside the associated rail and join them with visible rail/return wires.
- Keep clock, reset, bias, strap and protection branches by their associated pins or in a clearly labelled adjacent configuration block. A board is not a shelf of IC boxes followed by a shelf of resistors.
- Choose standard functional symbols first. Preserve every physical pin. Shared drawn tips are allowed only within one symbol, with equal geometry and the same connected net. Hidden passive copies remain in the native pin ledger; conflicting assignments must fail.
- Bus and cross-page labels are appropriate. Explicitly plan them. Do not silently turn a failed local route into a label connection.
- Organize pages by function, isolation/voltage boundaries, readable drawing area and cross-page dependencies. Equal component counts are not the objective. Merge sparse related complete blocks; split dense memory/power units along actual domains.
- Keep a repeated circuit's orientation, local passive pattern and field style consistent. Do not separate every NC unit into large independent pages.
- Inspect entire rendered pages and dense regions. Zero text/body collisions does not prove sensible composition, short loops, readable pin grouping or balanced pagination.

## Recover a rejected board

For an authorized layout-only improvement of an existing hierarchy, use
[existing-project-redraw.md](existing-project-redraw.md). Its baseline/delta
checks preserve the circuit; they do not close missing datasheet or peripheral
evidence. Do not mix a drawing change with unrecorded electrical repairs.

Preserve the rejected baseline and record why it was rejected. First repair and render representative power, precision analog and digital interface pages using the skill's real generation APIs. Publish their scope and unresolved ERC/pin/MPN issues honestly. Do not describe a few improved samples as a repaired full board. Apply accepted templates to the rest of the hierarchy only with per-page electrical contracts, render evidence, requirement coverage and exact native netlist comparison.

A regulator with a complete ten-part application circuit need not acquire more parts merely because another design has more. Conversely, an input header connected straight to an ADC is not a complete sensor interface: burden, common-mode, protection, filtering and range require evidence.
