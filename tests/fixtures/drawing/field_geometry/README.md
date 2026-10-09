The 96 placements in field-matrix.kicad_sch are synthetic. native-matrix.json
records the field stroke bounds exported by KiCad 10.0.6 SVG, across four symbol
rotations, no/x/y mirror, field angles 0/90 and centre/left/right/left-bottom
justification. These establish placement and anchor direction, not universal
font metrics. The matrix uses a Device:C cache extracted from the source below.

The two <=3KB mirrored-field fixtures retain one cached capacitor and its
fields from circuitdojo/nrf9151-feather, commit
43c5345c791a2980d2780249f40804ea39342cf9 (CERN-OHL-S-2.0, License.txt).
The negative fixture adds a foreign wire that crosses the actual native text.
No complete third-party circuit is bundled.
