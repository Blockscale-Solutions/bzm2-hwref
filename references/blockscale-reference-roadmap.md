# Blockscale / BZM2 Hardware Reference Roadmap

## Purpose

This reference is written for people designing boards and host software around the BZM2 ASIC. This page lists what
the reference covers today and what it plans to cover next, so an integrator can see where the documentation is
complete and where it is still thin. Planned items are intentions, not commitments, and carry no dates.

## Scope

In scope:

- generic ASIC bring-up and chain discovery
- rail, reset and voltage-stack design, including domain-aware power and tuning control
- the 9-bit UART and TDM interface
- board design patterns, pitfalls and parts choices
- diagnostics a host or board should expose
- observed data from reference hardware, kept apart from the specification

Out of scope:

- reproduction of vendor reference boards
- carrier-specific MCU protocols
- decoding of the first-generation four-byte `DTS_VS` sensor payload (the reference documents the eight-byte payload)
- JTAG usage beyond what concrete protocol evidence supports

## What the reference covers today

| Topic | Where |
|---|---|
| ASIC overview, rails and voltage stacking, clocking, bring-up sequence, telemetry and protection, calibration method, validation checklist | [Integration Guide](blockscale-asic-integration-guide.md) |
| 9-bit multidrop framing, opcodes, job programming, TDM, sensors | [UART and TDM Protocol Reference](blockscale-uart-protocol-reference.md) |
| All 60 pads, straps, PINSEL muxing, machine-readable ball map | [Pinout and Ball Map](bzm2-pinout-reference.md) |
| Patterns and pitfalls: level translation, clocking, VCORE, sequencing, 9-bit UART, checklist | [Board Design Guide](bzm2-board-design-guide.md) |
| Parts and approaches for translators, UART bridges, clock, VCORE control, protection, thermal | [Reference Design Guidance](bzm2-reference-design-guidance.md) |
| Worked voltage-stack topologies and their failure reasoning | [Voltage-Stack Topology Examples](bzm2-voltage-stack-examples.md) |
| Known boards and firmware, by maturity | [Hardware Implementations Survey](bzm2-hardware-implementations.md) |
| Observed data from one RDS unit | [RDS Reference Measurements](rds-measured-reference.md) |

## Host capabilities the reference describes

Ordered by dependency: each capability builds on the ones before it.

| # | Capability | What an integrator needs from it | Covered in | Planned |
|---|---|---|---|---|
| 1 | Discoverable bring-up | Find the chain from software with no fixed ASIC count: enumerate from default ID `0xFA`, assign IDs, verify each with `NOOP`. | Integration Guide (enumeration model), UART Reference (enumeration rule) | — |
| 2 | Rail and reset control | Sequence control rails, reference clock, reset and stack voltage; return to a safe state on shutdown; read rail telemetry. | Integration Guide (power-up sequence, protection), Board Design Guide | — |
| 3 | Domain voltage application | Apply coarse per-domain voltages before the clock ramp, verify them with rail telemetry and the ASIC's `DTS_VS` readings, and keep the operating point for restart reuse. | Integration Guide (voltage sensing, calibration) | A step-by-step domain-voltage procedure |
| 4 | Topology and defect discovery | Do not assume the default engine map is the real one; detect missing or disabled engines per ASIC. | Integration Guide (failure modes) | How a host probes engine presence |
| 5 | Closed-loop calibration and retune | Measure pass rate, throughput, per-PLL behaviour and per-domain power; retune on throughput regression, thermal drift or persistent voltage imbalance; revalidate saved operating points. | Integration Guide (calibration methodology) | Behaviour below 800 MHz; per-board threshold guidance |
| 6 | Diagnostics | Expose `NOOP`, loopback, register read/write, a clock report and a chain summary without raw serial tooling. | UART Reference (synchronous diagnostics, loopback) | — |
| 7 | JTAG | Only where enough packet-level evidence exists to do it correctly. | Pinout Reference (pads) | Held until the evidence exists |

## Planned coverage

- **Thermal and protection detail:** the offset between the on-die sensor reading and junction temperature, and
  temperature thresholds an integrator can adopt.
- **Clocking:** PLL lock and error behaviour below 800 MHz.
- **Opcode coverage:** the `BLOCK_HDR` opcode (`0x5`), whose direction, payload and response are not yet documented.
- **RDS observations:** the physical slot for each software board index.
- **Charts:** measured charts for the RDS observations, published once the long characterization run is complete.
