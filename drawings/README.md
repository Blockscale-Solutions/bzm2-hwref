# Drawings

Original editable SVGs for the hardware reference (charcoal + teal). Generated or hand-authored from **published** `references/` only — no Product Brief tracing, no invented pad IDs / voltages / opcodes.

| Path | Issue | Source |
| --- | --- | --- |
| `pinout/bzm2-padmap.svg` | #14 | `references/bzm2-ballmap.csv` + pinout reference (regen: `scripts/generate_padmap_svg.py`) |
| `bring-up/power-up-sequence.svg` | #16 | Published SoT for bring-up flow (arm gate + terminal STOP); Board §7/§9. Editable Mermaid sibling: `bring-up/power-up-sequence.mmd` |
| `rails/single-asic-rail-stack.svg` | #15 | Integration Guide Core Rails; multi-ASIC → Voltage-Stack Examples (#31) |
| `rails/stack-example-bitaxe-4s1p-4s2p.svg` | #31 | bitaxeBIRDS @ 11d188d and bitaxeBonanza @ 51b31ad public KiCad schematics (net names as drawn); nominal 0.71 V/ASIC from Integration Guide; failure notes inferred |
| `rails/stack-example-rds-readings.svg` | #31 | RDS structure only (3 boards, 25 stacks × 4, shared rail); leading 25s4p vs superseded 2s2p, both unconfirmed; arithmetic on nominal 0.71 V/ASIC — **no RDS measurements** |
| `uart/uart-9bit-character-frame.svg` | #13 | UART Physical Layer |
| `uart/tdm-frame-and-result-path.svg` | #13 | UART TDM / Result Aggregation / TX `0x0A` + public OSS packing; **opaque slot**; four labeled gaps |
| `process/job-to-result-path.svg` | #17 | Integration Glance + Mining Programming Model + UART job/result/TDM; TDM opaque; devices/HB = gap |
| `lab/rds-*-chart-placeholder.svg` | #18 | Empty frames + schema only — **needs measured RDS data** |

Captions on each SVG cite the source sections.
