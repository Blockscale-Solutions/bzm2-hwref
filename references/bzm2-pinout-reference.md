# BZM2 Pinout And Ball Map Reference

Per-pad reference for the BZM2 `7.5 x 7 mm` exposed-die molded FCLGA package:
`40` peripheral LGA pads plus a `20`-pad inner land field, `60` lands total.
The machine-readable version is [`bzm2-ballmap.csv`](bzm2-ballmap.csv).

Pad-for-pad cross-validated against a working single-ASIC board design.
Numbering runs around the periphery (`1-40`: east column, north row, west
column, south row in top view) then the inner field (`41-60`).

## Rails

| Rail | Pads | Count | Notes |
| --- | --- | --- | --- |
| `VDD` (`VDD_HASH`) | `2-8`, `41-42`, `49-52`, `59-60` | `15` | `0.71 V` nominal; size for `~14 A` stock, `~27 A` maxed - roughly `1-2 A` per pad at the extremes |
| `VSS` | `14`, `21-28`, `35`, `43-48`, `53-58` | `22` | ground return for everything |
| `VDDIO` | `19`, `30` | `2` | `1.2 V` IO rail; **tie both pads to the rail** - do not leave pad `19` on decoupling alone |
| `VDDINT_1` / `VDDINT_2` | `1`, `12` | `2` | internal stack midpoint (~`0.355 V`) brought out for reference/decoupling - **outputs**, not load rails |
| `VDDPLL` (datasheet: `RSVD`) | `13` | `1` | PLL supply decoupling point in the reference designs |
| `VDD_P75` (datasheet: `RSVD`) | `37` | `1` | `0.75 V` backup rail used if the on-chip LDO path is unavailable |

The datasheet marks pads `13` and `37` as reserved; the vendor architecture
material and the reference board designs treat them as `VDDPLL` and `VDD_P75`
respectively. Follow the reference-design treatment (local decoupling; supply
`VDD_P75` only if your design uses the backup-LDO path).

## Clocks

| Pad | Signal | Direction | Spec |
| --- | --- | --- | --- |
| `29` | `REFCLKIN` | Input, no pull | `<= 50 MHz`; `50 MHz` standard |
| `38` | `REFCLKOUT1` | Output | `< 50 MHz`; ASIC-to-ASIC, muxed in debug mode |
| `20` | `REFCLKOUT2` | Input (no pull) | `< 50 MHz`; ASIC-to-ASIC, muxed in debug mode |

Internal PLLs (one per stack) run `16 MHz` to `3200 MHz`, programmable.

## UART, Reset, And Trip (The PINSEL-Muxed Group)

Eight pads carry the UART / reset / trip chain interface. Their function
depends on the `PINSEL` strap (pad `36`), which exists so a wrap-around board
layout can flip the ASIC orientation without crossing traces:

| Pad | Name | `PINSEL = 0` | `PINSEL = 1` | Default state |
| --- | --- | --- | --- | --- |
| `18` | `RX_TRIP_IN` | `RX_IN` | `TRIP_IN` | input, pull-up |
| `16` | `TX_RESET_OUT` | `TX_OUT` | `RESET_OUT` | output |
| `17` | `RESET_TX_IN` | `RESET_IN` (active low) | `TX_IN` | input, pull-up |
| `15` | `TRIP_RX_OUT` | `TRIP_OUT` | `RX_OUT` | high-Z, pull-down |
| `31` | `RX_TRIP_OUT` | `RX_OUT` | `TRIP_OUT` | high-Z, pull-down |
| `32` | `RESET_TX_OUT` | `RESET_OUT` | `TX_OUT` | output |
| `33` | `TX_RESET_IN` | `TX_IN` | `RESET_IN` | input, pull-up |
| `34` | `TRIP_RX_IN` | `TRIP_IN` | `RX_IN` | high-Z, pull-down |

In a `PINSEL = 0` single-ASIC system: host TX -> pad `18`, host RX <- pad
`16`, reset in on pad `17`, trip out on pad `15`; pads `31-34` are the
chain-forwarding side and may be left for chain expansion. IO buffers default
to drive strength code `4'b0100` (programmable per register).

## Boot / Configuration Straps

| Pad | Signal | Internal default | Strap |
| --- | --- | --- | --- |
| `36` | `PINSEL` | pull-up (reads `1`) | strap to `VSS` for `PINSEL = 0` orientation |

`PINSEL` is the only configuration strap. Reset (`RESET_IN`) is active low
with an internal pull-up.

## Test / DFT

Full JTAG TAP on the periphery: `TDO` (`9`), `TDI` (`10`), `TCK` (`11`),
`TMS` (`39`), `TRST` (`40`). Bring these to a header for validation and
debug; the vendor JTAG collateral covers usage.

## Everything Else

- **Differential pairs:** none - all single-ended.
- **Analog pads:** none exposed; temperature and voltage sensing are internal
  and read over UART (`DTS_VS`).
- **NC / RESERVED:** pads `13` and `37` only (see the Rails section).
- **Power-up sequencing:** see the bring-up section of the
  [Integration Guide](blockscale-asic-integration-guide.md) - control rails
  and reference clock before stack voltage, ASICs held in reset, stack ramped
  with sensor feedback.
