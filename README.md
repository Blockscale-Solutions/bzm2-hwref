# bzm2-hwref
Hardware Reference Documentation for the Bonanza Mine 2 ASIC (Intel® Blockscale™ 1000 series, "BZM2").

**Site:** [https://blockscale-solutions.github.io/bzm2-hwref/](https://blockscale-solutions.github.io/bzm2-hwref/) — task-oriented hub (Bring-up · Board design · UART/TDM · Pinout & rails · Architecture · Implementations · Roadmap). Contributors: see [CONTRIBUTING.md](CONTRIBUTING.md).

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
- [Hardware Reference Roadmap](references/blockscale-reference-roadmap.md) — what the
  reference covers for integrators today and what it plans to cover next
- [Board Design Guide](references/bzm2-board-design-guide.md) — effective design patterns
  and common pitfalls for building a working BZM2 board (level translation, clocking,
  VCORE control, power/protection, sequencing, 9-bit UART, bring-up checklist), synthesized
  from the open BZM2 ecosystem and general practice
- [Reference Design Guidance](references/bzm2-reference-design-guidance.md) — a parts-and-approaches
  catalog: specific off-the-shelf, publicly-datasheeted components for each function (level
  translators, 9-bit UART bridges, 1.2 V clock, digital VCORE control, sense/telemetry, input
  protection, supervision, thermal/TRIP interlock), with trade-offs and a "when to pick it" — the
  parts companion to the Board Design Guide
- [Voltage-Stack Topology Examples](references/bzm2-voltage-stack-examples.md) — how boards stack
  BZM2s in series and parallel, led by the RDS (25 levels × 4 in parallel on a rail shared by three
  boards), with bitaxeBIRDS, bitaxeBonanza and HashBed as comparisons: levels, parallel count, rail vs
  per-ASIC voltage, balancing, and inferred failure behaviour
- [Hardware Implementations Survey](references/bzm2-hardware-implementations.md) — the known
  BZM2 boards and firmware (bitaxeBIRDS, bitaxeBonanza, Satoshi Starter, HashBed, EmberOne01,
  bonanza-bridge-fw, Mujina) across a maturity/availability spectrum — from fully public OSHW to
  boards still in private hardware development — with topologies, controller/bridge choices, and status

- [RDS Reference Measurements](references/rds-measured-reference.md) — observed data from one RDS
  unit, kept apart from the specification: which software board is which hashboard, heat by board
  across the stock profiles, rail and level-deviation readings, the power feeds, live clock changes
  and the error ratio at a fixed start

**Product collateral:**
- [Product Brief](Product%20Brief%20v012623.pdf)

**Firmware:** driver-specific engineering notes live in the firmware tree with the code they
describe. For the current state of BZM2 support in the [Mujina](https://github.com/256foundation/mujina)
miner firmware, see the [Hardware Implementations Survey](references/bzm2-hardware-implementations.md).
This repository holds the hardware reference material; firmware trees link here.

## License
This documentation is licensed under [CC-BY-SA-4.0](LICENSE)
(Creative Commons Attribution-ShareAlike 4.0 International).

## Claims

Factual claims carry an opaque id such as `[BZM2-ENG-002]`, listed in
[`CLAIMS.md`](CLAIMS.md) with the kind of evidence behind each one. See
[CONTRIBUTING.md](CONTRIBUTING.md) for how claims are tracked.
