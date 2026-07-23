# bzm2-hwref
Hardware Reference Documentation for the Bonanza Mine 2 ASIC (Intel® Blockscale™ 1000 series, "BZM2").

## Documentation

**Hardware reference (start here):**
- [ASIC Integration Guide](references/blockscale-asic-integration-guide.md) — architecture,
  rails and voltage stacking, electrical quick reference, clocking, bring-up, telemetry,
  calibration methodology, validation checklist
- [UART and TDM Protocol Reference](references/blockscale-uart-protocol-reference.md) —
  physical layer (fixed 9-bit multidrop framing, host bridge selection), opcodes, job
  programming, TDM, sensors
- [Pinout and Ball Map Reference](references/bzm2-pinout-reference.md) — all 60 pads:
  rails with pin counts, clocks, the PINSEL-muxed UART/reset/trip group, straps, JTAG
  ([machine-readable CSV](references/bzm2-ballmap.csv))
- [Reference Implementation Roadmap](references/blockscale-reference-roadmap.md) — the
  reference software/firmware landscape for the BZM2 and how the pieces relate
- [Board Design Guide](references/bzm2-board-design-guide.md) — effective design patterns
  and common pitfalls for building a working BZM2 board (level translation, clocking,
  VCORE control, power/protection, sequencing, 9-bit UART, bring-up checklist), synthesized
  from the open BZM2 ecosystem and general practice
- [Reference Design Guidance](references/bzm2-reference-design-guidance.md) — a parts-and-approaches
  catalog: specific off-the-shelf, publicly-datasheeted components for each function (level
  translators, 9-bit UART bridges, 1.2 V clock, digital VCORE control, sense/telemetry, input
  protection, supervision, thermal/TRIP interlock), with trade-offs and a "when to pick it" — the
  parts companion to the Board Design Guide
- [Hardware Implementations Survey](references/bzm2-hardware-implementations.md) — the known
  open-source BZM2 boards and firmware (Satoshi Starter, bitaxeBIRDS, bitaxeBonanza, HashBed,
  bonanza-bridge-fw, Mujina), their topologies, controller/bridge choices, and maturity

**Product collateral:**
- [Product Brief](Product%20Brief%20v012623.pdf)

**Firmware port notes:** driver-specific engineering notes (port architecture, tuning
planner, opcode grounding) live in the firmware tree with the code they describe —
[256foundation/mujina#71](https://github.com/256foundation/mujina/pull/71). This repository
is the canonical home for hardware reference material; firmware trees link here.

## License
This documentation is licensed under [CC-BY-SA-4.0](LICENSE)
(Creative Commons Attribution-ShareAlike 4.0 International).
