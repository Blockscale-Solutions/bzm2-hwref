# BZM2 hardware implementations — ecosystem survey

A field guide to the known hardware built around the Intel BZM2 (Bonanza Mine 2) ASIC, for anyone
evaluating design approaches. The boards below span a **maturity and availability spectrum** — from
fully public, working OSHW to boards still in **private hardware development** ahead of their planned
open-source release. Each entry notes its status; **publicly available repositories are linked**, and
boards still in private development are marked as such. This survey is a companion to the
[Board Design Guide](bzm2-board-design-guide.md) (how to build one) and the
[Reference Implementation Roadmap](blockscale-reference-roadmap.md) (the software/firmware landscape).

> Intel provides its own evaluation and reference-design hardware for the Blockscale 1000 series; the
> open boards below draw on that lineage. This survey documents the **community and open-source**
> implementations. Maturity notes reflect each project's own status at the time of writing — check the
> repos for current state.

## Maturity & availability tiers

- **Public OSHW** — fully open and navigable today; usable as a working reference now.
- **Private — A0 hardware dev** — a real board in active bring-up whose repository is still private
  during development (see each entry for its release/availability status).
- **Maturity 0 (infancy)** — a repository exists but the BZM2 design has not yet been started/adapted;
  a candidate for a *future* reference, not usable as one today.

## Hashboards

| Board | ASICs / topology | Host / UART bridge | Maturity & availability | Notes |
|---|---|---|---|---|
| **[bitaxeBIRDS](https://github.com/bitaxeorg/bitaxeBIRDS)** (bitaxe community) | **4**, series-stacked | **Raspberry Pi Pico 2W** (RP2350, PIO 9-bit UART) | **Public OSHW** · working — the most mature open BZM2 hashboard | Pico 2W (RP2350) bridge module; series voltage-stack ladder; native 1.2 V oscillator |
| **[bitaxeBonanza](https://github.com/bitaxeorg/bitaxeBonanza)** (bitaxe community) | multi-ASIC, series-stacked | **ESP32-S3** | **Public OSHW** · work-in-progress (design issues documented) | Publicly documented the two classic BZM2 traps: a reversed UART level-shifter ([#3](https://github.com/bitaxeorg/bitaxeBonanza/issues/3)) and the ESP32's inability to do 9-bit UART natively ([#4](https://github.com/bitaxeorg/bitaxeBonanza/issues/4)). The board itself is a documented work-in-progress; the 9-bit UART is supplied by a **separate RP2040 bridge** ([bonanza-bridge-fw](https://github.com/bitaxeorg/bonanza-bridge-fw)), not a chip on this board — invaluable lessons either way |
| **Satoshi Starter** (Reckless Systems) | **1** | **XR21V1414** — hardware native-9-bit USB-UART bridge | **Private — A0 hardware dev** (rev1 bring-up); full OSHW release planned, available by request | Single-ASIC student/STEM kit; USB-C PD + barrel input; hardware-bridge path (no MCU firmware for the UART). Repository private during development. |
| **HashBed** | **16**, series-stacked "heatbed tile" | **RP2040** (PIO) | **Private during development** — A0 hardware dev (in progress) | Novel 3D-printer-heatbed form factor; per-bit level translation, PMBus controller-based core rail, native 1.2 V oscillator |
| **[EmberOne01](https://github.com/256foundation/emberone01-pcb)** (256 Foundation) | multi-ASIC, series-stacked (inherited BM1362 layout) | *(not yet BZM2-adapted)* | **Maturity 0 (infancy)** — public repo, BZM2 design not yet started | The intended BZM2 variant of the EmberOne. Its schematic today is still the BM1362 EmberOne design with **no BZM2-specific changes yet**, so it's a candidate for a *future* reference — not usable as one now. |

## ASIC family notes

- **Voltage stacking is the axis that separates these boards.** Single-ASIC designs (Satoshi Starter)
  share one ground and one core rail; multi-ASIC boards (bitaxeBIRDS 4, HashBed 16) put ASICs in a series
  stack with per-domain grounds, which drives the level-translation, clock-chaining, and per-domain
  rail complexity. A firmware/driver that supports the family must be topology-agnostic across these.
- **The 9-bit UART is the recurring gate.** Every board's controller choice is really a choice about how
  to speak the ASIC's 9-bit multidrop UART: a hardware bridge with a native 9-bit mode, or an MCU whose
  UART/PIO can do 9-bit (RP2040/RP2350), or an FPGA. General MCUs that only offer a parity bit do not
  work (publicly demonstrated). See the [UART Protocol Reference](blockscale-uart-protocol-reference.md).
- **1.2 V IO domain** dominates the interface design on all of them — see the
  [Board Design Guide](bzm2-board-design-guide.md).

## Firmware

| Project | Role | Notes |
|---|---|---|
| **[bonanza-bridge-fw](https://github.com/bitaxeorg/bonanza-bridge-fw)** (bitaxe) | RP2040 USB↔BZM2 bridge firmware | Rust; implements the 9-bit multidrop UART on the RP2040 PIO; the reference for the MCU-bridge approach |
| **[Mujina](https://github.com/256foundation/mujina)** (256 Foundation) | Open miner firmware | Has a native BZM2 driver (protocol, board, calibration, diagnostics) — see [PR #71](https://github.com/256foundation/mujina/pull/71); talks to the boards above over the 9-bit UART |

## Adjacent / related (not BZM2 hashboards)

- **[libreboard](https://github.com/256foundation/libreboard)** (256 Foundation): a CM5-based control/host board — chip-agnostic host, not a hashboard.
- **[bonanzaDisplay](https://github.com/bitaxeorg/bonanzaDisplay)** (bitaxe): an RP2350 + OLED telemetry display add-on.

## Why this matters for a new design

The open ecosystem has already paid for several first-run lessons in copper — the reversed shifter, the
9-bit-capable controller, the 1.2 V clock, the digitally-controlled core rail, series-stack grounding.
The [Board Design Guide](bzm2-board-design-guide.md) distills the *patterns*; this survey shows *who
proved what*, so a new board can adopt the working approaches and skip the documented traps. Note the
availability tiers above: the fully public boards (bitaxeBIRDS, bitaxeBonanza) can be inspected directly
today, while others are still in private development ahead of their OSHW release.
