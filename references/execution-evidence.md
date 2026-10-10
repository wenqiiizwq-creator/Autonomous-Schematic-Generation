# Drawing execution and evidence freshness

Use for board redraws and delivery handoffs, especially with a dedicated writer.

## What proves execution

`make_root()` builds symbols, placement and fields; it does not route. Record the
actual routing entrypoint, per-page local groups and routing results. A wrapper
which calls only `make_root()` must not claim ASG routing was executed. If a
project writer extends unsupported geometry or crossings, keep that adaptation
scoped and independently verify its native partitions and render.

Do not convert local labels to global labels by changing only the S-expression
tag. KiCad's text direction and outline differ. Recompute orientation, text
clearance and attachment stems, then inspect the native rendering. An inline
label whose outline covers the continuing wire needs a different anchor/stem.

Post-route cleanup is a design mutation. Before deleting a dangling tail, split
its segment at retained branches and label anchors. A visually redundant end
can share a segment with a real pin connection. Re-export native XML/ERC after
the final cleanup, artwork, label or field mutation; old PASS results expire.

## Readability evidence

Apply [human-readable-routing.md](human-readable-routing.md). Record the
actual paths inspected and unresolved reading obstacles, not only which
pages were opened. A fresh snapshot can preserve an unreadable drawing;
it does not establish that this separate review passed.

Before handoff, inspect each OPEN item's closure plan against its actual
obligation: owner, target/state, needed input or action, acquisition method,
acceptance boundary and affected reruns. Follow the distinctions in
[requirements-to-intent.md](requirements-to-intent.md): external evidence,
design guarantee, tool coverage and downstream handoff need different actions.
Report generic or mismatched closure text as a delivery gap; a fresh hash or a
written proposal cannot close it. Preserve the original item when later adding
actual evidence and the independent disposition.

## Snapshot gate

After the final exports/checks, save `delivery-evidence.json` in the project root:

```json
{
  "schema_version": 1,
  "root": "board.kicad_sch",
  "inputs": {"board.kicad_sch": "<sha256>", "child.kicad_sch": "<sha256>"},
  "outputs": {"board.xml": "<sha256>", "erc.json": "<sha256>", "geometry.json": "<sha256>", "board.pdf": "<sha256>"},
  "roles": {"netlist": ["board.xml"], "erc": ["erc.json"], "geometry": ["geometry.json"], "render": ["board.pdf"]}
}
```

Include every active sheet, project configuration, symbol table and local
`symbols/*.kicad_sym` input. Hash all cited outputs, including baseline-delta and
visual-review records when used; extra roles such as `identity`, `routing` and
`visual_review` are allowed. Store real SHA-256 strings, not the placeholders.

Run `python3 scripts/check_delivery_freshness.py <project>/delivery-evidence.json`
immediately before reporting delivery. It checks active hierarchy coverage and
rejects missing/mutated inputs, outputs and required role evidence. `FRESH`
means only that this declared snapshot is unchanged. It cannot prove that a
command ran or a reviewer looked at the PDF, and never upgrades an ERC failure,
geometry gap, inherited open issue or electrical NO_GO to PASS.

Keep raw checker findings beside exact per-object dispositions. Native global
label outlines and conservative body envelopes can need render reconciliation;
never suppress every label or every symbol finding by category. Do not promote
one project's routing adaptation into the reusable engine without a separate,
representative regression set.

Geometry coverage is narrower than native connectivity. Explicit sheet pin
coordinates are attachment anchors; an arbitrary point on a sheet frame is
not. Native field rotation/mirror changes text justification, not the stored
absolute field anchor. The calibrated hierarchical-label text offset does not
qualify its contour or intersheet fields; keep those coverage gaps and render
review. The standalone geometry gate accepts either documented board-net
format, without changing membership or ignoring cross-net contacts.

For incomplete selected-project annotations, report each missing symbol UUID,
instance path and available project contexts. Reference properties are locator
hints, not fallback identities. Native exported object/pin counts and resolved
source annotation counts are different domains; reconcile them before drawing
electrical or delivery-completeness conclusions.
