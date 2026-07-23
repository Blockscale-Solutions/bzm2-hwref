# BZM2 hardware implementations — open ecosystem survey

A field guide to the known hardware built around the Intel BZM2 (Bonanza Mine 2) ASIC, for anyone
evaluating design approaches. Every board and firmware below is **open-source and public**; each entry
links to its repository. This survey captures *what exists, how it's built, and how mature it is* — a
companion to the [Board Design Guide](bzm2-board-design-guide.md) (how to build one) and the
[Reference Implementation Roadmap](blockscale-reference-roadmap.md) (the software/firmware landscape).

> Intel provides its own evaluation and reference-design hardware for the Blockscale 1000 series; the
> open boards below draw on that lineage. This survey documents the **public open-source**
> implementations. Maturity notes reflect each project's own public status at the time of writing —
> check the repos for current state.

## Hashboards

| Board | ASICs / topology | Host / UART bridge | Maturity (per project) | Notes |
|---|---|---|---|---|
| **[Satoshi Starter](https://github.com/Blockscale-Solutions/SatoshiStarter)** (Reckless Systems) | **1** | **XR21V1414** — hardware native-9-bit USB-UART bridge | rev1 in design audit / bring-up | Single-ASIC student/STEM kit; USB-C PD + barrel input; hardware-bridge path (no MCU firmware for the UART) |
| **[bitaxeBIRDS](https://github.com/bitaxeorg/bitaxeBIRDS)** (bitaxe community) | **4**, series-stacked | **RP2040** (PIO 9-bit UART) | working design | The most mature open BZM2 hashboard; RP2040 "pico" bridge; series voltage-stack ladder |
| **[bitaxeBonanza](https://github.com/bitaxeorg/bitaxeBonanza)** (bitaxe community) | multi-ASIC, series-stacked | **ESP32-S3** | documented design issues (see its README/issues) | Publicly documented the two classic BZM2 traps: a reversed UART level-shifter ([#3](https://github.com/bitaxeorg/bitaxeBonanza/issues/3)) and that the ESP32 can't do 9-bit UART natively ([#4](https://github.com/bitaxeorg/bitaxeBonanza/issues/4)) — invaluable lessons even where the board itself is a work in progress |
| **[HashBed](https://github.com/aadhi1014/hashbed)** | **16**, series-stacked "heatbed tile" | dual **RP2040** (PIO) | incomplete / in progress | Novel 3D-printer-heatbed form factor; SN74AVC4T774 translators, PMBus-class core control, native 1.2 V oscillator |

## ASIC family notes

- **Voltage stacking is the axis that separates these boards.** Single-ASIC designs (Satoshi Starter)
  share one ground and one core rail; multi-ASIC boards (BIRDS 4, HashBed 16) put ASICs in a series
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

- **[EmberOne00](https://github.com/256foundation/emberone00-pcb) / [EmberOne01](https://github.com/256foundation/emberone01-pcb)** (256 Foundation): 12-ASIC open hashboards — **but built on the Bitmain BM1362, not the BZM2.** Their *system* patterns (series stacking, thermal, power) are instructive, but the per-chip electricals (rails, UART, IO domain) do **not** transfer to the BZM2. A BZM2 EmberOne variant is a separate effort.
- **[libreboard](https://github.com/256foundation/libreboard)** (256 Foundation): a CM5-based control/host board — chip-agnostic host, not a hashboard.
- **[bonanzaDisplay](https://github.com/bitaxeorg/bonanzaDisplay)** (bitaxe): an RP2350 + OLED telemetry display add-on.

## Why this matters for a new design

The open ecosystem has already paid for several first-run lessons in copper — the reversed shifter, the
9-bit-capable controller, the 1.2 V clock, the digitally-controlled core rail, series-stack grounding.
The [Board Design Guide](bzm2-board-design-guide.md) distills the *patterns*; this survey shows *who
proved what*, so a new board can adopt the working approaches and skip the documented traps.
