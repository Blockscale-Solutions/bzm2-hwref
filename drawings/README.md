# Drawings

Original editable SVGs for the hardware reference (charcoal + teal). Generated or hand-authored from **published** `references/` only — no Product Brief tracing, no invented pad IDs / voltages / opcodes.

| Path | Issue | Source |
| --- | --- | --- |
| `pinout/bzm2-padmap.svg` | #14 | `references/bzm2-ballmap.csv` + pinout reference (regen: `scripts/generate_padmap_svg.py`) |
| `bring-up/power-up-sequence.svg` | #16 | Integration Guide Mermaid + Board §7/§9 |
| `rails/single-asic-rail-stack.svg` | #15 | Integration Guide Core Rails; multi-ASIC = gap (#4) |
| `uart/uart-9bit-character-frame.svg` | #13 | UART Physical Layer |
| `uart/tdm-frame-and-result-path.svg` | #13 | UART TDM / Result Aggregation / TX `0x0A` + public OSS packing; **opaque slot**; four labeled gaps |
| `process/job-to-result-path.svg` | #17 | Integration Glance + Mining Programming Model + UART job/result/TDM; TDM opaque; devices/HB = gap |
| `lab/rds-*-chart-placeholder.svg` | #18 | Empty frames + schema only — **needs measured RDS data** |

Captions on each SVG cite the source sections.
