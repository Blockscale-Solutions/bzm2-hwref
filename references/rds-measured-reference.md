# RDS reference measurements

> **Observed data, not specification.** Everything on this page was measured on one RDS unit (three hashboards of 100
> BZM2 ASICs on one shared supply rail), under the stock firmware and under the Mujina reference firmware. A figure
> from one unit is evidence about that unit. It is not a rating of the ASIC and not a performance claim for either
> firmware. The normative text (what the ASIC requires and how to design for it) is in the
> [Integration Guide](blockscale-asic-integration-guide.md), the
> [UART and TDM Protocol Reference](blockscale-uart-protocol-reference.md) and the
> [Board Design Guide](bzm2-board-design-guide.md).

## About these measurements

The structure of the RDS and the reasoning about its failure modes are in
[Voltage-Stack Topology Examples](bzm2-voltage-stack-examples.md). This page holds the observations. Each section ends
its claims at what was observed, and says what was not measured.

Runs are referred to by a short label in the text (for example *hp2-1*). The labels resolve in the tables below. A run
id is the run's start time in UTC, sometimes prefixed with the case, firmware and board.

### Stock-firmware holds

Eleven clean holds, each about an hour at the stock firmware's own operating point (*regular-2* held four hours):

| profile (stock strategy) | holds (label: run id) |
|---|---|
| low (power saving) | low-1: `r1-20261021T063723Z`, low-2: `r2-20261021T172423Z` |
| regular (balanced) | regular-1: `r3-20261021T191033Z`, regular-2: `r4-20261021T212909Z` |
| high (high performance) | high-1: `r5-20261022T023030Z`, high-2: `r5-20261022T140005Z`, high-3: `r6-20261022T160430Z` |
| hp2 (high performance 2) | hp2-1: `r7-20261022T210432Z`, hp2-2: `r7-20261023T035144Z`, hp2-3: `r7-20261026T015213Z`, hp2-4: `r8-20261026T042113Z` |

### Mujina reference-firmware runs

| label | board | run id |
|---|---|---|
| tune-b0-1 | 0 | `bonanza.MJ-TUNE-02.v17550b0.20261029T071354Z` |
| tune-b0-2 | 0 | `bonanza.MJ-TUNE-02.v17550b0.20261029T135804Z` |
| tune-b1 | 1 | `bonanza.MJ-TUNE-02.v17550b1.20261029T172540Z` |
| tune-b2 | 2 | `bonanza.MJ-TUNE-02.v17550b2.20261030T011051Z` |
| board-step-1 | 0 | `bonanza.MJ-TUNE-03.p0.20261028T231202Z` |
| board-step-2 | 0 | `bonanza.MJ-TUNE-03.p1.20261029T043249Z` |
| repeat-1 | 2 | `bonanza.MJ-TUNE-02.v17550r2.20261030T112640Z` |
| repeat-2 | 2 | `bonanza.MJ-TUNE-02.v17550r2.20261030T160549Z` |
| repeat-3 | 2 | `bonanza.MJ-TUNE-02.v17550r2.20261030T174010Z` |
| repeat-4 | 2 | `bonanza.MJ-TUNE-02.v17550s2.20261030T195256Z` |
| record-b0 | 0 | `bonanza.MJ-TUNE-02.v17550r0.20261030T131846Z` |
| record-b1 | 1 | `bonanza.MJ-TUNE-02.v17550r1.20261030T144115Z` |
| tune-b0-later | 0 | `20261030T021147Z` |
| tune-b1-later | 1 | `20261030T035225Z` |

### Stock-firmware wire capture

| label | board | run id |
|---|---|---|
| wire-1 | 0 | `MJ-OBS-01` `20260916T052158Z` |

## Engine grid and IDs on a stock chain

`[BZM2-ENG-006]`

In *wire-1*, the chain UART of one RDS board was recorded at 5 Mbaud while the stock firmware's work was still
returning results: about 120,000 result frames from 100 devices. Decoding each result frame's engine identifier
([Engine identifier layout](blockscale-uart-protocol-reference.md#engine-identifier-layout)):

- **236 distinct positions answered**, pooled over the 100 devices, on a grid of rows `0` to `19` and columns `0` to `11`.
- **The four holes never answered**: (row `0`, col `4`), (row `0`, col `5`), (row `19`, col `5`), (row `19`, col `11`).
  No frame carried a coordinate outside the grid.
- **Results were spread across the positions**: 423 to 587 frames per position, pooled.

Per device, between 231 and 236 positions answered in the window, which is what about 1,200 frames per device spread
over 236 positions gives; the capture does not show whether a position missing on one device was idle or absent.

Not established: the population on other boards or other parts, and whether any part has holes elsewhere.

## Board identity

`[BZM2-RDS-001]` `[BZM2-RDS-002]`

**For N = 0, 1, 2, software board N, its chain UART, its board-controller bus and the stock firmware's "board N" are the same hashboard.** No index is inverted. Two independent measurements
settle it:

- **The board-controller bus.** During stock hold hp2-1, the stock firmware's own per-board outlet
  temperature print was compared with the outlet temperature read over each bus at the nearest time (74 pairs per
  combination). The median absolute difference is 0.00 C when the stock board number equals the bus's board number,
  and 1.00 to 3.00 C for every other pairing. The inlet sensors do not separate boards 1 and 2; the outlets do.
- **The chain, by thermal fingerprint.** The pattern of a board's 100 per-ASIC die temperatures is a property of its
  silicon and its place on the board, and it repeats from run to run. The steady-state pattern of each stock board in hold regular-1
  was correlated with each Mujina chain in three of the Mujina runs. Pearson r is 0.958 to
  0.998 when the numbers match and 0.455 to 0.673 when they do not, even with the matching chain held at a different
  clock. The hottest ASIC ids repeat as well: the stock firmware's hottest on board 2 are ASICs 37, 43 and 72, and
  Mujina's on chain 2 are 37, 43 and 63.

A per-ASIC thermal fingerprint is a cheap way to match one firmware's board numbering to another's without trusting
either one's labels.

**Not measured:** which chassis slot, label or airflow position each software index is.

## Heat by board

`[BZM2-RDS-003]`

**Board 2 runs hottest on its dies and board 1 hottest at its outlet, under both firmwares.** In all eleven stock
holds board 2 had the hottest die and the hottest die mean, and board 1 had the hottest outlet and the largest outlet
rise over its inlet. Mujina agrees whenever board 2 runs at the stored map: its hottest die was on board 2 in four of
five of the Mujina runs. The fifth (tune-b2) held board 2 near 800 MHz, and board 0
was hottest.

Per board, over the last 2,400 s of each stock hold. Frequency is the stock firmware's own per-board print after its
calibration (median). Wall power is the whole machine at the two supply inlets, with the non-RDS load on those
circuits removed. Inlet is the board's own controller inlet sensor at launch (median of the first 60 s). All
temperatures are the on-die sensor reading or the board-controller sensors, in C. None is a junction temperature
(see the Integration Guide, [Temperature thresholds](blockscale-asic-integration-guide.md#temperature-thresholds)).

| profile | runs | wall power (W) | board | frequency (MHz) | hottest die − inlet | die mean − inlet | outlet − inlet |
|---|---|---|---|---|---|---|---|
| low | 2 | 2888 - 2891 | 0 | 1013.4 | 49.5 - 50.0 | 43.1 - 43.6 | 17.4 - 17.6 |
| | | | 1 | 1011.9 | 46.5 - 47.5 | 40.3 - 40.4 | 19.9 - 20.0 |
| | | | 2 | 1010.1 | 51.5 - 52.0 | 44.2 - 44.7 | 17.1 - 17.3 |
| regular | 2 | 3574 - 3627 | 0 | 1174.6 | 55.0 - 57.0 | 49.1 - 50.7 | 18.2 - 19.7 |
| | | | 1 | 1165.6 | 52.5 - 54.5 | 45.8 - 46.7 | 21.0 - 22.4 |
| | | | 2 | 1160.9 | 58.0 - 59.5 | 50.6 - 51.4 | 18.6 - 19.9 |
| high | 3 | 4367 - 4529 | 0 | 1318.1 - 1333.3 | 65.5 - 67.0 | 56.7 - 58.8 | 21.2 - 22.1 |
| | | | 1 | 1321.1 - 1328.9 | 61.5 - 64.0 | 53.7 - 55.1 | 24.9 - 26.1 |
| | | | 2 | 1325.4 - 1326.8 | 69.0 - 70.0 | 59.6 - 61.0 | 22.3 - 22.8 |
| hp2 | 4 | 5039 - 5166 | 0 | 1437.7 - 1442.9 | 75.0 - 78.0 | 65.8 - 68.5 | 24.9 - 25.2 |
| | | | 1 | 1441.5 - 1444.3 | 71.5 - 75.0 | 62.0 - 64.3 | 28.6 - 29.3 |
| | | | 2 | 1440.3 - 1447.5 | 81.0 - 85.0 | 69.4 - 73.0 | 25.5 - 26.4 |

The hottest die on board 2, printed by the stock firmware (whole degrees), was 71 at low, 82 at regular, 95 at high
and 106 at hp2, at launch inlets of about 19 to 25 C.

Straight-line fits per board over the eleven holds (y = a + b·x, residual standard deviation in C):

| board | quantity | slope (C per MHz) | residual sd (C) | slope (C per W of wall power) | residual sd (C) |
|---|---|---|---|---|---|
| 0 | hottest die − inlet | 0.0648 | 2.12 | 0.01241 | 1.49 |
| 1 | hottest die − inlet | 0.0615 | 2.11 | 0.01196 | 1.61 |
| 2 | hottest die − inlet | 0.0727 | 2.72 | 0.01430 | 2.18 |
| 0 | outlet − inlet | 0.0182 | 0.88 | 0.00350 | 0.75 |
| 1 | outlet − inlet | 0.0216 | 0.83 | 0.00419 | 0.67 |
| 2 | outlet − inlet | 0.0206 | 0.69 | 0.00404 | 0.57 |

How far the fits can be used:

- **Interpolation only.** They hold inside 1,010 to 1,447 MHz, on the four stock maps at their own voltages, at
  launch inlets of 19 to 25 C, under the stock fan control. A board run near 800 MHz among neighbours at the stock map
  sat 4 to 10 C above the line's extrapolation, because its neighbours' air heats it.
- **Four points per board, not eleven.** The holds sit at four operating points. The slope's uncertainty is
  understated by treating them as eleven.
- **Frequency and voltage move together** across the stock profiles, so the fits cannot separate them. Against
  power the residuals are about 25 to 30 % smaller, and the frequency fit's residuals are curved (positive at low and
  hp2, negative between), which says heat follows power, not clock alone.
- **The power axis is the whole machine's.** No per-board power is measured.

Two further stock observations from the same holds:

- **The rise rate does not change with heat.** In the last 40 minutes of every hold, no ASIC's printed temperature
  rose by more than one degree between consecutive reports (about 90 to 100 s apart), from low to hp2. Heat moves the
  level by about 35 C and leaves the rate where it was. Only the arrival of load after calibration is fast: up to 9 C
  in 104 s (hp2-4).
- **The stock firmware reports a hot board more often.** In holds hp2-1 and
  hp2-2, board 2's report interval fell from about 100 s to about 30 s (and as low as 4 s between some
  pairs) once its hottest die printed 105. Board 2's hottest die printed 104 to 106 for about nineteen minutes of
  hp2-1 and nothing stopped.

The stock firmware's die readings and Mujina's agree in pattern. An offset between them is not measured.

## Rails and level deviation

`[BZM2-RDS-004]` `[BZM2-RDS-005]`

**One setpoint, three rails close to it.** With the shared supply set to `17,550 mV`, the three board rails read 17.46
to 17.83 V for the whole of run tune-b0-1, board for board alike. Because the
three boards share that one setpoint (see
[Why voltage cannot be trimmed per board](bzm2-voltage-stack-examples.md#why-voltage-cannot-be-trimmed-per-board)),
a test that changes the setpoint changes all three boards, and cannot isolate one board's voltage.

**Level deviation** here means: take every internal-domain voltage (the two halves of every ASIC) on one board, and
report the largest distance of any one of them from their mean. It is the board's worst level imbalance, in volts.

At a uniform clock (every ASIC at the same frequency, no ASIC being moved), under the Mujina reference firmware at
`17,550 mV`:

| run | board | rounds read | level deviation |
|---|---|---|---|
| tune-b0-2 | 0 | 220 | at most 0.0125 V |
| tune-b1, before any ASIC moved | 1 | 221 | mean 0.0115 V, at most 0.0129 V |
| tune-b2 | 2 | 213 | 0.0104 to 0.0183 V, mean 0.0178 V |

**Moving single ASICs off the common clock widens it.** In tune-b1, one ASIC
was raised from 800 to 1,075 MHz in steps while its neighbours stayed at 800. The deviation went from about 0.0114 V
at 900 MHz to 0.0157 V at 1,000 MHz and 0.0206 V at 1,075 MHz, and 0.0252 V the round after. With a few ASICs raised,
it averaged 0.0243 V over the next 1,590 rounds and reached 0.0287 V at most. The widest halves were the raised ASICs
and their immediate neighbours. So a per-ASIC climb makes the imbalance it is measured by, and a ceiling fitted to
boards at one common clock will be crossed by the climb itself.

**Moving the whole board at once moves it much less.** In runs board-step-1 and board-step-2, board 0 was moved from its stored map (mean 1,163.7 MHz) by whole-board
steps and back. The largest half-voltage excursion from its pre-move mean, per step size, was:

| board-wide step | largest excursion |
|---|---|
| 25 MHz | 1.898 mV |
| 50 MHz | 3.658 mV |
| 75 MHz (applied as 50 then 25) | 3.218 mV |
| 100 MHz (applied as 50 then 50) | 6.479 mV |

After the 50 and 75 MHz moves the levels had not returned to their pre-move band by the end of the hold, at least 82 s
and 149 s after the first write.

### A level guard that refuses against one that only records

`[BZM2-RDS-008]`

A per-ASIC climb makes the imbalance it is measured by (above), so a guard that refuses a climb step while the level is
over a threshold will stop the climb it is measuring. The same board and calibration configuration ran twice under the
Mujina reference firmware, once with the guard **refusing** upward steps whenever a round's level deviation was over its
threshold (0.0345 V), and once **recording** the same rounds and moving nothing. Each pair is the same board, the
same start (every ASIC at 800 MHz, `17,550 mV`) and the same step-one mode; the run's other conditions differ a little
(start inlet 19.3 to 20.8 C, and for board 2 the two runs are about two hours apart). One pair per board is evidence about
this unit on that night, not a rate.

| board | run | guard | rounds read | level deviation range (mean) | rounds over 0.0345 V | upward steps refused for the guard | upward steps issued | ASICs ended above 800 MHz |
|---|---|---|---|---|---|---|---|---|
| 1 | `bonanza.MJ-TUNE-02.v17550m1.20261030T081756Z` | refuse | 1,850 | 0.009312 to 0.03864 V (0.030313 V) | 430 (23.2 %) | 164, on 86 ASICs | 4 | 6 |
| 1 | `bonanza.MJ-TUNE-02.v17550r1.20261030T144115Z` | record | 1,553 | 0.010940 to 0.054939 V (0.038842 V) | 1,263 (81.3 %) | 0 | 73 | 76 |
| 2 | `bonanza.MJ-TUNE-02.v17550m2.20261030T092911Z` | refuse | 1,712 | 0.007299 to 0.040352 V (0.028755 V) | 539 (31.5 %) | 94, on 57 ASICs | 18 | 18 |
| 2 | `bonanza.MJ-TUNE-02.v17550r2.20261030T112640Z` | record | 1,511 | 0.010624 to 0.060539 V (0.034780 V) | 842 (55.7 %) | 0 | 68 | 70 |

What the pairs show, and what they do not:

- **Readings above the threshold are routine once the climb runs.** The level is the board's worst domain's distance
  from the board mean. Board 2 before its climb read 0.007299 to 0.011884 V in the refusing run, and 0.010624 to
  0.024033 V in the recording run; it rose with the climb in both.
- **With the guard refusing, the climb was held for about a quarter to a third of the reads and mostly stopped.** The
  refusing runs breached from about 1,125 s (board 1) and 1,456 s (board 2) into the run and issued 4 and 18 upward steps.
  Board 1's long breach ran about 1,057 s and board 2's 1,143 s.
- **With the guard only recording, the climb proceeded though breaches were recorded,** and the level reached higher: its
  maximum was 0.054939 V on board 1 and 0.060539 V on board 2, against 0.03864 V and 0.040352 V when refusing. In both
  recording runs 59 of 73 and 53 of 68 upward steps were issued in a round that was over the threshold.
- **The per-ASIC verdicts kept working.** In the recording run of board 1 one ASIC was stepped down once, after it
  returned 10 valid and 748 wrong results at 1,075 MHz; one step down was issued in each recording run. The climb was
  limited by errors, not by the level.
- **Not shown: that a high level costs anything.** These runs record the level and the climb. They do not tie a round's
  level to the error ratios of the ASICs in it, so they cannot say whether a domain 0.05 V from its board's mean returns
  more errors, or whether the refusing runs' threshold is too low. That correlation is not yet measured, and none of these runs reached an exit, so none produced a finished map
  to compare.

### Error cost of the level deviation at the 800 MHz floor

`[BZM2-RDS-013]`

The recording runs and the repeats (record-b0, record-b1, repeat-1 to repeat-4) dwelled every ASIC at 800 MHz and
recorded the level each round. Each dwell's error ratio (wrong results over valid plus wrong results) was joined to the
level deviation of the round with the same time, over 1,065 dwells in 298 rounds, with a level deviation of 0.0122 to
0.0587 V (414 dwells over the 0.0345 V threshold). The fit weights each dwell by its result count, takes one
intercept per run and clusters its standard errors by round.

| design | cost per 0.01 V of level deviation | 95 % interval | dwells | runs |
|---|---|---|---|---|
| level, run intercepts | +0.0001 | -0.0017 to +0.0019 | 1,065 | record-b0, record-b1, repeat-1, repeat-2, repeat-3, repeat-4 |
| level, hottest die of the round also controlled | -0.0012 | -0.0028 to +0.0005 | 1,065 | record-b0, record-b1, repeat-1, repeat-2, repeat-3, repeat-4 |

Dwells per run: record-b0 196, record-b1 188, repeat-1 195, repeat-2 97, repeat-3 195, repeat-4 194. The boards are 0
(record-b0), 1 (record-b1) and 2 (the others).

- **No cost is established at the floor.** Both intervals include zero. At 95 % any real cost is under about 0.002 in
  error ratio per 0.01 V, in either direction.
- **Not controlled:** the individual ASIC. Each ASIC has about two dwells, so an ASIC effect cannot be estimated, and a
  few episodic ASICs carry most of the errors.
- **The cost at a climbed clock has not been measured.** Every dwell in these runs is at the one starting clock, and
  the record holds no dwells at a higher clock. Whether a
  domain far from its board's mean costs errors when its ASIC runs faster, where margins are smaller, remains open.

Not yet established: the cost at a climbed clock, and the deviation at the stock firmware's higher profiles.

## Power feeds

`[BZM2-RDS-006]` `[BZM2-RDS-007]`

**Two supplies, both needed.** The RDS takes two power supplies, each on its own cord. They are not interchangeable:
as observed on this unit (2026-10-20), supply A alone powers the control board but the machine does not
start, and supply B is needed for the hashboards. Measured at the two cords (each on its own inlet-metered PDU), the
running load is shared about evenly between them: over the window of hold low-1, cord
A carried 1.76 kWh and cord B 1.84 kWh. Size each feed for the whole machine's share with margin, and gate on each
cord's current, not on the total.

**Idle draw.** With both supplies on and nothing running, the RDS drew about 28 W at the wall (cord A 5.3 W, cord B
22.8 W), measured over a 10-minute stage on 2026-10-21 against an off stage on the same cords (measured before hold low-1).

**Power factor** at the wall was 0.994 over hold low-1 (low profile).

**The supply's own power report is not the wall.** Over the clean stock holds, wall power (non-RDS load
removed) divided by the supply's reported input power was:

| profile | runs | wall / supply-reported input |
|---|---|---|
| low | low-1, low-2 | 0.922 - 0.925 |
| regular | regular-1 | 0.981 |
| high | high-1, high-2, high-3 | 0.998 - 1.003 |
| hp2 | hp2-1, hp2-2, hp2-3, hp2-4 | 1.013 - 1.017 |

So the supply's report reads about 8 % above an independent AC meter at light load, and slightly below it at heavy
load. Above the wall cannot be physical for an input meter, so treat the supply's figure as an instrument with an
error that depends on load, and use a wall meter for any energy figure. (regular-2 is left out: its supply
record covers only 82 % of its hold.) The supply's DC output fields, read at the scale and pairing they are believed to have,
give DC out over wall AC of 0.889 to 0.915 across the same holds; that pairing is not yet independently confirmed.

**Power follows one board's clock.** Moving board 0 alone by whole-board steps, with the other two boards at their
stored maps, changed the supply's AC input by +0.345 W per MHz of board 0's mean frequency (95 % interval 0.079 to
0.612, four holds) in run board-step-2.

## Operational guidance: close order and kernel fault

`[BZM2-RDS-009]`

The stock image's driver for the three chain UART ttys (kernel 4.9.78) can fault the kernel when a chain tty is closed for
the last time. This is a property of the platform, not of any one program. In short:

- **How often.** Three faults in 266 boots' kernel logs: the stock mining daemon exiting (a stock-firmware session,
  2026-09-24), the Mujina miner at a normal stop (*board-step-1*, 2026-10-28) and the Mujina miner at its stop in
  *repeat-4* (2026-10-30). Different chains, two different programs, different builds.
  The timing and traffic before the close match the closes that passed.
- **Why it hurts.** The faulting thread dies holding a kernel-wide tty lock, so any later final close of a chain tty
  blocks for good in uninterruptible sleep. The closing process cannot exit, and TERM and KILL do nothing. Only a reboot
  or power cycle clears it.
- **What it did to a stop.** In the 2026-10-30 run the miner released its chain ports before powering the boards off, so
  the fault in the first close left boards 1 and 2 powered. They went dark only through the board controllers' own
  loss-of-heartbeat shutdown, about 88 s after their last heartbeat. The process stayed alive past KILL.

Guidance:

1. **Power the boards off, and verify them dark, before closing the chain ports.** Never the other way round. The
   Mujina reference firmware's stop now does this, with a bounded wait for each board and for each port release. That
   change has not been exercised against a fault.
2. **Do not block a stop on a close returning.** Bound each wait, log which port and thread a close was on, and go on.
3. **A process that survives KILL after closing these ports is a kernel fault, not a live power owner.** Treat the
   tty lock as held and the unit as needing a power cycle; do not keep sending it TERM and KILL, and do not read it as
   proof the boards are still being driven. Prove dark from the supply and the board controllers instead.
4. **Reboot between sessions that open and close the chain ports,** and before the next run after any such fault check
   that the kernel is untainted and no chain tty is held.

Not established: the fault rate per close, and the behaviour once the driver is fixed.

## Stock supply, fan power and the wall's overhead

`[BZM2-RDS-010]` `[BZM2-RDS-011]` `[BZM2-RDS-012]`

This section models the gap between what the RDS draws at the wall and what its supply delivers to the boards, from the
eleven clean stock holds (run ids in the table at the top of this page). It is derived from the raw per-minute
rows of those holds, and every figure below belongs to the runs named with it. None is a rating of the unit or of either
firmware.

**Instruments, kept apart.** The wall is both PDU cords' own minute log, less the non-RDS load on those circuits
(measured with the machine off). The DC figure is the supply's main-output current times its main-output voltage, paired
within 1 s. That is **one instrument**: no second meter has checked the supply's current sensor. The supply's AC-input
report is a third series, treated as an instrument under test. The fit uses whole minutes with both cords, the supply and
the fans all covered: 881 minutes offered, 848 kept after dropping minutes where clock error alone could move the figure
by more than the fit's own residual (calibration ramps fall out this way).

**The overhead is a smooth curve in current, with a fan term on top.** Overhead here is wall power minus the supply's DC
output. Fitted over 134 to 251 A of main current as

    overhead = c0 + c1 I + c2 I^2 + fan_full (rpm / rpm_full)^3

the result is c0 = 170.6 W, c1 = -1.633 W/A, c2 = 0.0096 W/A^2 and fan_full = 208.4 W at 6,759 rpm (the chassis fans at
full duty), with a residual standard deviation of 4.66 W over the 848 kept minutes. Leaving each run out in turn moves
fan_full between 195.9 and 210.5 W. The three current coefficients are a local fit: they are not separate physical
losses and mean nothing outside 134 to 251 A. The supply fixed loss and the control board's draw sit together in c0 and
are not separated; that needs the control board measured alone with the main output off.

**The fan exponent is not identified, so the fan watts are a range.** Fan shaft power should follow the cube of speed, but
the data do not pick the exponent. The same minutes fitted with exponent 2.0, 2.5, 3.0 and 3.5 give fan_full of 287, 240,
208 and 186 W with residual standard deviations of 4.674, 4.647, 4.657 and 4.700 W. Using only the five runs whose fan duty
moved within the hold gives 215.3 W. A dark sweep (boards off, fans stepped through several duties) would settle it.

Per run, over the last 1,800 s of each hold (*regular-2* over the last 1,800 s of the hold its supply stream covers):

| run | profile | wall (W) | supply DC output (W) | overhead (W) | fan duty | fan speed (rpm) | fans, modelled (W) | DC / wall |
|---|---|---|---|---|---|---|---|---|
| `r1-20261021T063723Z` | low | 2903 | 2648 | 255 | 0.727 | 5400 | 106 | 0.9122 |
| `r2-20261021T172423Z` | low | 2904 | 2649 | 255 | 0.725 | 5386 | 106 | 0.9123 |
| `r3-20261021T191033Z` | regular | 3586 | 3242 | 344 | 0.829 | 6021 | 147 | 0.9041 |
| `r4-20261021T212909Z` | regular | 3651 | 3248 | 402 | 0.972 | 6712 | 204 | 0.8898 |
| `r5-20261022T023030Z` | high | 4544 | 4045 | 499 | 1.000 | 6764 | 209 | 0.8902 |
| `r5-20261022T140005Z` | high | 4396 | 3918 | 478 | 1.000 | 6753 | 208 | 0.8913 |
| `r6-20261022T160430Z` | high | 4420 | 3942 | 478 | 1.000 | 6755 | 208 | 0.8918 |
| `r7-20261022T210432Z` | hp2 | 5182 | 4609 | 573 | 1.000 | 6754 | 208 | 0.8894 |
| `r7-20261023T035144Z` | hp2 | 5200 | 4626 | 574 | 1.000 | 6743 | 207 | 0.8896 |
| `r7-20261026T015213Z` | hp2 | 5076 | 4522 | 554 | 1.000 | 6757 | 208 | 0.8909 |
| `r8-20261026T042113Z` | hp2 | 5096 | 4537 | 560 | 1.000 | 6756 | 208 | 0.8902 |

What the table and the fit say:

- **The measured DC/wall ratio steps down near the regular profile because the fans go to full, not because the supply
  gets worse.** The stock fan law runs the fans between about 0.73 and 0.97 duty in the low and regular holds and pins
  them at full in the high and hp2 holds. With the modelled fan power counted as output, the supply's conversion falls
  steadily with load, from 0.9489 (*low-1*) to 0.9294 (*hp2-2*) across the holds.
- **Each extra DC watt costs more wall watts at high current.** With the fans held, the marginal supply loss runs from
  0.077 to 0.172 W of wall power per extra DC watt across the current range, rising with current.
- **Heat enters the overhead too.** Adding the supply's own ambient field as a term (1.876 W per count over the 9-count
  span the kept minutes cover, 16.9 W across the span, 15.8 to 18.7 W leaving a run out) lowers the residual standard
  deviation from 4.66 to 3.54 W. The field's unit is unresolved and it moves together with time, the room and the supply
  fan, so this is a covariate, not a measured temperature coefficient.

![Wall overhead against main current, per minute, shaded by chassis fan speed, with the model at full fans and with the fan term removed](../drawings/lab/stock-power/fig-wall-overhead.svg)

Caption: RDS-PROF-01 clean holds `r1-20261021T063723Z` to `r8-20261026T042113Z` (the eleven runs above); per-minute points,
the fit above, and its residuals. A test-reported fit over those runs, not a rating.

**The supply's AC-input report is not a wall meter, and its error changes sign with load.** Over the same last 1,800 s,
the report divided by the wall reads 1.0798 and 1.0824 at the low profile (*low-1*, *low-2*),
1.0172 and 1.0110 at regular (*regular-1*, *regular-2*), 0.9972 to 0.9987 at high, and 0.9830 to 0.9855 at hp2 (*hp2-2* to
*hp2-4*). Per minute the report minus the wall runs from -102 to +322 W; every
positive minute is at or below 4,374 W of wall power and every negative one at or above 4,045 W. This is the same finding
as [Power feeds](#power-feeds), stated over a shorter span (the ratios there are wall over report, over the whole hold,
and agree to within the span). The report is steady from run to run, so a trip derived in its own units can use it. It must
not be read as wall power, and a watts-per-MHz slope taken on it is not the slope at the wall. Captures of the stock firmware
show that its own printed wall power and conversion efficiency are built on this field, and they read 89.6 to 93.8 % where the
measured DC/wall is 0.89 to 0.91 above.

![The supply's input report minus the wall, against the wall](../drawings/lab/stock-power/fig-supply-input-report.svg)

Caption: RDS-PROF-01 clean holds `r1-20261021T063723Z` to `r8-20261026T042113Z`, per-minute points. A test-reported
comparison of two instruments, not a rating.

**Not established:** per-board power (the board controller's current field returns the rail voltage, not a current), the
fan law's exponent, the control board's draw apart from the supply's fixed loss, any second witness for the supply's
current sensor, and the supply's DC output pairing.
No stock run held a clock at a second voltage, so none of the above says what the overhead does at a clock off the four
stock maps.

## Live clock changes on a hashing chain

`[BZM2-PLL-001]` `[BZM2-PLL-002]`

Measured under the Mujina reference firmware. On one chain, the ASICs' PLLs were moved one ASIC at a time in ramped
steps, while the other two chains hashed at fixed clocks (run tune-b0-1). The guidance that follows from these
observations is in the Integration Guide, [Live clock changes](blockscale-asic-integration-guide.md#live-clock-changes-on-a-hashing-chain).

- **A live move of the feedback divider alone re-locks.** Every one of the 753 sets in that run read back locked.
  Die temperature on the chain stayed flat (mean about 56 C), so the effect below is not thermal.
- **One set costs the host about a second.** A separate run measured an upper bound of 1.06 s per set, including
  the caller's own cadence.
- **While sets run, the whole chain returns result frames with the nonce-valid status bit clear**, not only the ASIC
  being set. The reference firmware reads that bit as bit 3 (`0x08`) of the result status byte. In that run
  the chain carrying the sets returned 38,000 to 130,000 such frames per 20 s poll for as long as the sets went on.
  The two chains with no sets returned about none. The frames stopped on every ASIC of the chain together, about
  40 s after the last set.
- **The host was starving the chain.** In that firmware each set was issued from the same single writer that sends
  work to the chain, so for the length of every set no ASIC on the chain received new work, and a round of 100 sets
  held the chain for most of ten minutes. The frames line up with that hold. Whether the ASIC clears the bit
  because its work ran out, or because of a PLL write elsewhere on the chain, is not separated by these measurements.
- **One unexplained burst.** The two chains with no sets showed one short burst of such frames, at about 915 s into
  the run, with no set running anywhere. Its trigger was not measured.
- **Counting the frames as wrong results distorts an error ratio.** Counted as wrong, they turned that run's
  start-frequency error figure into 72.7 %, when the chain's own steady-state wrong share with no sets running was 1.0
  to 2.2 %.
- **The quiet period the reference firmware uses is a margin, not a property.** It discards any measurement interval
  that starts within 45 s of the latest PLL set on the chain: the observed 40 s tail plus a margin. It was not measured
  on every board.

Not yet established: whether these parts lock and run cleanly below 800 MHz in a hashing system.

## Error ratio at a fixed start

`[BZM2-CAL-001]` `[BZM2-CAL-002]` `[BZM2-CAL-003]`

Measured under the Mujina reference firmware. In each run every ASIC of one board started at a uniform `800 MHz`, with
the shared supply set to `17,550 mV` (the three board rails read `17.46 - 17.83 V`). The **error ratio** is wrong
results over valid plus wrong, where a wrong result is a nonce that does not meet the target. Frames with the
nonce-valid bit clear are counted apart and left out (see
[Live clock changes on a hashing chain](#live-clock-changes-on-a-hashing-chain)). Each ASIC's figure is its first dwell
at the start.

| run | board | board ratio (all ASICs pooled) | median ASIC | dispersion (chi-squared per degree of freedom) | board ratio without its high-error tail |
|---|---|---|---|---|---|
| tune-b0-2 | 0 | 1.0748 % | 0.5939 % | 11.13 | 0.6548 % |
| tune-b1 | 1 | 0.5168 % | 0.2642 % | 7.92 | 0.3817 % |
| tune-b2 | 2 | 1.1049 % | 0.6614 % | 11.08 | 0.7717 % |

What the table and its reruns show:

- **ASICs on one board do not share one error rate.** A dispersion of 8 to 11 is far above the 1 that a common rate
  would give. The median ASIC on every board is under 0.7 %, while the worst ASICs read 4 to 7 % at the same clock:
  on board 0, ASIC 20 read 6.60 % and ASIC 98 read 5.28 %; on board 2, ASIC 87 read 6.96 % and ASIC 43 read 6.04 %.
- **A board's pooled figure is carried by its tail.** A handful of high-error ASICs set the board number, so a board
  pass or fail at one clock is mostly a statement about those few ASICs.
- **Boards differ even without the tail.** With the high-error ASICs taken out, the boards still read 0.38, 0.65 and
  0.77 %. That is silicon variation between boards, at an identical start.
- **Runs differ.** The same board at the same start gave about twice the figure on a later run: board 1 read 0.5168 %
  (*tune-b1*) and then 1.038 % (*tune-b1-later*), and board 0 read 1.075 % (*tune-b0-2*) and then 1.985 %
  (*tune-b0-later*). A single reading at a fixed threshold is
  not a property of the board.
- **A threshold taken from one board of one run does not transfer.** A start ceiling derived from one board's
  earlier figure failed two of these three boards.
- **The stock firmware starts the same way.** A capture of it enables every PLL at `800 MHz`, measures each board at
  that uniform point, and then moves the whole board up. All three boards went on from that point, at figures the
  stock firmware printed as 0.24 to 0.35 %. The two firmwares' ratios are not directly comparable: at the same board
  and start, the reference firmware's figure ran 2.15 to 3.25 times the stock print, and board 1 was the lowest in
  both.

The calibration guidance that follows from these observations is in the Integration Guide,
[Start-frequency calibration](blockscale-asic-integration-guide.md#start-frequency-calibration).

Not yet established: whether a high-error ASIC improves at a lower clock.

### Error ratio across repeats on one board

`[BZM2-CAL-004]` `[BZM2-CAL-005]`

The table above pools every ASIC of a board into one number. These runs show how far that number can be trusted as a
measurement: four repeats of one start-frequency search on board 2 (*repeat-1* to *repeat-3* with one configuration,
*repeat-4* with its successor), from the same start as above (every ASIC at `800 MHz`, `17,550 mV`). The search's upper
error edge in these runs is `2.671 %`. The interval is the pooled figure's 95 % Wilson interval. An ASIC is individually
over the edge when the lower bound of its own first dwell is above the edge.

| run | board ratio (pooled) | interval | ASICs in the pool | ASICs individually over the edge | what the pooled rule decided |
|---|---|---|---|---|---|
| `bonanza.MJ-TUNE-02.v17550r2.20261030T112640Z` | 2.248 % | 2.144 to 2.357 % | 98 | 14 | under the edge: measured, climb ran |
| `bonanza.MJ-TUNE-02.v17550r2.20261030T160549Z` | 2.870 % | 2.752 to 2.994 % | 97 | 12 | lower bound over the edge: board stopped, no ASIC raised |
| `bonanza.MJ-TUNE-02.v17550r2.20261030T174010Z` | 2.342 % | 2.236 to 2.453 % | 99 | 15 to 18 (two counts in one record differ; not traced) | under the edge: measured, climb ran |
| `bonanza.MJ-TUNE-02.v17550s2.20261030T195256Z` | 2.0546 % | 1.9555 to 2.1585 % | 99 | 14 | under the edge: measured, climb ran |

Board 2 read lower in *tune-b2*, 1.1049 % in the table above. The two configurations are not compared here and the
difference is not explained.

- **The pooled figure repeats badly, and the edge sat between two repeats.** *repeat-1* read 2.248 % and *repeat-2*
  2.870 %, a ratio of 1.28 with disjoint intervals, and `2.671 %` lay between them. One repeat flipped the board from
  measured to stopped. *repeat-3* and *repeat-4* read 2.342 % and 2.0546 %.
- **A few ASICs carry the pool, and they are the same ASICs.** About an eighth of the board was over the edge in every
  run (12 to 18 of 97 to 99), and the board stop in *repeat-2* was decided by those 12. The per-ASIC ranking agrees
  from run to run (Spearman 0.83 to 0.88 between *repeat-1*, *repeat-2* and *repeat-3*), and ASIC 87 read over 10 % in
  all three. The median ASIC read 1.518 %, 1.316 % and 1.318 % in those three runs, far under the edge each time.
- **The median-ASIC rule against the pooled rule.** Judging each ASIC on its own first dwell and stopping the board
  only when more than half of its ASICs are individually over the edge reproduces the pooled rule's call for
  *repeat-1* (measured) and disagrees with it for *repeat-2* (the pooled rule stopped the board; the median rule
  measures it). *repeat-4* ran under the median rule, which measured the board with 14 of 99 over the edge.

The calibration guidance that follows from these runs is in the Integration Guide,
[How far a pooled error ratio can be trusted](blockscale-asic-integration-guide.md#how-far-a-pooled-error-ratio-can-be-trusted).
