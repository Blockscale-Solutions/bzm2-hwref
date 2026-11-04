# Claim register

Every factual claim in this reference that is not self-evident from the text
carries an opaque id, `BZM2-<domain>-<nnn>`. This file is the public half of the
register: the id and the claim, and nothing else.

Each id resolves, in the internal ledger, to a specific document, page or source
locator behind it. That resolution is not public — some of the material is under
NDA. What is public is the guarantee: **if a claim has no id, it should not be
here**, and any id can be challenged and traced to real source material in one
hop by anyone with access to the internal ledger.

`kind` says what sort of evidence stands behind the claim, without saying what
that evidence is:

| kind | meaning |
| --- | --- |
| `vendor-stated` | the vendor's own documentation says it in words |
| `vendor-drawn` | derived from vendor material that demonstrates it rather than stating it — a schematic, a register map, reference source |
| `measured` | observed by us on real hardware |
| `our-inference` | reasoned by us from the above; the weakest kind, and always marked |
| `third-party` | a public source not belonging to the vendor: a datasheet, a standard, or a published open-source implementation |

## Register

| id | claim | kind |
| --- | --- | --- |
| `BZM2-ENG-001` | The engine identifier is a 12-bit row/column pair, row in the low six bits: `engine_id = (col << 6) \| row`. | `third-party` |
| `BZM2-ENG-002` | The register map exposes **one nonce window per addressable engine position**: `StartNonce` and `EndNonce` are written against the same 12-bit engine id as every other work register, and no finer unit appears in the write path. | `third-party` |
| `BZM2-ENG-003` | A device carries **236 addressable engine positions**. | `third-party` |
| `BZM2-ENG-004` | Both nonce window endpoints must be even. | `vendor-stated` |
| `BZM2-ENG-005` | Each addressable position contains **4 engines**, for 944 engines per ASIC. | `vendor-stated` |
| `BZM2-ENG-006` | In a capture of an RDS chain under the stock firmware, result frames from 100 devices came from 236 distinct positions on a grid of rows 0 to 19 and columns 0 to 11, none from (0,4), (0,5), (19,5) or (19,11) and none from outside the grid (MJ-OBS-01, run `20260916T052158Z`). | `measured` |
| `BZM2-ENG-007` | The engine positions sit on a 20-row by 12-column grid with four holes, (row 0, col 4), (0,5), (19,5) and (19,11); rows 0 to 9 are the bottom stack and rows 10 to 19 the top stack, 118 positions each. | `third-party` |
| `BZM2-THM-001` | The BZM2's operating junction temperature range is 50 C to 85 C, with a 115 C absolute maximum. | `vendor-stated` |
| `BZM2-THM-002` | A public board-controller design latches an asserted ASIC trip input as a fault, forces safe outputs (5 V off, ASIC reset held, fan at full), refuses the host's clear while the trip input is asserted, and on a clear returns to safe-off rather than resuming; it has no independent cut of the core rail. | `third-party` |
| `BZM2-THM-003` | The device's thermal and voltage stream carries a thermal trip bit and a voltage trip bit, which a host can act on as they arrive. | `third-party` |
| `BZM2-UART-001` | A broadcast register read is answered by each device under its own `ASIC_ID`, never under `0xFF`: on a 100-device RDS chain one broadcast read drew 99 replies, each under a distinct ID (MJ-OBS-01, run `20260921T144604Z`). | `measured` |
| `BZM2-UART-002` | With the sensor stream at the fastest gap setting used, a 100-device RDS chain at 5 Mbaud cycled in strict ascending round robin at 19,543 frames/s: 5.117 ms per cycle, 51.17 us per slot; gap settings of 100 and 2000 gave about 1,000 and 2,260 frames/s (MJ-OBS-01, runs `20260921T145704Z`, `20260921T150701Z`, `20260921T151652Z`). | `measured` |
| `BZM2-UART-003` | Under the RDS stock firmware, a 100-device chain answers under ASIC IDs 0x00 to 0x63, one per device (MJ-OBS-01, run `20260916T052158Z`). | `measured` |
| `BZM2-UART-004` | Public open-source firmware assigns every device an ID below 0xFA, confirms each by reading `ASIC_ID` back at the new ID, and treats a NOOP reply at 0xFA after numbering as a fault. | `third-party` |
| `BZM2-UART-005` | A device left at 0xFA stays the target of every discovery probe, so a host cannot confirm the chain has ended, and it owns TDM slot 250, so it is heard only in a frame of more than 250 slots. | `our-inference` |
| `BZM2-VS-001` | On a healthy part, `ch2` (midpoint error) is near zero at light load and grows with load current as an IR drop across the internal midpoint path; a `ch2` bound must scale with current. It is not `ch1 − ch0`; the per-ASIC span is `ch0 + ch2 + ch1`. | `our-inference` |
| `BZM2-PWR-001` | In the public 25-point single-ASIC sweep, each row's power is its core voltage times its current and its efficiency is that power over its hash rate, to within rounding: a core-level figure. | `third-party` |
| `BZM2-PWR-002` | On a series stack one current flows through every level, so the rail's voltage times its current is the sum of every ASIC's core power plus the distribution loss; without a current measurement per level the per-ASIC core power is not readable from the rail. | `our-inference` |
| `BZM2-PLL-001` | A live PLL move that changes the feedback divider alone re-locks: 753 of 753 sets read back locked (MJ-TUNE-02, run `bonanza.MJ-TUNE-02.v17550b0.20261029T071354Z`). | `measured` |
| `BZM2-PLL-002` | While PLL sets run on a chain whose only dispatch path they hold, every ASIC on that chain returns result frames with the nonce-valid bit clear; they stop about 40 s after the last set; chains with no sets return about none (same run). | `measured` |
| `BZM2-POOL-001` | The 80-byte block header splits across SHA-256's 64-byte blocks so that version, previous-block hash and the first 28 bytes of the merkle root fall in the first block, and the merkle root's last 4 bytes, ntime, nBits and nonce in the second. | `third-party` |
| `BZM2-POOL-002` | Four writes per engine address, each with its own midstate (base version `0x20000000`, then `0x20004000`, `0x20008000`, `0x20010000`) and one shared merkle residue and ntime, residue, ntime and nBits sent with their header bytes reversed and midstate words least significant byte first, gave pool-accepted shares from every one of the four writes: 15, 14, 14 and 10 of the 53 accepted from one 100-device chain (MJ-TUNE-02, run `20261029T071354Z`). | `measured` |
| `BZM2-POOL-003` | The pool used assigned a 4-byte `extranonce1`, an 8-byte `extranonce2` and the version-rolling mask `0x1fffe000` (MJ-TUNE-02, run `20261029T071354Z`). | `measured` |
| `BZM2-POOL-004` | Each of those 53 accepted shares had exactly one result frame in its chain's receive record; nonce = byte-reverse(nonce field − `0x4c`), the sequence ID's low two bits named the write and its upper six bits the dispatch, and ntime = dispatched ntime + (60 − time field), with offsets of 0 to 22 s among the accepted shares (same run). | `measured` |
| `BZM2-CAL-001` | At a uniform 800 MHz start the ASICs on one RDS board do not share one error rate: dispersion 7.9 to 11.1, median ASIC under 0.7 %, worst ASICs 4 to 7 % (MJ-TUNE-02 runs `20261029T135804Z`, `20261029T172540Z`, `20261030T011051Z`). | `measured` |
| `BZM2-CAL-002` | The same RDS board at the same start gave about twice the error ratio on a later run (MJ-TUNE-02 runs `20261029T172540Z` and `20261030T035225Z`; `20261029T135804Z` and `20261030T021147Z`). | `measured` |
| `BZM2-CAL-003` | The stock RDS firmware enables every PLL at 800 MHz, measures each board there, then moves the whole board up (RDS-CAL-03, run `20261009T174718Z`). | `measured` |
| `BZM2-CAL-004` | The same arm on RDS board 2 read pooled error ratios of 2.248 %, 2.870 %, 2.342 % and 2.0546 % in four runs, and the search's 2.671 % edge lay between the first two (MJ-TUNE-02 runs `20261030T112640Z`, `20261030T160549Z`, `20261030T174010Z`, `20261030T195256Z`). | `measured` |
| `BZM2-CAL-005` | On RDS board 2 at the uniform 800 MHz start, 12 to 18 of 97 to 99 ASICs were individually over the edge in every run, their ranking agreed across runs (Spearman 0.83 to 0.88), and the median ASIC read about 1.3 to 1.5 % (same four runs). | `measured` |
| `BZM2-RDS-001` | On the RDS, software board N, its chain UART, its board-controller bus and the stock firmware's board N are one hashboard: outlet prints match at a median difference of 0.00 C only for equal numbers (RDS-PROF-01, run `r7-20261022T210432Z`). | `measured` |
| `BZM2-RDS-002` | An RDS board's per-ASIC die temperature pattern identifies it across firmwares: Pearson r 0.958 to 0.998 for matching boards, 0.455 to 0.673 otherwise (RDS-PROF-01 run `r3-20261021T191033Z` against three MJ-TUNE-02 arms). | `measured` |
| `BZM2-RDS-003` | On the RDS, board 2 carries the hottest die and die mean, and board 1 the hottest outlet, in all eleven clean RDS-PROF-01 holds. | `measured` |
| `BZM2-RDS-004` | At a 17,550 mV setpoint the three RDS board rails read 17.46 to 17.83 V (MJ-TUNE-02, run `bonanza.MJ-TUNE-02.v17550b0.20261029T071354Z`). | `measured` |
| `BZM2-RDS-005` | An RDS board's level deviation at a uniform clock stays under about 0.018 V, and raising single ASICs off that clock widens it to about 0.025 to 0.029 V, widest at the raised ASICs and their neighbours (MJ-TUNE-02 runs `20261029T135804Z`, `20261029T172540Z`, `20261030T011051Z`). | `measured` |
| `BZM2-RDS-006` | The RDS needs both of its supplies and shares the running load about evenly between their cords: 1.76 and 1.84 kWh over RDS-PROF-01 run `r1-20261021T063723Z`; idle draw about 28 W at the wall. | `measured` |
| `BZM2-RDS-007` | The RDS supply's reported input power reads about 8 % above the wall at the low profile and 1 to 2 % below it at hp2 (wall over reported 0.922 to 1.017 across ten clean RDS-PROF-01 holds). | `measured` |
| `BZM2-RDS-008` | On an RDS board, a level-deviation guard that only recorded let the per-ASIC climb proceed (73 and 68 upward steps, none refused) and the level reach 0.054939 and 0.060539 V, where the same arm with the guard refusing at 0.0345 V issued 4 and 18 and reached 0.03864 and 0.040352 V (MJ-TUNE-02 boards 1 and 2: `20261030T081756Z` against `20261030T144115Z`, `20261030T092911Z` against `20261030T112640Z`). | `measured` |
| `BZM2-RDS-009` | On the RDS stock image, the final close of a chain UART tty faulted the kernel three times in 266 boots' logs, under two different programs, and left the closing process unkillable; in MJ-TUNE-02 run `20261030T195256Z` two boards went dark only through their controllers' loss-of-heartbeat shutdown about 88 s after the last heartbeat. | `measured` |
| `BZM2-RDS-010` | On the RDS, the wall's overhead over the supply's DC output is a smooth curve in main current (134 to 251 A) plus a fan term of about 208 W at full fan speed, residual 4.66 W over 848 minutes; the fan exponent is not identified (fan_full 186 to 287 W for exponents 3.5 to 2.0) (the eleven clean RDS-PROF-01 holds, `r1-20261021T063723Z` to `r8-20261026T042113Z`). | `measured` |
| `BZM2-RDS-011` | The RDS supply's AC-input report divided by the wall read 1.08 at the low profile, about 1.01 to 1.02 at regular, about 1.00 at high and 0.983 to 0.986 at hp2 over the last 1,800 s of the clean RDS-PROF-01 holds; the stock firmware's own wall and conversion prints are built on that field. | `measured` |
| `BZM2-RDS-012` | Counting the fans as output, the RDS supply's modelled conversion falls from 0.9489 to 0.9294 across the clean RDS-PROF-01 holds, and the marginal supply loss runs 0.077 to 0.172 wall W per extra DC W (RDS-PROF-01 runs `r1-20261021T063723Z` to `r8-20261026T042113Z`). | `measured` |
| `BZM2-RDS-013` | Over 1,065 dwells at the 800 MHz floor in six record-only Mujina reference-firmware runs (level deviation 0.0122 to 0.0587 V), the error ratio's change per 0.01 V of level deviation is +0.0001 (95 % interval -0.0017 to +0.0019), and -0.0012 (-0.0028 to +0.0005) with the round's hottest die controlled: no cost is established, and any real cost at the floor is under about 0.002 per 0.01 V; the cost at a climbed clock is unmeasured. | `measured` |

### Public sources for `third-party` rows

`third-party` means the source is public and can be named here, which is the
point of the kind. These resolve to
[`johnny9/ESP-Miner-Bonanza`](https://github.com/johnny9/ESP-Miner-Bonanza)
(GPL-3.0), an independent open-source implementation that drives this part:

| id | where |
| --- | --- |
| `BZM2-ENG-001` | `components/asic/bzm_topology.c:78` - `physical_id = ((uint16_t) column << 6) \| row`; 12-bit width from `components/asic/include/bzm.h:16` (`BZM_MAX_ENGINE_COUNT 4096`) |
| `BZM2-ENG-002` | `components/asic/bzm_work.c:33-34` writes `BZM_REG_START_NONCE` and `BZM_REG_END_NONCE` against `work->engine_id`, the same id used for every other work register at `:30-56`; offsets at `components/asic/bzm_work_registers.h:11-12` |
| `BZM2-ENG-003` | `components/asic/include/bzm_topology.h:16` - `BZM_TOPOLOGY_ENGINE_COUNT 236U`, asserted as a hardware-validity gate at `components/asic/bzm_bringup.c:1031`. Independently corroborated by our own capture: 23,600 work engines across 100 devices |
| `BZM2-ENG-007` | `components/asic/include/bzm_topology.h:13-17` - 20 rows, 12 columns, 236 positions, 118 per stack; holes at `components/asic/bzm_topology.c:52`; stack by row (`row < 10` is the bottom stack) at `components/asic/bzm_topology.c:41-44` |
| `BZM2-THM-003` | `components/asic/bzm_telemetry.c:39` and `:44` decode the thermal and voltage trip bits from the stream; `:124-131` treats them as actionable at once |
| `BZM2-UART-004` | `components/asic/bzm_bringup.c:223-264` probes `0xFA`, writes each ID and reads `ASIC_ID` back at it; `:272-276` reports a reply at `0xFA` after numbering as an extra device |

Rows that resolve to other public repositories:

| id | where |
| --- | --- |
| `BZM2-THM-002` | [`bitaxeorg/bonanza-bridge-fw`](https://github.com/bitaxeorg/bonanza-bridge-fw) (GPL-3.0), `docs/safety-interlock.md:13-23` (safe outputs; no independent core-rail cut), `:44-48` (states and exits), `:94` (clear only with trip low, returns to safe-off), `:121` (trip latches) |
| `BZM2-PWR-001` | [`bitaxeorg/bitaxeBIRDS`](https://github.com/bitaxeorg/bitaxeBIRDS) (CERN-OHL-S-2.0), `doc/specs.md`: voltage times current matches the power column within 0.8 %, and power over hash rate matches the efficiency column within 0.9 %, in all 25 rows |

**`BZM2-ENG-005` deliberately has no public row.** The x4 is vendor-only. Note
that `944` appears in the same open-source firmware and means something else
there - 236 positions x 4 **ASICs on a board**, not 236 positions x 4 engines on
one ASIC. Citing it for the ASIC-internal x4 would be wrong by construction while
every individual number looked right.

`BZM2-POOL-001` resolves to public standards: the Bitcoin block header layout
([developer reference](https://developer.bitcoin.org/reference/block_chain.html#block-headers))
and SHA-256's 512-bit message blocks (FIPS 180-4, section 5.2).
