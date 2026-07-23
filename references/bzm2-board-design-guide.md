# BZM2 Board Design Guide — effective patterns and common pitfalls

A practical companion to the reference docs in this repository. Where the
[Integration Guide](blockscale-asic-integration-guide.md), [Pinout Reference](bzm2-pinout-reference.md),
and [UART Protocol Reference](blockscale-uart-protocol-reference.md) tell you *what* the ASIC needs,
this guide captures *how* to build a board around it that is likely to work on first power-up.

The guidance here is synthesized from the **open BZM2 board ecosystem** — the community hardware
designs and firmware built around this ASIC — and from general mixed-signal design practice. Where a
pattern is illustrated by a specific open design or a publicly documented issue, it is cited so you
can verify it. Electrical limits referenced below come from the [Integration Guide](blockscale-asic-integration-guide.md)'s
IO/electrical tables.

> **Scope note.** This is general design guidance. Characterize every limit on your own board before
> committing it; the ASIC's own datasheet governs.

---

## 1. The host ↔ ASIC digital interface lives at 1.2 V — treat it as the #1 risk

Every host-facing digital signal (UART, reset, trip, reference clock) is on the ASIC's **1.2 V IO
domain**, while a typical host (USB bridge, MCU, oscillator) is 3.3 V. Getting this boundary wrong is
the single most common way to end up with a dead-on-arrival board.

**Do:**
- Cross the boundary with a **real IC level translator**, powered with **VCCA on the ASIC's 1.2 V IO
  rail** and VCCB on the host 3.3 V rail. The 1.2 V IO rail makes a clean local reference for the
  translator's low side.
- Pick a translator family that **actually supports a 1.2 V VCC.** The `SN74AXC` family (≈0.65 V VCC
  floor) has real margin at 1.2 V. The very common `SN74LVC1T45` has a **1.65 V floor and cannot run
  at 1.2 V** — this is the classic mis-pick. `AVC`-class parts work but sit near their 1.2 V floor.
- Match direction per signal (UART is bidirectional across two lines; reset/trip/clock are
  unidirectional). A per-bit-direction translator (e.g. `SN74AXC4T774`) fits the mixed set cleanly.

**Don't:**
- **Don't use a resistive divider** to drop 3.3 V into a 1.2 V pad. It over-drives the pad against the
  **`VDDIO + 0.3 V` ≈ 1.5 V input ceiling**, DC-loads the source, and — for anything fast — rounds the
  edges. If you *must* stay passive, an AC-couple + bias network is defensible; a resistor divider is
  not.
- **Don't get RX/TX direction backwards.** A transposed UART translator is fatal and invisible to a
  level check — it just doesn't communicate. Verify TX-in vs RX-out against the pinout/ball map before
  fab. *(A community single-ASIC board shipped exactly this and was non-functional until re-spun:
  [bitaxeorg/bitaxeBonanza#3](https://github.com/bitaxeorg/bitaxeBonanza/issues/3).)*

## 2. Reference clock — deliver 50 MHz *in the 1.2 V domain*

`REFCLKIN` is a 1.2 V input. The clean, low-risk answer is a **native 1.2 V-supply oscillator** driving
it directly — no divider, no translator, no source loading. Stocked 1.2 V 50 MHz parts exist and are
used across the open BZM2 boards. If you keep a 3.3 V oscillator, translate it with a 50 MHz-capable
level translator (which also unloads the oscillator). Never feed the clock through a resistor divider —
it exceeds the 1.5 V input ceiling and degrades the edge. Series-terminate the clock trace.

**Multi-ASIC:** daisy-chain `REFCLKOUT → REFCLKIN` down the chain, **AC-coupled** so the series-stack
ground offsets between ASICs don't fight the DC level.

## 3. VDDIO (1.2 V IO rail) — tie *both* pads

The ASIC has **two VDDIO pads**. Tie **both** to the 1.2 V IO rail — do not leave the second pad on
local decoupling alone (see the [Pinout Reference](bzm2-pinout-reference.md)). The current is small, so
a thin trace / single via suffices; the value is a solid IO reference and no risk of an under-supplied
IO bank. Label the rail net so a later schematic edit cannot silently orphan one pad.

## 4. VCORE / VDD_HASH — make it *controllable*, not just adjustable

`VDD_HASH` is a tunable rail (nominal 0.71 V, window ≈0.6–0.81 V) that the host is expected to **ramp in
software under voltage-sensor feedback**, and to trim per-part. That has three implications most first
designs miss:

- **Use a digitally-controllable regulator**, not a fixed trim pot. A PMBus/I²C buck, or a small DAC
  injected into a conventional buck's feedback node, lets firmware set and ramp VCORE. The open
  multi-ASIC boards do this (PMBus bucks; a current-DAC-into-feedback approach on one design). A fixed
  divider + panel pot can't perform the ramp and usually can't even reach the full window.
- **Add remote / Kelvin sense.** At 0.71 V, a few tens of mV of IR drop is several percent of the rail.
  Sense at the ASIC land, not at the regulator.
- **Provide current sense + telemetry** (a sense resistor + INA/ADC, or the regulator's own PMBus
  readback). The host needs live rail data for the stack-imbalance safety loop the ASIC's voltage
  sensor is designed to feed.

Size the copper and vias for the rail as a **plane + via-farm** problem (budget for ~30 A headroom on a
maxed single ASIC), not a trace.

## 5. The other ASIC rails

- **VDDINT (stack mid-reference, ~0.355 V):** the ASIC brings out two VDDINT pads. Keep their
  **decoupling separate** — give each its own bypass bank rather than commoning them — and treat the
  node as a low-impedance power node close to the package (open multi-ASIC boards keep the two on
  distinct bypass islands).
- **VDDPLL:** decouple locally per the pinout reference.
- **VDD75 (0.75 V):** normally generated by the ASIC's on-chip LDO — local decoupling is sufficient; an
  external supply is only needed to bypass the on-chip path.

## 6. Decoupling & PDN

- Put decoupling **close to the package.** If a heatsink owns the top side (it will — the die is
  thermally active the moment hash rails come up), place the **cap bank on the bottom side** under the
  FCLGA land field.
- `VDD_HASH` is the plane-and-via problem above; the IO/PLL/INT rails want tight local ceramics.
- All-ceramic output on the core buck is fine; mind DC-bias derating (a ceramic at its rated voltage can
  lose more than half its capacitance — spec the rating against the actual rail voltage, and confirm it
  in the BOM, not just the schematic value field).

## 7. Power sequencing & reset — fail safe

- **Hold the ASIC in reset and the core rail off until the host is ready.** A pull-down on `NRST` (reset
  asserted) and on the core-buck enable (off) at power-up is the correct default; firmware releases them
  deliberately. An open-source bridge firmware defaults reset low for exactly this reason
  ([bitaxeorg/bonanza-bridge-fw](https://github.com/bitaxeorg/bonanza-bridge-fw)).
- Bring the **control/IO rails up before** applying hash-stack voltage.
- Beware host-driver side effects on reset: a UART bridge's DTR line wired to `NRST` will reset the ASIC
  every time a serial port opens — make that deliberate or isolate it.

## 8. Input power & protection

- **Prefer a single keyed input** (barrel or terminal). It structurally avoids reverse-polarity and
  source-backfeed problems.
- If you support **two inputs** (e.g. USB-PD *and* a barrel), you must OR them — an ideal-diode ORing
  controller (near-zero drop) beats series Schottkys (which dissipate ~1 W+ at load). A barrel in
  parallel with a live PD path will back-drive the adapter otherwise.
- **Add a series reverse-block** on any barrel input (a reversed plug otherwise shorts every input
  device). An open BM1362 sibling shipped a reverse-polarity add specifically for this
  ([256foundation/emberone00-pcb#37](https://github.com/256foundation/emberone00-pcb/issues/37)).
- **TVS the power and data ports** (VBUS, VIN, CC, D±), not just the data lines — hot-plug/cable-fault
  transients hit power nodes too.
- **Respect the input regulator's VIN abs-max.** Silk-label the accepted input-voltage range; a wall
  brick above the regulator limit silently bricks the aux rails.

## 9. Thermal safety

- The `TRIP` output signals over-temperature/over-voltage. **Gate the core-rail enable with TRIP in
  hardware** — do not rely on host software polling alone to contain a destructive fault.
- **Wire the fan tachometer.** An exposed-die FCLGA has a low thermal mass; an undetected fan stall on a
  115 °C-abs-max die is a real hazard.
- Assume continuous high leakage/heat once stack voltage is present; plan the heatsink and airflow
  accordingly.

## 10. The 9-bit UART host interface

The ASIC's UART is **9-bit** (the 9th bit is an address/data mode flag, *not* a parity bit — see the
[UART Protocol Reference](blockscale-uart-protocol-reference.md)). Choose a host UART path with **native
9-bit support**:

- A **hardware USB-UART bridge** with a true 9-bit/multidrop mode, or
- An **MCU whose UART/PIO can do 9-bit natively** (e.g. an RP2040 PIO implementation — used by the open
  bridge firmware; STM32-class parts also qualify), or an FPGA.

**Do not** try to abuse a general MCU's parity bit as the 9th bit — it is asynchronous to the data
register and fails at the required data rates. A community board hit exactly this wall and had to change
controllers ([bitaxeorg/bitaxeBonanza#4](https://github.com/bitaxeorg/bitaxeBonanza/issues/4)). Document
the bridge's mode-register/driver setup as part of bring-up.

## 11. PINSEL, straps, and orientation

- **PINSEL** selects the ASIC's pin-mux orientation. Strap it to the ASIC's **local VSS** for the mode
  you want (see the ball map). In a series-stacked multi-ASIC layout, reference each strap to that
  chip's *own* ground domain — a strap tied to the wrong stack ground is a per-chip failure
  ([bitaxeorg/bitaxeBIRDS#7](https://github.com/bitaxeorg/bitaxeBIRDS/issues/7)).
- Terminate genuinely floating high-impedance inputs; add JTAG pulls + VTref if JTAG is brought out.

---

## Common failure modes to avoid (distilled from the open ecosystem)

Every item below is a mistake a real open BZM2/related design made and documented publicly — cheap to
avoid in schematic, expensive to find on the bench.

| Failure | Avoid it by | Public reference |
|---|---|---|
| Level-shifter RX/TX backwards → DOA | verify UART direction vs the ball map before fab | bitaxeBonanza#3 |
| MCU can't do 9-bit UART → can't talk to the chip | native-9-bit bridge/MCU/PIO, not a parity hack | bitaxeBonanza#4 |
| 3.3 V clock over-driving the 1.2 V pad | 1.2 V oscillator or a translator, never a divider | (1.5 V ceiling; general) |
| VRM feedback/strap wrong → wrong VCORE | re-derive every regulator strap at BOM review | bitaxeBonanza#1 |
| Can't tune/ramp VCORE | digitally-controllable VRM (PMBus / DAC-into-FB) | emberone#20 |
| Regulator shuts down above its VIN limit | clamp/limit VIN; silk the input range | emberone#1 |
| No reverse-polarity protection | series reverse-block / ideal-diode ORing | emberone#37 |
| Unprotected power nodes | TVS on VBUS/VIN/CC, not just data | emberone#28/#31 |
| Floating high-Z pin suspected in a boot failure | pull/terminate no-pull inputs "for good measure" | libreboard#26 |
| Package too small to hand-solder | 0603-min passives; up-size translators/LDOs | bitaxeBIRDS#6 |
| Under-rated / unspecified caps + DC-bias derating | pin cap voltage ratings in the BOM for the real rail | (general) |

## First-article bring-up checklist

- Test points on the UART/reset/trip/clock nets and every rail.
- **Scope every 1.2 V pad's signal level** on the first board — confirm nothing exceeds the ≈1.5 V
  ceiling and that logic levels are valid.
- Confirm UART **direction** (host-TX → ASIC-RX, ASIC-TX → host-RX).
- Bring up with the core rail *off*, enumerate the chip, verify the 9-bit link and a NOOP before
  applying hash voltage.
- Ramp VCORE in software under voltage-sensor feedback; watch stack balance.
- ERC-clean the schematic so it can serve as a pre-fab regression gate.
