# BZM2 Reference Design Guidance — a menu of proven approaches and parts

A **parts-and-approaches catalog** for building a board around the Intel BZM2 (Blockscale 1000-series)
ASIC. Where the [Board Design Guide](bzm2-board-design-guide.md) tells you *what patterns* work and *what
pitfalls* to avoid, this document gives you a **menu of specific, off-the-shelf ways to implement each
function** — with real manufacturer part numbers, trade-offs, and a "when to pick it" — so a designer can
choose deliberately rather than start from a blank page.

## How to read this

Each entry is written as *"an effective, proven approach leverages [method] with [example parts] in this
manner"* — a starting point to adapt, **not a schematic to copy**. Every named part is a real,
publicly-datasheeted commodity component; every "an open board does this" note points at a public
open-source design you can inspect. Pick the row that matches your cost, current, and hand-assembly
constraints, then verify the exact values against the ASIC's own datasheet on your board.

- **This is designer guidance, not a reference schematic.** No proprietary or vendor-confidential design
  is reproduced here; the approaches are assembled from public component datasheets, the public open-source
  BZM2 board ecosystem, and general mixed-signal practice.
- **The electrical requirements** each section designs against come from the public
  [Integration Guide](blockscale-asic-integration-guide.md) and [Board Design Guide](bzm2-board-design-guide.md)
  in this repository.
- Where a value can't be confirmed from a public source it is marked *designer to verify against the ASIC
  datasheet.*

> **Scope note.** This catalogs *alternatives* — it does not prescribe one bill of materials. The right
> choice depends on your current level, whether you hand-assemble or reflow, single- vs multi-ASIC
> topology, and cost target. Characterize every limit on your own board before committing it.

---

# 1. Host ↔ ASIC digital interface & reference clock

**The requirement.** Every host-facing digital pad — UART TX/RX, `NRST`, `TRIP`, `REFCLKIN` — lives on
the ASIC's **1.2 V IO domain**, with an input ceiling of **`VDDIO + 0.3 V` ≈ 1.5 V** (VDDIO abs-max
1.3 V). A typical host (USB bridge, MCU, oscillator) is 3.3 V. Crossing this boundary cleanly is the #1
dead-on-arrival risk, and the UART adds a second constraint: it is **fixed 9-bit multidrop** (8 data + a
9th *address/data* bit — not parity), 2.5–10 Mbps, 5 Mbps bring-up convention.

## 1.1 Level translation (1.2 V ↔ 3.3 V)

A proven approach crosses the boundary with a **real IC level translator whose low-side supply (VCCA)
sits on the ASIC's own 1.2 V IO rail** — this is both what the mature open BZM2 boards do and the
reference-grade practice (a passive diode-clamp or divider is a shortcut, not the robust answer). The only
translator families that qualify are those whose VCC floor is *at or below* 1.2 V.

| An effective approach leverages… | …with these example parts | …in this manner | When to pick it |
|---|---|---|---|
| A **0.65 V-floor translator** for maximum 1.2 V margin | TI **SN74AXC4T774** (4-bit, per-bit direction, X2QFN) · **SN74AXC1T45** (1-bit, SOT-23-6) [AXC4T774 ds](https://www.ti.com/lit/ds/symlink/sn74axc4t774.pdf) · [AXC1T45 ds](https://www.ti.com/lit/ds/symlink/sn74axc1t45.pdf) | VCCA on the 1.2 V IO rail, VCCB on 3.3 V; one `4T774` covers the mixed set (UART ×2 + reset + trip) with an independent DIR pin per line, or use several `1T45` in leaded SOT-23 for hand assembly | **Default.** The AXC family's 0.65 V floor buys real margin at 1.2 V. `4T774` for a reflow board; `1T45` ×N for hand-solder. |
| A **1.2 V-floor translator** in a leaded package | TI **SN74AVC4T774** (TSSOP) · **SN74AVCH1T45** (SOT-23-6, bus-hold) [AVC4T774 ds](https://www.ti.com/lit/ds/symlink/sn74avc4t774.pdf) · [AVCH1T45 ds](https://www.ti.com/lit/ds/symlink/sn74avch1t45.pdf) | Same wiring; runs *at* the 1.2 V floor rather than below it — leaded TSSOP/SOT-23 are easier to hand-solder than the AXC's tiny QFN | When you want a leaded package and accept working at the floor (verify your 1.2 V rail tolerance). |
| A **passive AC-couple + bias** for AC-only lines | series cap + bias network to ~0.6 V | Blocks DC and re-centers an *edge* signal (clock) in the 1.2 V window; the multi-ASIC `REFCLKOUT→REFCLKIN` chain is AC-coupled anyway | Clock hops between stacked ASICs; never for a DC-meaningful line like reset. |

**Mis-picks — never on the 1.2 V rail:** **SN74LVC1T45** (1.65 V floor — the famous wrong choice, pin-alike
to AVC/AXC) · **TXS0102/TXS010x** (1.65 V floor *and* open-drain pass-gate) · **any resistive divider** into
a pad (DC-loads the source, rounds edges, and can breach the ≈1.5 V ceiling). Auto-direction parts
(TXB/TXS class) also dislike the 50 MHz clock — prefer a strap you can verify in review over edge-rate
artifacts you can't.

*Open-board corroboration:* bitaxeBonanza and HashBed ship the `SN74AXC4T774` (0.65 V floor); Satoshi
Starter uses the `SN74AVCH1T45` (1.2 V floor, bus-hold), one per signal. *(EmberOne00/01 use the AVC4T774
in TSSOP but translate the **BM1362** sibling's IO, not the BZM2's — a package data point only.)*

## 1.2 9-bit UART host bridge

The host must emit/receive **true 9-bit frames** at ≥5 Mbps. A proven approach uses either a hardware
bridge with a native 9-bit mode, or a reprogrammable controller whose UART/PIO can be told to do 9 bits.

| An effective approach leverages… | …with these example parts | …in this manner | When to pick it |
|---|---|---|---|
| A **hardware USB-UART bridge with a native 9-bit mode** | MaxLinear **XR21V1410** (1-ch) / **XR21V1414** (4-ch) [ds](https://www.maxlinear.com/ds/xr21v1410.pdf) | Its "Multidrop (9-bit) Mode" with auto half-duplex does 9-bit up to 12 Mbps — clears 5 Mbps bring-up and the 10 Mbps ceiling; appears to a host PC as a COM port with no MCU firmware | A USB-attached bench/bring-up host that must talk to the chip directly. **Satoshi Starter takes this path (XR21V1414).** |
| A **reprogrammable MCU doing 9-bit in PIO** | Raspberry Pi **RP2040 / RP2350** [ds](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) | PIO builds arbitrary framing — `9N1` at 5 Mbps is proven in the open bridge firmware; the same MCU can also run fan/board control and the VCORE ramp | The community's proven, cheap, reprogrammable path. **bitaxeBIRDS and HashBed use RP2040 PIO; bitaxeBonanza pairs its ESP32-S3 with an RP2040 for exactly this.** |
| A **native hardware 9-bit USART** | STM32F4-class MCU (USART word-length M=1 → 9 data bits) [RM0090](https://www.st.com/resource/en/reference_manual/rm0090-stm32f405415-stm32f407417-stm32f427437-and-stm32f429439-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) | True hardware 9-bit with multiprocessor/address-mark wakeup; write the 9th bit in the data register (not as parity) | A board that already has an STM32 for control and wants the UART in silicon, not PIO. |

**Do NOT** try to emulate the 9th bit with a general MCU's **parity bit** — it's asynchronous to the data
register and fails at ≥5 Mbps. This is publicly demonstrated: the ESP32 cannot do it
([bitaxeorg/bitaxeBonanza#4](https://github.com/bitaxeorg/bitaxeBonanza/issues/4)), which is why the
Bonanza design adds an RP2040. Also out on speed/mode: **CH340** (~2 Mbps), **FTDI FT231X** (3 Mbps) /
**FT232** (no per-byte 9-bit), **CP2102** (8-bit only).

## 1.3 50 MHz reference clock

`REFCLKIN` is a 1.2 V input with the same ≈1.5 V ceiling. The reference-grade and lowest-risk answer is a
**1.2 V-domain clock source**, delivered directly.

| An effective approach leverages… | …with these example parts | …in this manner | When to pick it |
|---|---|---|---|
| A **native 1.2 V oscillator, direct-drive** | SCTF **SX3M50.000E20F30THN** (50 MHz, 1.2 V, ±20/30 ppm, 3225) [ds](https://datasheet.lcsc.com/lcsc/2209051730_Shenzhen-SCTF-Elec-SX3M50-000E20F30THN_C5137267.pdf) · LCSC `C5137267` | Drives `REFCLKIN` directly — no translator, no divider, no source loading, no ceiling risk; series-terminate the trace | **Default, and what the open boards ship.** Fewest parts, lowest risk. |
| A **3.3 V oscillator + fast translator** | e.g. Epson **SG3225CAN 50 MHz** (1.6–3.63 V) [product](https://www.epsondevice.com/crystal/en/products/crystal-oscillator/sg3225can.html) or SiTime **SiT8008** → an AXC/AVC translator (§1.1) | XO runs at its native voltage; a 50 MHz-capable translator drops it to 1.2 V and unloads the oscillator | When you need a specific low-jitter/tight-ppm Western-brand XO only sold at ≥1.6 V, or already have a fast translator placed. **Satoshi Starter uses this branch (SG3225CAN + translate).** |
| A **3.3 V oscillator + AC-couple + bias** | XO + series cap + bias to ~0.6 V | Re-centers the clock in the 1.2 V window passively; respect the ≈1.5 V ceiling in the bias network | Cost-down passive path, or reusing the multi-ASIC daisy-chain AC-couple network. |

**Never** a resistor divider into the clock pad (breaches the ceiling, rounds the edge). **Availability
honesty:** native 1.2 V MHz oscillators are a niche — the Western majors (SiTime, Epson, Kyocera) floor
above 1.2 V, so if second-sourcing a 1.2 V XO matters, plan the translator branch as the fallback.
*Designer to verify current stock at order time.* **Multi-ASIC:** daisy-chain `REFCLKOUT → REFCLKIN`
AC-coupled down the stack. *Open-board corroboration: bitaxeBIRDS and HashBed ship the native 1.2 V
`SX3M50`; EmberOne runs a 25 MHz part because BM1362 clocks at 25 MHz, not the BZM2's 50 MHz.*

---

# 2. Power delivery & control (VCORE / VDD_HASH)

**The requirement.** `VDD_HASH` is a **0.6–0.81 V window, 0.71 V nominal** rail that the host must **ramp
in software under voltage-sensor feedback** and trim per-part — drawing ~14 A stock to ~27 A tuned
(**plan ~30 A copper**). The ASIC has an on-die 3-channel voltage sensor but **no on-die VCORE
regulator**: the buck and its digital control are the board designer's to build. The reference-grade
approach controls VCORE **digitally** (a controllable VRM, or a DAC injected onto a buck's feedback node) —
never a fixed pot, which can neither ramp nor usually span the window.

## 2.1 VCORE regulation with digital control

### Route A — an integrated PMBus/I²C VRM (fewest parts, richest telemetry)

A proven approach sets and ramps VCORE over a digital bus, and gets **remote sense and V/I telemetry in the
same chip** — folding three functions into one part.

| An effective approach leverages… | …with these example parts | …in this manner | When to pick it |
|---|---|---|---|
| A **stackable integrated PMBus buck** | TI **TPS546D24A** (40 A/phase, up to 4× stack → 160 A, on-chip differential remote sense) [ds](https://www.ti.com/lit/ds/symlink/tps546d24a.pdf) | One chip = buck + digital set/ramp + Kelvin sense + IOUT/VOUT/temp readback; stack phases to cover 14→30 A and multi-ASIC on one address | **Default for a serious core rail.** **bitaxeBIRDS (single) and bitaxeBonanza (multi) use exactly this.** |
| A **smaller integrated PMBus buck** | TI **TPS546B24A** (20 A) [ds](https://www.ti.com/lit/ds/symlink/tps546b24a.pdf) · ADI **MAX20730** (25 A integrated-FET) [ds](https://www.analog.com/media/en/technical-documentation/data-sheets/max20730.pdf) | Same digital-set + telemetry in a cheaper/smaller part; 20–25 A covers the stock point with modest headroom | Cost-down single-ASIC board that won't be pushed to the top of the tuning window. |
| A **PMBus controller + external FETs** | ADI **LTC3886** (dual, 16-bit ADC/12-bit DAC, diff remote sense, fault logging) [ds](https://www.analog.com/en/products/ltc3886.html) driving discrete N-FETs (e.g. onsemi **NTMFS3D6N10MCL**) | Size current by choosing FETs; full PMBus telemetry + EEPROM fault logging | When you want to set current with discrete FETs and want rich telemetry. **HashBed uses the LTC3886 + discrete FETs.** |

For very large aggregated multi-ASIC domains, data-center VR controllers (TI **TPS53681**, MPS **MP2891**,
Renesas **RAA228228**) scale further via DrMOS smart-stages — noted for completeness; overkill for one ASIC.

### Route B — a DAC injected into a conventional buck's feedback (cheapest, most hand-solderable)

A proven approach keeps a commodity analog buck and lets firmware move its output by pushing/pulling a
small current (or voltage) onto the feedback node — decoupling "which buck" from "how firmware controls
it."

| An effective approach leverages… | …with these example parts | …in this manner | When to pick it |
|---|---|---|---|
| A **current-DAC into the FB node** | Maxim/ADI **DS4432U** (dual I²C 7-bit ±200 µA, **outputs zero on power-up**) [ds](https://www.analog.com/media/en/technical-documentation/data-sheets/ds4432.pdf) on a buck like TI **LM25119** [ds](https://www.ti.com/product/LM25119) | Sinks/sources current into FB to raise/lower Vout in fine steps; the buck's 0.8 V floor is *pulled down into* the 0.6–0.81 V window by the DAC; power-up-zero matches the "start conservative" bring-up rule | Cost-conscious, hand-assembled board. **This is the canonical EmberOne00 route (DS4432U → LM25119 FB, INA260 closing the loop).** |
| A **voltage-DAC into FB via a summing R** | Microchip **MCP4726** (12-bit, EEPROM-stored setpoint) [ds](https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/22272C.pdf) | Finer VCORE granularity than a 7-bit current-DAC; restores its setpoint from EEPROM; SOT-23 is the easiest solder | When you want fine, repeatable VCORE steps but still a simple analog buck. |

**Route C — analog + trim (fixed divider / pot) is disqualified:** it cannot perform the host-driven
ramp-under-sensor-feedback the ASIC expects, usually can't span the full window, and gives no per-part
trim. Listed only to rule out (see the `bitaxeBonanza#1` VRM-strap failure).

## 2.2 Remote / Kelvin sense

At 0.71 V, 20–30 mV of IR drop is 3–4 % of the rail — sense **at the ASIC land**, not the converter cap.

- **On-chip differential remote sense** (present on TPS546x / LTC3886 / MAX20730): route VOSNS± to the
  ASIC VDD_HASH/VSS land — zero extra parts, the loop regulates *at the load*. **The default when a Route-A
  VRM is already on the board.**
- **Kelvin the FB divider to the land** (for the Route-B DAC-into-FB path): take the top of the
  feedback/summing network from a dedicated sense trace at the ASIC. Same IR-drop rejection with a
  controller that has no dedicated sense pins.
- **No remote sense (regulate at the cap): rejected** for this rail — it bakes the IR drop into VCORE.

## 2.3 Current sense + telemetry (feeds the stack-imbalance safety loop)

The host needs live rail V/I for the safety loop the on-die sensor feeds. Note the **~30 A** ceiling:
integrated-shunt monitors top out near ±15 A, so at full current, sense per-phase, use an external shunt,
or read the VRM's own PMBus.

| An effective approach leverages… | …with these example parts | …in this manner | When to pick it |
|---|---|---|---|
| An **integrated-shunt I²C monitor** | TI **INA260** (2 mΩ internal shunt, direct A/W, alert) [ds](https://www.ti.com/lit/ds/symlink/ina260.pdf) | No external shunt/calibration; iron-solderable TSSOP; ~±15 A range | Per-phase or ≤15 A / multi-ASIC-slice monitoring. **EmberOne00 uses the INA260.** |
| An **external-shunt precision monitor** | TI **INA228** (20-bit, 85 V, energy accumulation) [ds](https://www.ti.com/lit/ds/symlink/ina228.pdf) | Pick the shunt for full 30 A; measures the whole rail at one point | Full-current single-point sensing when INA260's range is exceeded. |
| The **VRM's own PMBus readback** | TPS546x / LTC3886 READ_IOUT/VOUT/TEMP | Zero added parts if a Route-A VRM is already present; covers full current inside the VRM | Default when a PMBus VRM is on the board; add an INA only for an independent cross-check. |
| A **generic ADC across your own shunt + stack taps** | TI **ADS1115** (16-bit, 4-ch, PGA) [ds](https://www.ti.com/lit/ds/symlink/ads1115.pdf) | One ADC watches shunt current **and** the bottom/top stack-node voltages the on-die sensor reports | Belt-and-suspenders for the imbalance loop. |

## 2.4 Rail LDOs (1.2 V VDDIO; 0.75 V normally on-chip)

The **1.2 V VDDIO** is a *quality reference*, not a power rail — accuracy beats current, and you must never
let tolerance stack push it past the **1.3 V abs-max**. A proven approach uses a tight-tolerance small LDO
from an existing 1.8/3.3/5 V rail: TI **TPS7A20** (1.5 % accuracy, fixed-1.2 V option, low noise)
[ds](https://www.ti.com/lit/ds/symlink/tps7a20.pdf) for the low-noise default, or **TLV757P** (fixed 1.2 V,
SOT-23 — easiest hand-solder) [ds](https://www.ti.com/lit/ds/symlink/tlv757p.pdf). The **0.75 V (VDD_P75)**
rail is **normally generated by the ASIC's on-chip LDO** — do nothing but decouple locally; provide an
external 0.75 V source (e.g. an adjustable **TLV75901**) *only* to bypass the on-chip path, and only if a
datasheet-confirmed reason exists.

---

# 3. Protection, supervision & thermal

**The requirement.** Input is usually a **12 V barrel and/or 5 V USB-PD** stepped down to the core rail;
the high current lives on the 0.71 V *output* side, so input protection carries the smaller *input*
current. `TRIP` (over-temp/over-voltage) is a **1.2 V-domain** ASIC output; `Tj` is 50–85 °C operating,
**115 °C absolute max** — a stalled fan on an exposed-die FCLGA is a real hazard.

## 3.1 Input power protection

The structurally cheapest fix is **one keyed input** — it eliminates both reverse-polarity and back-feed
with zero parts (what most open boards do). Add a reverse block on any barrel; only add ORing if two live
inputs can genuinely coexist.

| An effective approach leverages… | …with these example parts | …in this manner | When to pick it |
|---|---|---|---|
| A **series Schottky reverse-block** | Diodes **B560C** (60 V/5 A) [ds](https://datasheet.octopart.com/B560C-13-F-Diodes-Inc.-datasheet-530186.pdf) | Blocks reverse instantly; one part, no gate logic; big hand-solderable tab | Low-current input where ~1 W of `Vf·I` loss is acceptable and you want zero logic risk. **HashBed does this (B560C).** |
| A **P-FET reverse-block** (lower loss) | AOS **AO3401A** (−30 V/−4 A) [ds](https://www.aosmd.com/res/datasheets/AO3401A.pdf) | Drop is `I·RDS` (tens of mV, ~10× less than Schottky); trivial to solder; up-size the FET above 4 A | Cost/efficiency-sensitive single input without an ORing controller. |
| An **ideal-diode controller + N-FET** | TI **LM74700-Q1** (20 mV drop, 3.2–65 V) [ds](https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf) · Diodes **AP74701Q** (adds −33 V VDS clamp) [ds](https://www.diodes.com/datasheet/download/AP74701Q.pdf) | Near-zero loss, scales to any current via the FET; one controller per input leg also ORs two rails | High-current input where a Schottky's watts are unacceptable, or a true barrel-**and**-USB-PD OR. |

For a 5 V-only, low-current OR, TI **LM66100** (integrated ideal diode, SC-70) [ds](https://www.ti.com/lit/ds/symlink/lm66100.pdf)
is the compact pick; ADI **LTC4359** only if the board must survive large negative/HV input faults.
*(A BM1362 sibling shipped a reverse-polarity add for a missing block — `256foundation/emberone00-pcb#37`.)*

## 3.2 Transient / ESD protection

Protect **power nodes and data lines** — hot-plug/cable-fault transients hit VBUS/VIN/CC, not just D±
(leaving power nodes bare is the documented `emberone00-pcb#28/#31` miss). Pick a TVS whose reverse
standoff sits *above* the node's normal max and whose clamp stays under the downstream part's abs-max.

- **5 V VBUS / positive rail:** Littelfuse **SMAJ5.0A** (5 V standoff, ~9.2 V clamp, 400 W) [ds](https://www.littelfuse.com/assetdocs/tvs-diodes-smaj-datasheet?assetguid=13c2a823-03b8-4d1f-9ddc-9b44670aed9d) — scale the `SMAJxxA` number to the rail (SMAJ12A for a 12 V barrel). *HashBed uses an SMAJ6.0A on VBUS.*
- **USB-C CC1/CC2:** Nexperia **PESD5V0X1BT** (ultra-low cap, 9 kV) [ds](https://www.nexperia.com/product/PESD5V0X1BT) — one per CC pin.
- **USB 2.0 D± + VBUS in one part:** ST **USBLC6-2SC6** (3.5 pF, IEC 61000-4-2 L4) [ds](https://www.st.com/resource/en/datasheet/usblc6-2.pdf).

## 3.3 Rail supervision

**Ecosystem finding:** *none* of the surveyed open BZM2 boards carry a dedicated voltage-supervisor or
watchdog IC — rail health is inferred from the regulator **PGOOD** pin and host telemetry, which is exactly
the host-polling-only gap `emberone00-pcb#56` illustrates. A proven, cheap hardening step adds independent
hardware detection:

- **PGOOD → host GPIO** — free baseline; always wire it out, don't leave it floating.
- **A nanopower supervisor** — TI **TPS3839** (150 nA, factory-trimmed) [product](https://www.ti.com/product/TPS3839) or Diodes **APX803S** (0.1 V threshold steps, open-drain wire-OR) [ds](https://www.diodes.com/datasheet/download/APX803S.pdf) — an independent "is this rail up?" flag per rail.
- **A supervisor + watchdog** — TI **TPS3823** (WDI + manual reset) [ds](https://www.ti.com/lit/ds/symlink/tps3823.pdf) — catches a *hung host/bridge*, not just a low rail.

Wire supervisor/PGOOD outputs into (a) a host interrupt and (b) — for the core rail — the same hardware
enable-gate used for `TRIP` (§3.4), so a collapsed rail can also drop the core.

## 3.4 Thermal safety

Two layers: **monitoring + fan control with tach/stall detection**, and a **hardware `TRIP` → enable-gate
cut** so a fault contains the core rail even if firmware is hung.

**Temperature sense & fan control** — a proven approach leverages an SMBus fan controller with tach:
Microchip **EMC2101** (PWM + tach + internal/external temp in one QFN-10) [ds](https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/EMC2101-Data-Sheet-DS20006703.pdf),
or **EMC2302/2305** (RPM-based, explicit **stall alert**, 2/5 fans — *bitaxeBonanza uses the EMC2302,
libreboard the EMC2305*) paired with a TI **TMP1075** temp sensor (±0.25 °C, ALERT pin — *EmberOne and
HashBed use the TMP1075*) [ds](https://www.ti.com/lit/ds/symlink/tmp1075.pdf). The minimal path is a
discrete tach level-shift (BSS138 + Zener) into a host counter — *what bitaxeBIRDS does*. Either way,
**the tach must be wired**; prefer a hardware alert-on-stall over pure host polling.

**Hardware TRIP interlock** — the reference-grade move makes `TRIP` (or a sensor ALERT, or a supervisor
fault) **force the core-buck ENABLE low in hardware**:

- **Logic AND into EN** — a 1.2 V-capable single AND gate (e.g. **SN74AXC1G08**, respecting the ≈1.5 V
  ceiling): `EN = host_enable AND (NOT TRIP)`. Deterministic, sub-µs, keeps host control while adding a
  hardware veto. **The default interlock.**
- **Comparator / SR-latch cut** — latches EN off until a deliberate clear, so a momentary over-temp stays
  tripped instead of oscillating.
- **Sensor ALERT → EN** — reuse the TMP1075/EMC2101 ALERT, wire-OR'd to the same gate, for a second
  over-temp cut independent of the ASIC's TRIP.
- **Fail-safe default-off** — pull-downs on core-buck EN and `NRST` so the rail is off / ASIC in reset at
  power-up (the open bridge firmware defaults `NRST` low). Baseline; combine with a gate above.

---

# Quick-pick summary

**A cost-conscious, hand-solderable single-ASIC board** (the Satoshi-Starter class):

| Function | First pick | Why |
|---|---|---|
| Level translation | `SN74AXC1T45` ×N (SOT-23) or `SN74AXC4T774` | 0.65 V floor = real 1.2 V margin; leaded for hand assembly |
| 9-bit UART | RP2040 PIO (`9N1`) or XR21V1414 | Proven; MCU folds in fan/telemetry, or a no-firmware USB bridge |
| 50 MHz clock | `SX3M50` native 1.2 V, direct-drive | Fewest parts, no translator/ceiling risk |
| VCORE | DS4432U → LM25119 FB (cheap) **or** TPS546D24A (integrated) | Software-rampable; the two proven open-board routes |
| Remote sense | On-chip diff (VRM) or Kelvin the FB to the land | Reject IR drop at 0.71 V |
| Telemetry | INA260 (≤15 A) / INA228 (full 30 A) / PMBus readback | Feeds the stack-imbalance loop |
| 1.2 V VDDIO | TPS7A20 or TLV757P (fixed 1.2 V) | Accurate reference under 1.3 V abs-max |
| Input protection | 1 keyed input + B560C or AO3401A reverse-block | Structurally avoids reverse/back-feed |
| ESD | SMAJ5.0A (VBUS) + USBLC6-2 (data) | Protect power nodes, not just data |
| Supervision | PGOOD wired + TPS3839 (optional) | Independent rail detection — a gap in every open board |
| Thermal | EMC2101 (temp+fan+tach) + AND-gate TRIP→EN | Stall detection + hardware fault cut |

**Scale up for multi-ASIC / higher current:** stack TPS546D24A phases (or LTC3886 + bigger FETs);
daisy-chain the clock AC-coupled; reference every strap to its *own* stack ground; INA228/external shunt or
per-phase sensing for current.

---

## Related documents in this repository

- [Board Design Guide](bzm2-board-design-guide.md) — the *patterns and pitfalls* this catalog implements.
- [Hardware Implementations Survey](bzm2-hardware-implementations.md) — the open boards cited here as
  corroboration, and their maturity.
- [Integration Guide](blockscale-asic-integration-guide.md) / [UART Protocol Reference](blockscale-uart-protocol-reference.md) /
  [Pinout Reference](bzm2-pinout-reference.md) — the electrical facts each requirement is drawn from.

---

*Clean-room provenance: this guidance is assembled from public component datasheets (linked inline), the
public open-source BZM2 board ecosystem (bitaxeBIRDS, bitaxeBonanza, HashBed, EmberOne, libreboard,
bonanza-bridge-fw), and general mixed-signal design practice. It reproduces no proprietary or
vendor-confidential design, part selection, net name, or value. Every choice is a designer's starting
point to adapt and verify against the ASIC's own datasheet, not a schematic to copy.*
