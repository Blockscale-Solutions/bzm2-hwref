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

**Product collateral:**
- [Product Brief](Product%20Brief%20v012623.pdf)

**Firmware port notes:** the Mujina port engineering notes formerly hosted here have moved
to the firmware repository ([256foundation/mujina#66](https://github.com/256foundation/mujina/pull/66)).

## License
This documentation is licensed under [CC-BY-SA-4.0](LICENSE)
(Creative Commons Attribution-ShareAlike 4.0 International).
