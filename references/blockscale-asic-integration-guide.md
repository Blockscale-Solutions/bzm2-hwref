# Blockscale / BZM2 ASIC Hardware Integration Guide

## Purpose

This document consolidates ASIC-level behavior needed to design a custom
hardware solution around the Blockscale / BZM2 mining ASIC. It focuses on
generic implementation requirements:

- power architecture
- sequencing
- clocking
- UART transport
- multi-ASIC chaining
- telemetry
- protection
- tuning and calibration

It deliberately avoids copying vendor reference-board implementation details.
Those reference systems are useful examples, but they are not required for a
working design.

## Scope

This guide is for hardware developers building:

- a single-ASIC board
- a small multi-ASIC board with one or a few voltage domains
- a larger multi-ASIC platform with multiple voltage domains

The core constraint does not change with board size: every ASIC contains an
internal dual-stack engine arrangement and expects the host system to sequence,
clock, load, and protect it correctly.

## Terms Used In This Reference

| term | meaning |
| --- | --- |
| BZM2 | the Intel Blockscale 1000-series bitcoin mining ASIC (Bonanza Mine 2) |
| RDS | the vendor's reference mining system for the BZM2: three hashboards of 100 ASICs on one shared supply rail. The observed data in this reference come from one RDS unit |
| stock firmware | the vendor's own host software as shipped on the RDS, including its mining daemon |
| Mujina | open-source miner firmware; its BZM2 support is described under [Relationship To The Mujina Reference Firmware](#relationship-to-the-mujina-reference-firmware) |
| bottom stack, top stack | the two internal voltage domains of one ASIC, in series: bottom `0` to `~0.355 V`, top `~0.355` to `~0.71 V` |
| engine position (tile) | the unit an engine identifier addresses: `236` per ASIC, each holding four engines |
| TCE | the vendor's name for one hashing engine; the four engines at a position are its four lanes |
| enhanced mode | the default engine programming mode: four job writes per position, one per engine |
| notch | the vendor's name for the ASIC-level controller block; it holds the ASIC result FIFO, and its local registers are reached with engine identifier `0xFFF` |
| PLL, DLL | phase-locked loop (two per ASIC, one per stack) and delay-locked loop |
| DTS, VS | the on-die digital temperature sensor and voltage sensor; `DTS_VS` is the opcode and packet that carry both |
| TDM | the time-division multiplexed return stream: each ASIC transmits in the time slot that matches its ID |
| TRIP | the ASIC's over-temperature / over-voltage output, once the sensors are armed |
| FCLGA | flip-chip land grid array, the package type |
| PDN | power distribution network |

## ASIC At A Glance

ASIC-level properties:

- `236` addressable engine positions per ASIC `[BZM2-ENG-003]` - used by public
  open-source firmware and corroborated by bench capture
- `4` engines per position `[BZM2-ENG-005]` - vendor-stated; not independently
  measured
- `944` total engines per ASIC - the product of the two figures above
- `2` primary PLL domains, corresponding to the bottom and top engine stacks
- on-die digital temperature sensing
- on-die three-channel voltage sensing
- UART as the primary host control and mining transport
- unicast, multicast, and broadcast job/register distribution
- TDM streaming for results, register responses, `NOOP`, and sensor data

Throughput per ASIC can be estimated as:

```text
Throughput (GH/s) = 236 * 4 * PLL_Frequency / 3 * Pass_Rate
```

Where:

- `PLL_Frequency` is in GHz
- `Pass_Rate` is `0.0` to `1.0`

Example:

```text
1.2 GHz * (236 * 4 / 3) * 1.0 = 377.6 gigahash per second
```

The example is arithmetic on the formula, not a measured rate. The formula is
useful for sizing cooling, PSU headroom, calibration targets, and per-domain
operating points.

## Recommended System Partitioning

The ASIC does not require a specific vendor platform. It does require that the
overall system provide the following functions:

- stable control-side power
- stable stack-side power
- reference clock generation
- reset and trip handling
- UART master
- telemetry collection and protection logic
- work generation and result collection

The host connects to the ASIC chain through the UART master (control, work and results), the power path
(regulators, often over PMBus) and the cooling control (fans or pumps). The chain reports back through its
sensor stream (`DTS_VS`) and its `TRIP` output.

The exact split is your design choice:

- a Linux SoC can own all logic directly
- an MCU can own power sequencing while a host CPU owns mining
- an FPGA can assist with fanout, timing, or board aggregation

The ASIC-facing requirements remain the same.

## Package, IO, And Mechanical Constraints

Package and mechanical envelope:

- package size: `7.5 x 7 mm`
- package type: exposed-die molded `FCLGA`
- `60` lands: `40` peripheral plus a `20`-land inner field (see the
  [Pinout and Ball Map Reference](bzm2-pinout-reference.md))
- junction temperature limits: see the
  [Electrical Quick Reference](#electrical-quick-reference-per-asic)

Design implications:

- provide strong top-side thermal extraction
- assume continuous high leakage once stack voltage is present
- do not depend on reset state to keep thermal rise negligible
- plan for heatsink and forced airflow, or an equivalent thermal solution

Even a single-ASIC design should be treated as thermally active immediately
after hash rails are applied.

## Core Rails And Voltage Architecture

The ASIC is built around internal voltage stacking. The documents describe two
engine-stack ranges:

- bottom stack: approximately `0.0 V` to `0.355 V`
- top stack: approximately `0.355 V` to `0.71 V`

Additional named rails described in the vendor material:

- GPIO / control IO: `1.2 V`
- `VDD_HASH`: nominal `0.71 V`
- `VDD_P75`: backup rail if the on-chip LDO path is unavailable

### Rail and stack topology (single ASIC)

![BZM2 single-ASIC rail and stack topology](../drawings/rails/single-asic-rail-stack.svg)

Single-ASIC rail topology, using the figures in the Electrical Quick Reference below and the pinout Rails table. For multi-ASIC series stacking, see [Voltage-Stack Topology Examples](bzm2-voltage-stack-examples.md): the RDS (25 levels × 4 in parallel) and the published bitaxeBIRDS (4s1p) and bitaxeBonanza (4s2p) designs.

### Why voltage stacking matters

Voltage stacking is central to efficiency, but it also creates the main
hardware risk:

- the absolute stack voltages must stay inside safe limits
- the differential between the stacks must stay controlled
- bad sequencing or poor balancing can create overvoltage or thermal runaway

The ASIC includes internal voltage sensing specifically because the host must
monitor and react to stack imbalance.

### Voltage sensor channels

The internal voltage sensor reports three channels. Getting their scales wrong
produces bounds that cannot fire, so read the healthy-reading column before
setting any limit:

| channel | what it measures | healthy reading | can it trip the ASIC? |
| --- | --- | --- | --- |
| `ch0` | differential across the **bottom** stack | `~355 mV` | **yes** |
| `ch1` | differential across the **top** stack | `~355 mV` | **yes** |
| `ch2` | top-stack return against bottom-stack supply - the **midpoint error** | small, near zero at idle, grows with load | **no** |

Both stack channels read the differential across their **own** stack, not an
absolute node voltage, so both sit near `355 mV` and are directly comparable
to each other. Public reference firmware programs the
**same** shutdown code into both channels and bounds their difference with a
single spread limit - neither would be coherent if the two were on different
scales.

`ch2` is **not** a third rail and is **not** the `~355 mV` step between the
stacks. It is also **not** `ch1 − ch0`. It is the gap between the bottom
domain's top and the top domain's bottom: near zero on a healthy part at light
load, but it grows with load current (it behaves like a resistive drop across
the internal midpoint path). Bound it by **absolute magnitude** with a
**current-scaled** limit - a fixed near-zero alarm false-trips healthy parts at
full load - not by proximity to `355 mV`. The per-ASIC span is
`ch0 + ch2 + ch1`. `[BZM2-VS-001]`

**Only `ch0` and `ch1` feed the ASIC's own voltage shutdown.** The
voltage-sensor control register carries a threshold field for each of those
two and none for `ch2`, so the part takes no action on a midpoint fault. If
your design needs to survive one, the response has to be on the board or in
the host - nothing in the ASIC is watching.

Treat all three as first-class runtime safety inputs, not debug-only data -
but do not assume the part acts on all three.

## Electrical Quick Reference (Per ASIC)

Design-point numbers a board designer needs up front. The two operating points below match rows in
[bitaxeorg/bitaxeBIRDS `doc/specs.md`](https://github.com/bitaxeorg/bitaxeBIRDS/blob/main/doc/specs.md),
a published 25-point sweep on real hardware. Characterize on your own design
before committing limits.

| Parameter | Value | Notes |
| --- | --- | --- |
| `VDD_HASH` (stack rail) | `0.71 V` nominal | tunable window roughly `0.6` to `0.81 V` |
| Internal stack split | `0 - 0.355 V` / `0.355 - 0.71 V` | bottom / top engine stacks |
| Control / GPIO IO rail (`VDDIO`) | `1.2 V` nominal (`1.0 - 1.3 V` range), `1.3 V` abs max | UART, reset, trip signaling; per-pin input/output levels below |
| Stack current, stock operating point | `~14 A` | roughly `10 W` core power; a public sweep gives `13.6 A / 9.4 W` at `1.05 GHz` and `14.2 A / 9.9 W` at `1.10 GHz` |
| Stack current, maximum tuned point | `~27 A` | roughly `22 W`; plan copper for `~30 A` headroom. A public sweep's top row is `27.1 A / 21.95 W` at `0.810 V, 1.85 GHz` |
| Efficiency | best at a low clock, worsening as the clock rises | A public sweep puts the best efficiency near `0.60-0.75 GHz` and the worst at the maximum tuned point. Chasing best efficiency costs hashrate, and a single efficiency number is meaningless without the clock it was measured at |
| Reference clock | up to `50 MHz` on `REFCLKIN` | `50 MHz` is the standard choice |
| UART baud | see [Baud and signaling](blockscale-uart-protocol-reference.md#baud-and-signaling) | |
| Junction temperature | `50 - 85 C` operating, `115 C` abs max `[BZM2-THM-001]` | a rating of the silicon, not the on-die sensor reading (see [Temperature thresholds](#temperature-thresholds)); plan top-side thermal extraction |

PDN guidance that follows directly from those numbers:

- the `VDD_HASH` path is a plane-and-via-farm problem, not a trace problem -
  budget wide pours and dozens of vias between layers, sized per IPC-2152
- decoupling must live close to the package; if a heatsink owns the top side,
  put the capacitor bank on the bottom side under the FCLGA land field
- at `0.71 V`, tens of millivolts of IR drop are several percent of the rail -
  measure remote-sense placement against your layout, not a reference design

### IO DC thresholds (the 1.2 V domain)

The control, UART, reset, trip, and reference-clock pads sit on the `VDDIO`
rail. Any signal driven into them must land inside the input window below;
exceeding the input-high limit overstresses the pad. Levels are given against
`VDDIO`, with the right column evaluated at the `1.2 V` nominal rail.
Synthesized from the vendor collateral - characterize before committing limits.

| Parameter | Spec | At `VDDIO = 1.2 V` |
| --- | --- | --- |
| `VDDIO` rail | `1.0` min / `1.2` nominal / `1.3 V` **abs max** | `1.2 V` |
| Input high `VIH` | min `0.65 x VDDIO`, **max `VDDIO + 0.3 V`** | `0.78 V` min, `1.5 V` max |
| Input low `VIL` | max `0.35 x VDDIO` | `0.42 V` max |
| Input threshold | `~0.6 V` | `0.6 V` |
| Output high `VOH` | min `0.75 x VDDIO` | `0.90 V` |
| Output low `VOL` | max `0.25 x VDDIO` | `0.30 V` |
| Peak overshoot (transient) | `VDDIO + 0.3 V` | `1.5 V` |
| Peak undershoot (transient) | `~0.3 V` below ground | `~ -0.3 V` |
| Pull-up / pull-down | `~20k` / `~24k` typical | strong pull-up `~3.4k` |

The absolute ceiling on any IO pin - static input-high or transient overshoot -
is **`VDDIO + 0.3 V`, i.e. `1.5 V`** at a `1.2 V` rail. Two direct consequences
for a board:

- **A `3.3 V` source cannot drive these pads through a simple resistive
  divider.** A `3.3 V` clock halved to `~1.65 V`, or a `3.3 V` UART through a
  `5.1k/3.3k` divider to `~1.3 V`, both sit at or above the input-high limit -
  overstress, not merely marginal. Use a real level translator, an
  AC-couple-and-bias network, or a `1.2 V`-domain source instead.
- **`REFCLKIN` specifically** wants a clean `1.2 V`-referenced swing (roughly
  ground to `VDDIO`), not a divided-down `3.3 V` oscillator - and watch source
  loading if you ever do use passive networks.

## Clocking

### External reference clock

The ASIC takes its reference clock on `REFCLKIN`:

- `REFCLKIN` is the ASIC reference clock input, specified up to `50 MHz`
- `50 MHz` is the standard choice - the UART baud range and the documented
  bring-up flow are both defined against a `50 MHz` reference

The ASIC also exposes `REFCLKOUT1` and `REFCLKOUT2`, primarily as
debug-oriented outputs.

### Internal PLLs

The ASIC uses two PLLs to feed the two internal engine stacks:

- `PLL0`: bottom stack
- `PLL1`: top stack

Bring-up implications:

- both PLLs are disabled by default
- software must enable them explicitly
- software must wait for lock before releasing dependent logic

When both divider classes are changed, the documented programming rule is:

1. write `FBDIV`
2. write `POSTDIV`

Do not reverse that order during live clock changes.

### Live clock changes on a hashing chain

Observations from live PLL moves on an RDS chain are in
[RDS reference measurements](rds-measured-reference.md#live-clock-changes-on-a-hashing-chain). What a host should take
from them:

- **A live move of the feedback divider alone re-locks.** Read lock back after each set.
- **Budget about one second of host time per set.**
- **A frame with the nonce-valid bit clear is not a result.** While PLL sets run on a chain, every ASIC on it can return
  result frames with that bit clear. The reference firmware reads it as bit 3 (`0x08`) of the result status byte. Count
  such frames on their own. Do not count them as valid results or as wrong ones, and keep them out of any error ratio.
- **Do not measure a chain while its clocks are being moved, or just after.** The Mujina BZM2 reference firmware discards
  any measurement interval that starts within a 45 s quiet period after the latest PLL set on the chain. Treat that as
  a margin to be set per board.
- **Do not block work dispatch for a run of PLL sets.** Each set holds whatever path it is issued from. If that is
  the chain's only dispatch path, the whole chain idles for the whole sequence.

Not yet established: whether these parts lock and run cleanly below 800 MHz in a hashing system.

### DLL health

The stock firmware also checks DLL state using its `coarsecon` and `fincon`
status fields. That is not strictly required to boot the ASIC, but it is useful for:

- manufacturing validation
- marginal-clock debug
- SI validation at new board layouts or cable lengths

If you are building a custom carrier or long-chain design, budget time for DLL
health checks during validation.

## UART And Chain Topology

UART is the primary host interface for:

- enumeration
- register control
- job dispatch
- result retrieval
- TDM streaming
- sensor retrieval

### Practical UART assumptions

- the link is **fixed 9-bit multidrop framing** - this is the single most
  important host-side constraint; see the physical-layer section of the
  [UART and TDM Reference](blockscale-uart-protocol-reference.md) for the
  framing details and host bridge selection guidance
- the supported baud range and the bring-up rate are in
  [Baud and signaling](blockscale-uart-protocol-reference.md#baud-and-signaling)
- the internal `notch` controller block runs from the `50 MHz` clock during
  bring-up

The UART-related pads are `1.2 V` IO. Treat this as a real electrical
requirement when selecting the host UART PHY or level-shifting scheme.

### Chain orientation and pin muxing

The vendor material describes a `PINSEL`-based pin muxing arrangement where the
same physical pins can serve as:

- `RX_IN` / `TX_OUT`
- `RESET_IN` / `RESET_OUT`
- `TRIP_IN` / `TRIP_OUT`

This is what enables daisy-chain style system layouts. For a generic design,
the important point is:

- your schematic must preserve a consistent direction through the chain
- reset and trip propagation need the same level of attention as RX/TX routing

### ASIC enumeration model

The documented enumeration flow is:

1. all ASICs start with default `ASIC_ID = 0xFA`
2. the host addresses `0xFA`
3. the first visible ASIC responds
4. the host writes a unique `ASIC_ID`
5. writing the ID also unlocks `RX_OUT`
6. the next ASIC becomes reachable
7. repeat until the chain is assigned

`NOOP` is the simplest chain-liveness check. Its reply, and the spelling trap
in it, are in the protocol reference under [`NOOP`](blockscale-uart-protocol-reference.md#noop).

### Broadcast and multicast

The ASIC supports:

- unicast to one engine in one ASIC
- broadcast to the same engine position across all ASICs
- multicast to a row group

That capability is what makes large chains viable over UART. Use it for:

- initial register programming
- dummy-job deployment
- broad frequency ramps
- row-wise validation

Reserve unicast for:

- ASIC ID assignment
- per-ASIC final tuning
- fault isolation
- result ownership and targeted debug

## Power-Up And Bring-Up Sequence

The sequence below is the part of the vendor's reference flow that applies to any
board:

![BZM2 power-up / bring-up flowchart](../drawings/bring-up/power-up-sequence.svg)

The flowchart combines this guide's bring-up sequence with the hardware fail-safes in the [Board Design Guide](bzm2-board-design-guide.md) (§7, §9).

### Arm the on-die protection before raising the stack, and confirm it took

**Arm-protection gate.** Do not raise the stack voltage until thermal and voltage protection are confirmed enabled (`thermal_enabled` and `voltage_enabled` both reported by the device). Otherwise stop; do not raise the stack.

Out of reset both sensors are powered down, so the trip output cannot assert at
any temperature or voltage. A stack ramp before arming runs with no on-die
protection at exactly the point where voltage and frequency are being raised.

The step does not need the stack: **VDDIO is a separate rail**, so an ASIC is
reachable over UART and its sensors are armable while the core stack does not
yet exist. This holds on any topology that brings the control rails up before the stack, as the sequence above does.

**Confirm from the device's own sensor stream, not by reading the registers
back.** A readback travels the same synchronous path that wrote them, so it
proves the path works rather than that the arming took. The part reports
`thermal_enabled` and `voltage_enabled` asynchronously and unprompted; that is a
witness. On a chain, record **which** device confirmed - a broadcast write is
acknowledged by the bus, not by every part on it.

**Anything that reads die temperature before this point gets no reading.** A
calibration or tuning pass that silently falls back to an ambient or board-level
proxy will choose operating points against the wrong temperature, and will do so
without erroring.

### Practical bring-up rules

- start from a conservative voltage
- start from a conservative clock, typically much lower than final operating
  point
- do not ramp voltage or frequency without sensor feedback
- do not leave engines idle during stack-balancing phases if your control
  strategy depends on balanced load
- do not start full production mining until IDs, PLL lock, and basic telemetry
  are confirmed

### Dummy-job use is not optional in stacked systems

Vendor guidance treats dummy jobs as part of power balancing, not merely a debug
aid. In practice, dummy jobs help:

- keep engines drawing current
- maintain stack balance during ramp-up
- prevent some engines from sitting unloaded while others are active
- hold a repeatable thermal and electrical state during calibration

## Mining Programming Model

![BZM2 process walk — job → engines → result](../drawings/process/job-to-result-path.svg)

Job path: the host programs a job, 236 engine positions (4 engines each) execute it, results are aggregated, and the TDM stage returns them to the host. TDM is drawn as a single stage; the frame and slot layout are in the [UART and TDM Protocol Reference](blockscale-uart-protocol-reference.md). The number of ASICs per hashboard depends on the board design.

The programming contract lives in the protocol reference:

- [Enhanced-Mode Job Programming](blockscale-uart-protocol-reference.md#enhanced-mode-job-programming): register
  setup, the four-write sequence, and why only the fourth write may launch work
- [Job Control Semantics](blockscale-uart-protocol-reference.md#job-control-semantics): the `JobControl` values, and
  the cancel path that recovers from invalid or stale engine state
- [Partial, Incomplete, And Invalid Programming](blockscale-uart-protocol-reference.md#partial-incomplete-and-invalid-programming):
  what malformed sequences do. The ASIC does not sanitize them.


## Telemetry And Protection

### Temperature sensing

The ASIC exposes a digital temperature sensor, read through the `DTS_VS` packet. The conversion from raw code to
Celsius, with a worked example, is in the protocol reference under
[Sensor Conversion Equations](blockscale-uart-protocol-reference.md#sensor-conversion-equations).

### Temperature thresholds

Three different temperatures appear in the vendor material and they are not the same quantity. Keep them apart.

1. **Junction temperature**, a rating of the silicon: the operating range and absolute maximum are in the
   [Electrical Quick Reference](#electrical-quick-reference-per-asic). Vendor characterisation data adds that hash
   throughput falls off above `85 C`, and recommends keeping the junction between `55` and `85 C`. This is a rating,
   not a reading the software takes.
2. **The on-die sensor reading** (the thermal tune code above, converted to Celsius). This is what the host and the trip
   logic see. **No public or vendor source gives the offset between the sensor reading and the junction
   temperature**, so a junction rating must not be applied to a sensor reading as if they were one number.
3. **The sensor trip level** a host programs into the ASIC (the trip described under Protection behavior).

The vendor software specification states staged thresholds on the sensor reading, per mining strategy:

| strategy | warning (event recorded per ASIC) | software shutdown (per ASIC, system shut down) | hardware thermal trip |
|---|---|---|---|
| balanced | `85 C` | `95 C` | `105 C` |
| high performance 1 | `90 C` | `100 C` | `110 C` |
| high performance 2 | `95 C` | `105 C` | `115 C` |

The same specification marks a working temperature of under `85 C` and says the thresholds were still to be finalized. The
stock daemon's own compiled defaults differ below the highest strategy: a warning at `105 C`, a software shutdown at
`110 C` (acted on only after the reading stays at or above it for more than ten consecutive polls) and a chip trip of
`115 C`, with the trip adjustable up to `125 C`. Both agree on `115 C` for the chip trip, and a capture of the stock
firmware at power-on shows it programming `115 C`. Which table a given daemon build applies is not determined by these
sources.

On an RDS at the stock firmware's highest strategy, the hottest sensor reading stayed above that strategy's software
shutdown level for many minutes without a shutdown; the readings are in
[RDS reference measurements](rds-measured-reference.md#heat-by-board). No damage rating on the sensor reading is
available.

Open questions in this section: the sensor-to-junction offset, which threshold table the stock daemon applies per
strategy, and damage or wear data on the sensor reading.

### Voltage sensing

The three voltage channels and what each one means electrically are under
[Voltage sensor channels](#voltage-sensor-channels). The conversion from raw code to millivolts is in
[Sensor Conversion Equations](blockscale-uart-protocol-reference.md#sensor-conversion-equations); it gives an
uncalibrated voltage, so allow for the sensor's accuracy when setting a bound.

### Protection behavior

**Out of reset, the ASIC is not protecting itself.** Both sensors come up
powered down, no thresholds exist, and **the trip output cannot assert at any
temperature or voltage** until a host programs the sensor block. A board with
the trip pin correctly wired to its core-rail enable has **no** overtemperature
protection until that programming happens - while appearing, on the schematic,
to have a hardware interlock.

Arming is therefore a mandatory bring-up stage, not an optimisation. Public
reference firmware treats it exactly that way: it writes the sensor enables,
both trip thresholds and the confirmation counts, verifies them by readback,
and **gates the clock stage on that verification** - refusing to proceed if the
sensors were not confirmed.

Once armed, the ASIC can assert a trip output when thermal or voltage
thresholds are exceeded. A robust system should wire this into board-level
protection.

Recommended policy:

- use sensor data for continuous host-side supervision
- use the trip path for fast hardware or firmware response
- treat temperature and differential stack voltage as shutdown-class signals
- never rely on software polling alone for destructive fault containment

## Calibration Methodology

The calibration material is useful as methodology, but not as a fixed set of
numbers. The reusable sequence is:

1. characterize a single ASIC or a small golden sample
2. choose conservative initial voltage and frequency
3. reset all ASICs to the safe starting point
4. bring stack voltage to a safe operating region
5. use dummy jobs to keep the electrical state stable
6. raise frequency in steps, commonly `25 MHz` coarse steps
7. measure pass rate, throughput, temperature, current, and power
8. raise voltage only if throughput targets cannot be met within thermal and
   power limits
9. once the board-level operating region is found, fine-tune individual ASICs
   in smaller steps, for example `6.25 MHz`
10. persist the resulting operating point for restart reuse

### Start-frequency calibration

Error ratios at a uniform `800 MHz` start, measured on an RDS, are in
[RDS reference measurements](rds-measured-reference.md#error-ratio-at-a-fixed-start). They show a few high-error ASICs
on each board, boards that differ even without them, and a ratio that differs between runs of the same board. What to
take from this for a calibration design:

- Make the **ASIC** the unit that a start-frequency decision acts on. Keep the board's pooled figure as a record and a
  reference for that board, not as a gate.
- Expect a tail. A few ASICs per board will sit well above the rest. Park them low and keep them hashing rather than
  failing the board.
- Derive thresholds from several boards and several runs, and record which ones.
- Whether a high-error ASIC improves at a lower clock is not yet known.

### How far a pooled error ratio can be trusted

Repeats of one start-frequency search on one RDS board, with the pooled figure and the per-ASIC counts for each run, are
in [RDS reference measurements](rds-measured-reference.md#error-ratio-across-repeats-on-one-board). They show a pooled
board figure that lands on both sides of a fixed edge from one repeat to the next, and a high-error tail made of the
same ASICs every time. What to take from this for a calibration design:

- **Do not gate a board on one pooled reading near a fixed threshold.** A single pooled reading is a statement about
  that board at that time, not a property of the board; a repeat can flip the decision.
- **Judge each ASIC on its own first dwell at the start, and stop the board only when more than half of its ASICs are
  individually over the edge.** This is the median-ASIC rule: the median cannot be moved by fewer than half the ASICs,
  however far over the edge they read, so the board is called suspect (the instrument or the operating point is wrong)
  only when the board as a whole reads in error territory. The Mujina BZM2 reference firmware's later calibration mode
  uses this rule.
- **Keep a pooled board stop for gross faults.** A board wholly over the edge points at the instrument or the operating
  point, for example frames lost while PLLs are being moved (see
  [Live clock changes on a hashing chain](#live-clock-changes-on-a-hashing-chain)). A fault confined to fewer than half
  the ASICs looks the same as a tail and is handled the same way, per ASIC.
- **Do not pool "everything but the tail".** Trimming removes the ASICs that have to be counted, and a trimmed pool
  needs a trim fraction that nothing measured sizes.

### Calibration inputs that should be board-specific

The following should be measured on your own design, not copied from a vendor
reference system:

- PSU current limits
- PSU power limits
- board thermal limits
- acceptable stack imbalance
- safe junction temperature target
- fan or pump response curves
- pass-rate thresholds for field use

### What scales from 1 ASIC to 100 ASICs

A practical strategy for scale is:

- characterize at the domain level first
- then fine-tune per ASIC

For example:

- `1 ASIC`: one domain, direct per-ASIC tuning
- `4 ASICs`: tune the shared rail first, then trim per ASIC if needed
- `100 ASICs`: first establish safe per-domain voltage and coarse clock, then
  apply per-ASIC final offsets

The Mujina BZM2 reference firmware's tuning planner follows the same model.

## Design Recommendations By System Size

### Single-ASIC board

Recommended priorities:

- keep power sequencing simple and deterministic
- expose UART, reset, and trip for debug access
- expose DTS/VS in firmware or API from day one
- use direct per-ASIC characterization rather than heavy-weight broadcast flows

### Small multi-ASIC board

Recommended priorities:

- decide early whether all ASICs truly share one rail policy
- keep chain routing short and deterministic
- implement broadcast writes and per-ASIC unicast verification
- maintain enough sensor visibility to identify one bad ASIC quickly

### Large multi-domain system

Recommended priorities:

- treat domain balancing as a system function, not an afterthought
- separate board protection from mining software
- use broadcast for coarse actions and unicast for final trim
- persist calibration state and replay it on restart
- provide out-of-band observability for voltage, current, and trip events

## Common Failure Modes

Expect these classes of issues during bring-up:

- chain breaks due to mux orientation or RX/TX direction errors
- false confidence from UART liveness before IDs or PLLs are fully initialized
- stack imbalance during idle or partial-load operation
- thermal runaway from insufficient cooling during early ramp
- residual engine programming causing unexpected nonces
- malformed partial write-job sequences
- assuming all engine IDs are contiguous or present

Design for fast isolation:

- per-domain current and voltage visibility
- easy reset control
- easy UART capture
- per-ASIC NOOP and register-read debug
- trip logging

## Minimum Validation Checklist

Before calling a hardware platform ready, verify:

- control IO is truly `1.2 V` compatible
- reference clock integrity at the ASIC pin
- reset propagation through the entire chain
- per-ASIC enumeration from default ID
- `NOOP` response integrity across the full chain
- stable PLL lock across the intended operating range
- valid DTS/VS readings for every ASIC
- no dangerous stack imbalance at idle, dummy load, and production load
- sustained production pass rate at target operating point
- protection response for overtemperature and stack-voltage faults

## Relationship To The Mujina Reference Firmware

**Mujina** is the open-source miner firmware (256 Foundation) that the firmware-side examples in this reference
follow. BZM2 support for it is proposed upstream and is not part of its default branch. The proposal is tracked in
[Mujina's pull requests](https://github.com/256foundation/mujina/pulls?q=is%3Apr+bzm2), and the same branches are public in a
[reference fork](https://github.com/recklessnode/mujinabzm2). It covers:

- an ASIC and UART protocol driver: frame codec, UART controller and enumeration, on-die sensor streaming, engine
  discovery over TDM, PLL and DLL clock control, a calibration planner, a thermal interlock, work dispatch and result
  decoding, and UART diagnostics
- general fixes found along the way
- an RDS platform layer: the hashboard controller, rail sequencing and bring-up, fan control, run-time calibration and
  replay of a saved operating point

Mujina describes itself as a developer preview, so check the repository for current state before relying on any of
this. See the [Hardware Implementations Survey](bzm2-hardware-implementations.md) for how it sits among the other
projects.

Relevant follow-on documents:

- [UART and TDM Reference](blockscale-uart-protocol-reference.md) - the
  protocol companion to this guide
- [RDS Reference Measurements](rds-measured-reference.md) - observed data from one RDS unit, kept apart from this
  specification
