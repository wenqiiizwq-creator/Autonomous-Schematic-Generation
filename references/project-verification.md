# Verify multi-page delivery and intentional electrical changes

Both tools are read-only, emit JSON and exit nonzero for `FAIL` or `INSUFFICIENT`.
They neither generate a hierarchy nor certify hardware.
Choose a fresh `--out` path for every run. Existing files, symlinks and hardlink
aliases are rejected before processing, and reports are created exclusively.
This also protects malformed input files from being overwritten by error reports.

## Hierarchy and complete PDF

```sh
python3 scripts/audit_project.py candidate/board.kicad_sch \
  --pdf candidate/board-complete.pdf --expected-pages 12 \
  --baseline baseline/board.kicad_sch --out output/project-audit.json
```

Use the actual expected count, or omit `--expected-pages`; 12 is an example.
Optional Poppler `pdfinfo` reads the real PDF page count. Missing requested PDF
coverage is `INSUFFICIENT`. Count equality does not prove page content/order:
export the current root through KiCad, bind its hash, and review the PDF.

The root directory is the delivery boundary. The tool follows `Sheetfile`,
resolves `${KIPRJMOD}`, counts every instance (including reused child files),
reports missing files/cycles and records file hashes. Nonportable paths and
unresolved variables fail. Missing project annotation is a coverage gap; use
`--project NAME` if the root filename differs from the annotation project name.
Nonconsecutive page identifiers are legal; duplicate identifiers are reported.

Reference/unit pairs use the selected instance context. Shared cached library
IDs must agree; multi-unit references must share a complete consistent pin
definition. Signatures cover unit/style, number/name/type/shape/hidden state
independently of artwork. Unresolved symbol inheritance is insufficient. This
also checks active unit pins and agreement with the instance annotation. It
does not resolve `sym-lib-table`, check footprint pads or assess graphic layout.

With `--baseline`, file/instance/reference and pin-signature changes are reported.
This delta is descriptive, not approval of removals or arbitrary changes. Bind
the expected page list and protected files to the authorized scope.

## Electrical-change contract

Export both root netlists as `kicadxml`, then run:

```sh
python3 scripts/verify_design_change.py baseline.xml candidate.xml \
  change.json --out output/design-change.json
```

A complete minimal contract for a resistor value change:

```json
{
  "schema_version": 1,
  "component_changes": {
    "R1": {"value": {"before": "1k", "after": "2k"}}
  }
}
```

Only that identity change is permitted; all physical partitions and other
component properties must remain unchanged. Set `baseline_sha256` to the frozen
XML hash for stored/reused contracts. Reports bind both actual XML hashes.

| Optional field | Meaning |
| --- | --- |
| `remove_components` | Unique list of baseline references; affected nets also need explicit replacement. |
| `add_components` | New reference → `{ "identity": ..., "pins": ["1", "2"] }`; list all physical pin numbers. |
| `component_changes` | Existing reference → identity field → exact `before` / `after`; verify the baseline precondition. |
| `replace_partitions` | List of `{ "before": [["J1.1", "R1.1"]], "after": [["J1.1"], ["R1.1"]] }`; each inner list is a complete physical net. Empty outer lists mean no nets, not empty nets. |
| `named_nets` | Required exact candidate names → complete pin sets; declare interfaces whose names matter downstream. |
| `same_net` | Lists of at least two known physical pins that must share a net. |
| `distinct_net` | Lists of pins that must all be on separate nets; this does not prove galvanic isolation. |

An identity has exactly `value`, `footprint`, `datasheet`, `lib_id`, `dnp` and
`fields`. Text values are strings, `dnp` is Boolean, `fields` is a string map.
Example: `{ "value": "10k", "footprint": "", "datasheet": "", "lib_id":
"Device:R", "dnp": true, "fields": {} }`. Blank fixture fields do not qualify
a real BOM. Review presentation-driven library-ID changes explicitly.

Every replaced `before` partition must exist once. The final expected graph must
retain every remaining baseline pin and all declared new pins exactly once.
Unknown, duplicate, missing and invented pins fail. `#` references are virtual
and excluded consistently; physical NC singleton nets remain significant. Local
net names may change without changing partitions; use `named_nets` for important
names. Expected partitions must come from independent intent, not the candidate.

Native exported pins are not independent datasheet evidence. This tool does not
check package mapping, unexported hidden pins, assembled DNP operation or analog
performance. Keep source tables, footprint/population and performance checks.

```sh
python3 -m unittest discover -s tests -p 'test_project_audit.py' -v
python3 -m unittest discover -s tests -p 'test_design_change.py' -v
```
