# CopperPilot reference-circuit candidates

Use when the user requests CopperPilot assistance. This is a workflow, not a
bundled client, public-API claim or automatic image-to-KiCad converter.

Check official documentation and supported installed entrypoints for an API,
CLI or MCP. Prefer a documented interface tested for task submission/readback.
Internal HTTP/WebSocket clients, private packages or authentication deep links
do not establish an external design API. Do not extract credentials or call
private service endpoints as a substitute.

If no supported interface is verified, operate the installed UI with available
computer-use tools. Record version and actual interface tested. For requested
per-component assistance, confirm the selected KiCad component and page. Submit
exact part/package, function, voltages, load, interfaces and constraints; mark
undecided inputs. Discovery starting points: [official documentation](https://copperpilot.ai/documentation)
and [reference-diagram workflow](https://copperpilot.ai/documentation/product/design/reference-diagrams).
Recheck capabilities when versions change.

A quota warning or disabled submission is not a completed query. Continue
manufacturer research when authorized, with distinct provenance; do not call a
locally authored design a newly generated CopperPilot reference.

Request images/vector output, BOM, intended pin/net table, sources and placement
rationale where available. Preserve raw files and hashes. Check CSV quoting,
column counts and required fields before importing: commas in footprint fields
can shift columns. Report malformed rows rather than claiming import success.

Check exact devices, physical pin numbers and packages against manufacturer
documents. Distinguish unknown connections, DNP wired pads and intentional IC
NC pins; UNKNOWN must not silently become NC. Compare the picture with its pin
table. An apparent line contact, crossing, or SVG net name is not electrical
truth. Derive reviewed electrical intent and a separate placement plan.

Place actual KiCad symbols and visible connections using that intent; retain
cross-page ports explicitly. Verify root XML, ERC, geometry and native renders
as described in [electrical-redesign.md](electrical-redesign.md).

Report submission/readback, candidate parsing, independent intent review and
final KiCad verification as four separate outcomes. Success at one stage does
not imply later stages passed. Publish reusable methods and neutral fixtures,
not account data or private reference outputs.
