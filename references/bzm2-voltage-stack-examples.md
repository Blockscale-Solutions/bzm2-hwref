# BZM2 voltage-stack topology examples

Worked examples of how boards arrange BZM2 ASICs **in series and in parallel on one rail**, and what each
arrangement means for balancing and fault tolerance. The **RDS**, a production three-board system, is the
primary example and is treated in depth. Published open designs follow as comparisons. This page fills the
multi-ASIC gap noted in the [Integration Guide](blockscale-asic-integration-guide.md#core-rails-and-voltage-architecture)
with examples. It makes no new claim about the silicon.

- **Read this with:** the single-ASIC rail/stack drawing
  ([`single-asic-rail-stack.svg`](../drawings/rails/single-asic-rail-stack.svg)), the
  [voltage sensor channels](blockscale-asic-integration-guide.md#voltage-sensor-channels) table, and the
  [Hardware Implementations Survey](bzm2-hardware-implementations.md).
- **Evidence rules on this page:**
  - the RDS section is **topology and reasoning only**: no measurements from the system are published here;
  - every statement about an open-source board is cited to a repository, a commit and a file;
  - anything that cannot be read from a public source is marked **unconfirmed** or **not public**;
  - failure behaviour is circuit reasoning, not a measurement, and is marked **inferred**;
  - voltages computed from the published nominal per-ASIC figure are marked as arithmetic.

## The building block: one ASIC, two internal domains

One BZM2 operates with `VDD_HASH` in a window of roughly `0.6-0.81 V`, `0.71 V` nominal
([Electrical Quick Reference](blockscale-asic-integration-guide.md#electrical-quick-reference-per-asic)).
Internally that span is **two voltage domains in series**, a bottom and a top engine stack of ≈ `0.355 V`
each, with the midpoint brought out on `VDDINT_1/2`
([Core Rails](blockscale-asic-integration-guide.md#core-rails-and-voltage-architecture);
[Pinout, Rails](bzm2-pinout-reference.md)).

The voltage sensor reports three channels ([voltage sensor channels](blockscale-asic-integration-guide.md#voltage-sensor-channels)):
- `ch0` and `ch1`: the differential across the bottom and top domain (≈ `355 mV` each on a healthy part);
- `ch2`: the midpoint error between the two, which is small on a healthy part.

Two consequences for anyone reasoning about a stack:
- **A single ~355 mV sense reading is half an ASIC, not a whole one.** Dividing a board rail by it doubles the
  apparent series depth.
- **The ASIC's full span is `ch0 + ch1` plus the midpoint term, not `ch0 + ch1` alone.** A small per-ASIC `ch2`
  is negligible for one part. Summed down a long string it is not: leaving it out undercounts the string by
  N × `ch2`.

## Vocabulary

| term | meaning here |
| --- | --- |
| **voltage domain** | one internal half-stack of an ASIC (≈ 0.355 V); every ASIC is two domains in series |
| **ASIC level** (series level) | a group of ASICs sharing the same bottom (VSS) and top (VDD) node; levels stack on each other |
| **parallel count (p)** | ASICs per level; they share the level's current |
| **NsMp** | N ASIC levels of M ASICs in parallel: N × M ASICs and 2N voltage domains in series on one rail |
| **rail** | the regulated supply across the whole string, ≈ N × per-ASIC voltage |

In a series stack the **same current** flows through every level. Each level's voltage is set by how much
current its members want at that voltage, relative to the other levels. Levels are never exactly equal, and
the division follows the load. That is why a stacked board has to keep every level loaded alike (see
[Dummy-job use is not optional in stacked systems](blockscale-asic-integration-guide.md#dummy-job-use-is-not-optional-in-stacked-systems)).

## Primary example: RDS (production system; 3 boards on one rail)

**Source:** structure and reasoning only. No measurements from this system are published on this page.

### Structure

- **3 hashboards** on **one shared supply rail** with **one setpoint**.
- Each board has **100 ASICs**, presented by the vendor telemetry as **25 stacks of 4**.
- Each board's controller **enables or disables** its board. It has **no per-board voltage setpoint**.

![RDS stack wiring: 25s4p settled; 2s2p ruled out](../drawings/rails/stack-example-rds-readings.svg)

### Wiring: 25 ASIC levels × 4 in parallel (settled by analysis)

Each board is **25 ASIC levels of 4 ASICs in parallel (25s4p)**. Because every ASIC is two internal domains
in series, that is **50 voltage domains in series but 25 ASIC levels**. The "50" that appears when a rail is
divided by a ~355 mV reading counts domains, not ASICs.

**Why 2s2p is ruled out.** The alternative reading wires each stack of 4 as two in series by two in parallel,
which puts **50 ASICs** in series per board.
- Divide the board rail by 50 and each ASIC would sit near **0.35 V**: half its nominal, and well **below the
  ~0.6 V bottom of its operating window**
  ([Electrical Quick Reference](blockscale-asic-integration-guide.md#electrical-quick-reference-per-asic)).
- The boards hash at their normal operating point. They could not do that with every ASIC at half its
  minimum operating voltage.
- Read the other way, 2s2p at the nominal 0.71 V per ASIC would need a rail of about 50 × 0.71 ≈ 35.5 V: twice
  the setpoint discussed in [#4](https://github.com/Blockscale-Solutions/bzm2-hwref/issues/4).
- The 2s2p reading comes from dividing the rail by one ~355 mV domain sense as if it were a whole ASIC.

**Physical confirmation (non-destructive).** With a board **unpowered**, check continuity between the
ground-side (VSS) pads of the four ASICs in one stack:
- under 25s4p they are **one node**;
- under 2s2p they would be **two nodes**.

This is the decisive physical check. Telemetry from a running board supports 25s4p through the arithmetic
above; the continuity check confirms it directly. No fault is induced and no setpoint is changed.

### Per-level voltage arithmetic

- **The rail is a commanded setpoint, not a constant.** The supply is set to a target, the delivered rail
  differs slightly from it, and the vendor's calibration may move the setpoint. Reason with "rail / 25", not
  with a fixed number.
- **Average per-level voltage = rail / 25**, and each level is one ASIC's span (`ch0 + ch1 +` the midpoint term).
- **Levels are not equal.** Each level's share follows its members' current demand. The real per-level
  spread is not published, so treat "rail / 25" as the mean, not as every level.

| quantity | value | basis |
| --- | --- | --- |
| rail at the nominal 0.71 V per ASIC | 25 × 0.71 ≈ **17.75 V** | arithmetic |
| rail range spanned by the 0.6-0.81 V operating window | 25 × 0.6 ≈ 15.0 V to 25 × 0.81 ≈ 20.25 V | arithmetic; this is the chip window, not the system's calibration range |
| board string current | 4 × the per-ASIC stack current | topology |
| board string current at the reference stock point | 4 × ~14 A ≈ 56 A | arithmetic on the reference's per-ASIC figure; real boards differ |

### What a failure does (inferred)

Circuit reasoning under 25s4p. The rows describe direction and rough size, not measured values.

| failure | the failed ASIC | its 3 parallel partners | the rest of its board's string (24 levels) | the shared rail and the other two boards |
| --- | --- | --- | --- | --- |
| **open ASIC** | carries no current, stops hashing | carry the level's current between three: **about +33 % each** if the string current holds (e.g. ~14 A → ~18.7 A at the reference stock point) | a small redistribution: the level with the open device takes slightly more voltage | essentially unchanged |
| **shorted ASIC** | carries **nearly the whole string current** (≈ 4 × the per-ASIC current) through the fault: a local heating hazard | **bypassed**: ≈ 0 V and ≈ 0 current, stop hashing (4 ASICs lost in total) | the rail is shared by 24 levels instead of 25: **≈ +4.2 % on average**, more on the worst level | that board's current and power rise at the same setpoint. Other boards are unaffected if regulation holds |
| **silent but conducting** (stopped hashing, still powered) | draws less current, so its level's voltage rises | see the higher level voltage and draw more current, partly buffering the fault inside the level | slightly less voltage for the other levels | unchanged. Keeping the silent ASIC loaded with dummy work, if it still accepts writes, is the balancing tool |
| **failed level: open** | — | — | **string current stops**: that board stops hashing; nearly the full rail can appear across the gap unless the board has a per-level bypass element (not public) | the supply sees about a one-third load step; the other two boards keep the same setpoint if regulation holds |
| **failed level: short** | as a shorted ASIC | as a shorted ASIC | as a shorted ASIC | as a shorted ASIC |

**Several shorted levels.** With k levels shorted, the survivors share the rail 25 / (25 − k):

| shorted levels k | average rise | average per-level at a 17.75 V rail (arithmetic) |
| --- | --- | --- |
| 1 | +4.2 % | ≈ 0.740 V |
| 2 | +8.7 % | ≈ 0.772 V |
| 3 | +13.6 % | ≈ 0.807 V |
| 4 | +19.0 % | ≈ 0.845 V |

Levels are uneven, so the **worst** level crosses the ~0.81 V top of the operating window **sooner than the
average predicts**: after the third shorted level rather than the fourth, where the average only just reaches it.

**0.81 V is the top of the operating window, not a damage threshold.**
- The ASIC's own voltage shutdown acts on `ch0` and `ch1` against programmable thresholds
  ([voltage sensor channels](blockscale-asic-integration-guide.md#voltage-sensor-channels)).
- The absolute-maximum `VDD_HASH` and the default trip thresholds are **not public**.
- Between the operating maximum and the chip's own trip there is a band in which nothing on the chip acts.
  **Host software has to guard that band**: bound per-level voltage, and take the board down before the
  chip's own trip is the only protection.

### Why voltage cannot be trimmed per board

- The three boards share **one** rail with **one** setpoint. Moving it moves every level on every board.
- The board controller can only **enable or disable** its board. It has no voltage setpoint.
- Within a board, a level's voltage is not set directly at all: it follows that level's current demand relative to
  the other 24.

So a board with a shorted level cannot be "trimmed back". Lowering the shared rail to bring its 24 surviving levels
back into the window also lowers all 25 levels on each healthy board, costing them headroom and hashrate. The
per-board levers are **load**: engine enablement, frequency and dummy work. Beyond those the only per-board
action is **on/off**.

### Fault-tolerance implications

- **Single open ASIC: survivable in principle.** Its three partners carry the level at about +33 % current, and
  the board can keep running at a derated string current if that stays inside the parts' limits.
- **Single short: survivable in principle, at a cost.**
  - 4 ASICs stop.
  - The rest of the string runs about 4 % high on average, with the worst level higher.
  - The failed part carries the string current.
  - Each further short narrows the margin quickly, and by the third the worst level is past the operating
    maximum.
- **A failed-open level ends that board**, and removes a third of the load from a supply shared with two other
  boards.
- **Detection has to come from per-ASIC telemetry.**
  - The publicly documented sense is per ASIC (`ch0`/`ch1`/`ch2`).
  - A level's state is inferred from its four members, and a string's total must include the midpoint term.
- **Isolation is board-granular.** The only isolating action is disabling a whole board. Conventional practice
  treats a failed hashboard as catastrophic: disable it, keep the others hashing, and do not bring it back
  automatically.
- **Re-enabling a board onto a live shared rail is uncharacterised publicly.**

### Not public (RDS)

- measured rail, string current and per-level spread;
- the calibration range of the setpoint;
- `VDD_HASH` absolute maximum and default trip thresholds;
- whether the board has per-level bypass or bleed elements;
- the result of the continuity check.

## Comparison examples

These published designs sit after the RDS because they are smaller and, as far as is publicly known, **less
proven** in hardware. They are useful as clean illustrations of 1-wide and 2-wide levels.

### bitaxeBIRDS (4s1p): published design, untested prototype

**Source:** [bitaxeorg/bitaxeBIRDS](https://github.com/bitaxeorg/bitaxeBIRDS) at
[`11d188d`](https://github.com/bitaxeorg/bitaxeBIRDS/tree/11d188de8778dd4a394ca4740a7cc3f722619baf)
(default branch `pico`), CERN-OHL-S-2.0. **Status: untested prototype.** Its own README says "It is still an
untested prototype!" ([`README.md` line 5](https://github.com/bitaxeorg/bitaxeBIRDS/blob/11d188de8778dd4a394ca4740a7cc3f722619baf/README.md)).
The topology below is read off the design files; it says nothing about whether the board works.

![bitaxeBIRDS 4s1p and bitaxeBonanza 4s2p stacks (published designs)](../drawings/rails/stack-example-bitaxe-4s1p-4s2p.svg)

| property | value | basis |
| --- | --- | --- |
| ASICs | 4 | [`README.md`](https://github.com/bitaxeorg/bitaxeBIRDS/blob/11d188de8778dd4a394ca4740a7cc3f722619baf/README.md) line 10: "Four Intel BZM2 ASICs, powered in series" |
| series levels × parallel | **4 × 1** | [`ASIC.kicad_sch`](https://github.com/bitaxeorg/bitaxeBIRDS/blob/11d188de8778dd4a394ca4740a7cc3f722619baf/ASIC.kicad_sch) nets: A1 `VSS` = `GND`; A1 `VDD` = `DOMAIN1` = A2 `VSS`; A2 `VDD` = `DOMAIN2` = A3 `VSS`; A3 `VDD` = `DOMAIN3` = A4 `VSS`; A4 `VDD` = `VDD` (regulator output). One ASIC per level |
| rail | one TPS546D24S "tuned for 2.8V output @ 20A" | `README.md` line 16; regulator `U2` TPS546D24 in [`Power.kicad_sch`](https://github.com/bitaxeorg/bitaxeBIRDS/blob/11d188de8778dd4a394ca4740a7cc3f722619baf/Power.kicad_sch) driving net `VDD` |
| per-ASIC voltage | ≈ 0.70 V (2.8 V / 4; arithmetic) | README line 11: "Each BZM2 is nominally 0.7V"; single-chip sweep 0.68-0.81 V in [`doc/specs.md`](https://github.com/bitaxeorg/bitaxeBIRDS/blob/11d188de8778dd4a394ca4740a7cc3f722619baf/doc/specs.md) |
| per-level IO rail | four MCP1824T-1202 1.2 V LDOs (`U6`, `U1`, `U3`, `U4`), each with its `GND` pin on its level's bottom node (`GND`, `DOMAIN1`, `DOMAIN2`, `DOMAIN3`), each output feeding that ASIC's `VDDIO` (`1V2-1`..`1V2-4`) | `ASIC.kicad_sch` |
| per-level sense | the three intermediate nodes `DOMAIN1/2/3` go to Pico 2W ADC inputs `GP26_A0`, `GP27_A1`, `GP28_A2` | [`data.kicad_sch`](https://github.com/bitaxeorg/bitaxeBIRDS/blob/11d188de8778dd4a394ca4740a7cc3f722619baf/data.kicad_sch) |
| balancing hardware | **none found** in the power path: no shunt balancers or per-level regulators on the stack | `ASIC.kicad_sch`, `Power.kicad_sch` (absence on the schematic) |

**Balancing.** The schematic is passive: the four ASICs share the string current and hold balance by being
loaded alike. What the board adds is **observability**: every intermediate node is on an ADC, so a level
drifting off 1/4 of the rail is visible directly. The firmware balancing policy is not part of this
repository and is **unconfirmed** here. Public reference firmware for four-series BZM2 boards bounds the
aggregate rail to 2.1-3.2 V ([`main/device_config.h:142-143`](https://github.com/johnny9/ESP-Miner-Bonanza/blob/474c8bcb7892b7b94496e21b975b14c4a3c575c1/main/device_config.h#L142-L143)
@ `474c8bc`). Per ASIC, it bounds `ch0` and `ch1` independently and treats a large `ch0`/`ch1` spread as a
stack-imbalance fault ([`main/Kconfig.projbuild:207-270`](https://github.com/johnny9/ESP-Miner-Bonanza/blob/474c8bcb7892b7b94496e21b975b14c4a3c575c1/main/Kconfig.projbuild#L207-L270)).

**Failure behaviour (inferred):**
- **Failed short:** the three survivors share the rail, 2.8 / 3 ≈ 0.93 V each, above the ~0.81 V top of the
  window. The rail must come down at once.
- **Failed open:** string current stops, the board stops hashing, and nearly the whole rail can appear across
  the open device.
- **Stops hashing but still conducts:** its current falls, so its level rises and the others fall. That is
  visible on the `DOMAIN` ADCs.

**Fault tolerance:** none by topology. With one ASIC per level, any single device failure ends the string.
The design's point of interest is that a failure would be **observable per level** from the host.

### bitaxeBonanza (4s2p): published design, not known to have been built

**Source:** [bitaxeorg/bitaxeBonanza](https://github.com/bitaxeorg/bitaxeBonanza) at
[`51b31ad`](https://github.com/bitaxeorg/bitaxeBonanza/tree/51b31ad8e6962b76d652d8b956b0495d39725633)
(branch `1001x`). **Status: a published design with no known assembled units.** To the maintainer's
understanding, it is not known to have been built as of 2026-09. Its README also says the design "doesn't
work because issue #3 and might never work because issue #4" (the UART level-shifter and 9-bit issues, not
the stack). It is included only as the public example of **parallel ASICs within a level**, and must not be
read as proven hardware.

| property | value | basis |
| --- | --- | --- |
| ASICs | 8 | [`README.md`](https://github.com/bitaxeorg/bitaxeBonanza/blob/51b31ad8e6962b76d652d8b956b0495d39725633/README.md): "Eight Intel BZM2 ASICs" |
| series levels × parallel | **4 × 2** | [`asic.kicad_sch`](https://github.com/bitaxeorg/bitaxeBonanza/blob/51b31ad8e6962b76d652d8b956b0495d39725633/asic.kicad_sch) nets: A1+A2 `VSS` = `GND`, `VDD` = `GND1`; A3+A4 `GND1`→`GND2`; A5+A6 `GND2`→`GND3`; A7+A8 `GND3`→`Vcore` |
| rail | net `Vcore`, fed by two TPS546D24A (`U3`, `U4`) whose inductors (`L1`, `L2`) both land on `Vcore` | [`power.kicad_sch`](https://github.com/bitaxeorg/bitaxeBonanza/blob/51b31ad8e6962b76d652d8b956b0495d39725633/power.kicad_sch) |
| rail voltage | not stated in the repository (**unconfirmed**); ≈ 4 × 0.71 ≈ 2.8 V nominal by arithmetic, the same series depth as bitaxeBIRDS | arithmetic |
| per-level IO rail | MCP1824 1.2 V LDOs with `GND` pins on the level nodes (`U10`→`GND1`, `U9`→`GND2`, `U8`→`GND3`; `U11` and the host-side parts on `GND`) | `asic.kicad_sch` |
| per-level sense | no level nodes found on host ADC pins in `esp32.kicad_sch` (**unconfirmed**; not found, not proven absent) | [`esp32.kicad_sch`](https://github.com/bitaxeorg/bitaxeBonanza/blob/51b31ad8e6962b76d652d8b956b0495d39725633/esp32.kicad_sch) |

**Failure behaviour (inferred):**
- **Short:** takes out both ASICs of its level, and the other three levels rise to ≈ 0.95 V. The rail must come down.
- **Open (one device):** the partner carries the whole level current, about twice its share.

### HashBed (16 ASICs, series-stacked): survey-level only

**Source:** the [Hardware Implementations Survey](bzm2-hardware-implementations.md) only. HashBed's
repository is **private during development**, so nothing below goes beyond what the survey already states.

| property | value | status |
| --- | --- | --- |
| ASICs | 16 | public (survey) |
| stacking | "series-stacked", 3D-printer-heatbed tile form factor | public (survey) |
| host / bridge | RP2040 (PIO) | public (survey) |
| core rail control | "PMBus controller-based core rail" | public (survey) |
| IO | per-bit level translation, native 1.2 V oscillator | public (survey) |
| series levels × parallel | **unconfirmed** (16s1p, 8s2p and 4s4p are all "series-stacked") | not public |
| per-ASIC operating voltage | **unknown** | not public |
| rail voltage | **unknown** | not public |
| balancing, per-level sense | **unconfirmed** | not public |

**Failure behaviour and fault tolerance:** cannot be stated until the parallel count is public. The general
pattern applies: with 1 per level, any single device ends the string. With p > 1, a single open is
carried by the partners at p/(p−1) of their share, and a short costs a whole level.

## Comparison

| | **RDS (25s4p)** | bitaxeBIRDS | bitaxeBonanza | HashBed |
| --- | --- | --- | --- | --- |
| status | production system (structure only here) | published design; **untested prototype** (its README) | published design; **not known to have been built** (2026-09) | private development |
| ASICs on the string | 100 per board; 3 boards on one rail | 4 | 8 | 16 |
| ASIC levels × parallel | **25 × 4** (2s2p ruled out) | 4 × 1 | 4 × 2 | **unconfirmed** |
| voltage domains in series | 50 | 8 | 8 | unconfirmed |
| rail | one commanded setpoint shared by 3 boards; ≈ 17.75 V at the nominal (arithmetic) | 2.8 V (stated) | ≈ 2.8 V (arithmetic; unstated) | unknown |
| per-ASIC voltage | ≈ rail / 25 | ≈ 0.70 V | ≈ 0.71 V (nominal assumed) | unknown |
| per-level host sense | per-ASIC VS only (public) | yes: 3 ADC nodes | not found | unconfirmed |
| per-board voltage trim | **no** (shared rail; board control is on/off) | n/a (one board) | n/a | unconfirmed |
| single short (inferred) | 4 ASICs lost; failed part carries the string current; others +4.2 % average | survivors ≈ 0.93 V: rail down | level lost; others ≈ 0.95 V: rail down | depends on p |
| single open (inferred) | partners +33 % | string stops | partner at ≈ 2× | depends on p |
| survives one device fault? | **yes, within limits** (inferred) | no | open: marginal; short: no | unconfirmed |

**The pattern:**
- more ASICs in parallel per level make a single open survivable;
- more levels make a single short survivable at a small overvoltage;
- a one-per-level design trades that tolerance for per-level observability at low cost.

In every case the limits (worst-level voltage, partner current, and the band between the operating maximum and
the chip's own trip) must be characterised on the real board before any firmware relies on them.

## Gaps

- RDS: the unpowered continuity check that physically confirms 25s4p, and everything listed under "Not public (RDS)".
- HashBed: topology and operating voltage, private until release.
- bitaxeBonanza: rail setpoint and per-level sense not found in the public design files; no known built units.
- bitaxeBIRDS: untested prototype per its README; no public characterisation of its stack under fault.
