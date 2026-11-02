# Drawings (contributor notes)

Working notes for people editing the figures under `drawings/`. This file is not published on the Pages site; keep reader-facing figure text and captions free of process notes (see [CONTRIBUTING.md](../CONTRIBUTING.md)).

Original editable SVGs for the hardware reference (charcoal + teal). Generated or hand-authored from **published** `references/` only — no Product Brief tracing, no invented pad IDs / voltages / opcodes.

| Path | Issue | Source |
| --- | --- | --- |
| `pinout/bzm2-padmap.svg` | #14 | `references/bzm2-ballmap.csv` + pinout reference (regen: `scripts/generate_padmap_svg.py`) |
| `bring-up/power-up-sequence.svg` | #16 | Source of truth for the bring-up flow (arm gate + terminal STOP); Board §7/§9. Editable Mermaid sibling: `bring-up/power-up-sequence.mmd` |
| `rails/single-asic-rail-stack.svg` | #15 | Integration Guide Core Rails; multi-ASIC → Voltage-Stack Examples (#31) |
| `rails/stack-example-rds-readings.svg` | #31 | RDS structure only (3 boards, 25 stacks × 4, shared rail): 25s4p determined by analysis, 2s2p ruled out; 50 domains vs 25 ASIC levels; arithmetic on nominal 0.71 V/ASIC — **no RDS measurements** |
| `rails/stack-example-bitaxe-4s1p-4s2p.svg` | #31 | bitaxeBIRDS @ 11d188d and bitaxeBonanza @ 51b31ad public KiCad schematics (net names as drawn; published designs — BIRDS untested prototype, Bonanza not known built); BIRDS 0.70 V/ASIC (2.8 V / 4, its README), Bonanza nominal 0.71 V/ASIC from Integration Guide; BIRDS nodes shown as sheet label · local label; failure notes inferred |
| `uart/uart-9bit-character-frame.svg` | #13 | UART Physical Layer |
| `uart/tdm-frame-and-result-path.svg` | #13 | UART TDM / Result Aggregation / TX `0x0A` + public OSS packing; **opaque slot**; four labeled gaps |
| `process/job-to-result-path.svg` | #17 | Integration Glance + Mining Programming Model + UART job/result/TDM; TDM opaque; devices/HB = gap |
| `docs/lab-charts/rds-*-chart-placeholder.svg` | #18 | Empty frames + schema only — **needs measured RDS data**. Kept out of the published `drawings/` tree until real data exists; see [`lab-charts/`](lab-charts/README.md) |

Captions on each SVG describe the figure; they must not carry issue numbers, provenance audit notes or publishing-policy statements. The editable `.mmd` Mermaid sibling of a figure exists for redraws only; the SVG is the published figure and the single copy that readers see.
