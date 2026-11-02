# RDS measured reference

## Purpose

This page holds what has been **measured** on an RDS (one unit, `bonanza`: three hashboards of 100 BZM2 ASICs on
one shared supply rail), under the stock firmware and under the Mujina reference firmware. The structure and the
failure reasoning for the RDS are in [Voltage-Stack Topology Examples](bzm2-voltage-stack-examples.md). The chip-level
findings from the same runs are in the [Integration Guide](blockscale-asic-integration-guide.md).

Every figure names the test it came from: a case id (`MJ-...`, `RDS-...`) and a run id. A run id is the run's start
time in UTC, sometimes prefixed with the unit, case and arm. A figure from one unit is evidence about that unit. It
is not a rating, and it is not a performance claim for either firmware.

Stock-profile runs are RDS-PROF-01's eleven clean holds, each about an hour at the stock firmware's own operating
point (r4 held four hours):

| profile (stock strategy) | runs |
|---|---|
| low (power saving) | `r1-20261021T063723Z`, `r2-20261021T172423Z` |
| regular (balanced) | `r3-20261021T191033Z`, `r4-20261021T212909Z` |
| high (high performance) | `r5-20261022T023030Z`, `r5-20261022T140005Z`, `r6-20261022T160430Z` |
| hp2 (high performance 2) | `r7-20261022T210432Z`, `r7-20261023T035144Z`, `r7-20261026T015213Z`, `r8-20261026T042113Z` |

## Board identity

`[BZM2-RDS-001]` `[BZM2-RDS-002]`

**Software board N, chain `tty9bit<N>0` and board-controller bus `/dev/i2c-(N+2)` are the same hashboard, for N = 0,
1, 2, and the stock firmware's "board N" is that same board.** No index is inverted. Two independent measurements
settle it:

- **The board-controller bus.** During stock run `r7-20261022T210432Z`, the stock firmware's own per-board outlet
  temperature print was compared with the outlet temperature read over each bus at the nearest time (74 pairs per
  combination). The median absolute difference is 0.00 C when the stock board number equals the bus's board number,
  and 1.00 to 3.00 C for every other pairing. The inlet sensors do not separate boards 1 and 2; the outlets do.
- **The chain, by thermal fingerprint.** The pattern of a board's 100 per-ASIC die temperatures is a property of its
  silicon and its place on the board, and it repeats from run to run. Stock run `r3-20261021T191033Z`'s settled
  pattern for each stock board was correlated with each Mujina chain in three MJ-TUNE-02 arms. Pearson r is 0.958 to
  0.998 when the numbers match and 0.455 to 0.673 when they do not, even with the matching chain held at a different
  clock. The hottest ASIC ids repeat as well: the stock firmware's hottest on board 2 are ASICs 37, 43 and 72, and
  Mujina's on chain `tty9bit20` are 37, 43 and 63.

A per-ASIC thermal fingerprint is a cheap way to match one firmware's board numbering to another's without trusting
either one's labels.

**Not measured:** which chassis slot, label or airflow position each software index is
([#42](https://github.com/Blockscale-Solutions/bzm2-hwref/issues/42)).

## Heat by board

`[BZM2-RDS-003]`

**Board 2 runs hottest on its dies and board 1 hottest at its outlet, under both firmwares.** In all eleven stock
holds board 2 had the hottest die and the hottest die mean, and board 1 had the hottest outlet and the largest outlet
rise over its inlet. Mujina agrees whenever board 2 runs at the stored map: its hottest die was on board 2 in four of
five MJ-TUNE-02 arms. The fifth (`bonanza.MJ-TUNE-02.v17550b2.20261030T011051Z`) held board 2 near 800 MHz, and board 0
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

| board | quantity | per MHz | sd | per W of wall power | sd |
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
  in 104 s (`r8-20261026T042113Z`).
- **The stock firmware reports a hot board more often.** In hp2 runs `r7-20261022T210432Z` and
  `r7-20261023T035144Z`, board 2's report interval fell from about 100 s to about 30 s (and as low as 4 s between some
  pairs) once its hottest die printed 105. Board 2's hottest die printed 104 to 106 for about nineteen minutes of
  `r7-20261022T210432Z` and nothing stopped.

The stock firmware's die readings and Mujina's agree in pattern. An offset between them is not measured
([#46](https://github.com/Blockscale-Solutions/bzm2-hwref/issues/46)).

## Rails and level deviation

`[BZM2-RDS-004]` `[BZM2-RDS-005]`

**One setpoint, three rails close to it.** With the shared supply set to `17,550 mV`, the three board rails read 17.46
to 17.83 V for the whole of run `bonanza.MJ-TUNE-02.v17550b0.20261029T071354Z`, board for board alike. Because the
three boards share that one setpoint (see
[Why voltage cannot be trimmed per board](bzm2-voltage-stack-examples.md#why-voltage-cannot-be-trimmed-per-board)),
a test that changes the setpoint changes all three boards, and cannot isolate one board's voltage.

**Level deviation** here means: take every internal-domain voltage (the two halves of every ASIC) on one board, and
report the largest distance of any one of them from their mean. It is the board's worst level imbalance, in volts.

At a uniform clock (every ASIC at the same frequency, no ASIC being moved), under the Mujina reference firmware at
`17,550 mV`, in MJ-TUNE-02:

| run | board | rounds read | level deviation |
|---|---|---|---|
| `bonanza.MJ-TUNE-02.v17550b0.20261029T135804Z` | 0 | 220 | at most 0.0125 V |
| `bonanza.MJ-TUNE-02.v17550b1.20261029T172540Z`, before any ASIC moved | 1 | 221 | mean 0.0115 V, at most 0.0129 V |
| `bonanza.MJ-TUNE-02.v17550b2.20261030T011051Z` | 2 | 213 | 0.0104 to 0.0183 V, mean 0.0178 V |

**Moving single ASICs off the common clock widens it.** In `bonanza.MJ-TUNE-02.v17550b1.20261029T172540Z`, one ASIC
was raised from 800 to 1,075 MHz in steps while its neighbours stayed at 800. The deviation went from about 0.0114 V
at 900 MHz to 0.0157 V at 1,000 MHz and 0.0206 V at 1,075 MHz, and 0.0252 V the round after. With a few ASICs raised,
it averaged 0.0243 V over the next 1,590 rounds and reached 0.0287 V at most. The widest halves were the raised ASICs
and their immediate neighbours. So a per-ASIC climb makes the imbalance it is measured by, and a ceiling fitted to
boards at one common clock will be crossed by the climb itself.

**Moving the whole board at once moves it much less.** In MJ-TUNE-03 (arms `bonanza.MJ-TUNE-03.p0.20261028T231202Z`
and `bonanza.MJ-TUNE-03.p1.20261029T043249Z`), board 0 was moved from its stored map (mean 1,163.7 MHz) by whole-board
steps and back. The largest half-voltage excursion from its pre-move mean, per step size, was:

| board-wide step | largest excursion |
|---|---|
| 25 MHz | 1.898 mV |
| 50 MHz | 3.658 mV |
| 75 MHz (applied as 50 then 25) | 3.218 mV |
| 100 MHz (applied as 50 then 50) | 6.479 mV |

After the 50 and 75 MHz moves the levels had not returned to their pre-move band by the end of the hold, at least 82 s
and 149 s after the first write.

### What a record-only guard showed: the same arm, refusing and recording

`[BZM2-RDS-008]`

A per-ASIC climb makes the imbalance it is measured by (above), so a guard that refuses a climb step while the level is
over a threshold will stop the climb it is measuring. MJ-TUNE-02 ran the same board and arm twice under the Mujina
reference firmware, once with the guard **refusing** upward steps whenever a round's level deviation was over its
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
  more errors, or whether the refusing runs' threshold is too low. That correlation is the open part of
  [#44](https://github.com/Blockscale-Solutions/bzm2-hwref/issues/44), and none of these runs reached an exit, so none
  produced a finished map to compare.

Not yet established: whether a domain this far from its board's mean costs anything in errors, and the deviation at
the stock firmware's higher profiles ([#44](https://github.com/Blockscale-Solutions/bzm2-hwref/issues/44)).

## Power feeds

`[BZM2-RDS-006]` `[BZM2-RDS-007]`

**Two supplies, both needed.** The RDS takes two power supplies, each on its own cord. They are not interchangeable:
by the owner's observation on this unit (2026-10-20), supply A alone powers the control board but the machine does not
start, and supply B is needed for the hashboards. Measured at the two cords (each on its own inlet-metered PDU), the
running load is shared about evenly between them: over the arm window of RDS-PROF-01 run `r1-20261021T063723Z`, cord
A carried 1.76 kWh and cord B 1.84 kWh. Size each feed for the whole machine's share with margin, and gate on each
cord's current, not on the total.

**Idle draw.** With both supplies on and nothing running, the RDS drew about 28 W at the wall (cord A 5.3 W, cord B
22.8 W), measured over a 10-minute stage on 2026-10-21 against an off stage on the same cords (RDS-PROF-01 stage
baselines, before run `r1-20261021T063723Z`).

**Power factor** at the wall was 0.994 over the hold of `r1-20261021T063723Z` (low profile).

**The supply's own power report is not the wall.** Over the clean RDS-PROF-01 holds, wall power (non-RDS load
removed) divided by the supply's reported input power was:

| profile | runs | wall / supply-reported input |
|---|---|---|
| low | `r1-20261021T063723Z`, `r2-20261021T172423Z` | 0.922 - 0.925 |
| regular | `r3-20261021T191033Z` | 0.981 |
| high | `r5-20261022T023030Z`, `r5-20261022T140005Z`, `r6-20261022T160430Z` | 0.998 - 1.003 |
| hp2 | `r7-20261022T210432Z`, `r7-20261023T035144Z`, `r7-20261026T015213Z`, `r8-20261026T042113Z` | 1.013 - 1.017 |

So the supply's report reads about 8 % above an independent AC meter at light load, and slightly below it at heavy
load. Above the wall cannot be physical for an input meter, so treat the supply's figure as an instrument with an
error that depends on load, and use a wall meter for any energy figure. (`r4-20261021T212909Z` is left out: its supply
record covers only 82 % of its hold.) The supply's DC output fields, read at the scale and pairing we believe they have,
give DC out over wall AC of 0.889 to 0.915 across the same holds; that pairing is not yet independently confirmed
([#45](https://github.com/Blockscale-Solutions/bzm2-hwref/issues/45)).

**Power follows one board's clock.** Moving board 0 alone by whole-board steps, with the other two boards at their
stored maps, changed the supply's AC input by +0.345 W per MHz of board 0's mean frequency (95 % interval 0.079 to
0.612, four holds) in MJ-TUNE-03 (analysis `bonanza.MJ-TUNE-03.p1.20261029T043249Z`).

## Operational guidance: close order and kernel fault

`[BZM2-RDS-009]`

The stock image's driver for the chain UART ttys (`/dev/tty9bit00`, `10`, `20`, kernel 4.9.78) can fault the kernel when
a chain tty is closed for the last time. This is a property of the platform, not of any one program, and it is tracked as
[#54](https://github.com/Blockscale-Solutions/bzm2-hwref/issues/54), which holds the full description and the way to
close the gap. In short:

- **How often.** Three faults in 266 boots' kernel logs: the stock mining daemon exiting (MJ-HASH-07, 2026-09-24), the
  Mujina miner at a normal stop (MJ-TUNE-03 arm `p0`, 2026-10-28) and the Mujina miner at its stop in
  `bonanza.MJ-TUNE-02.v17550s2.20261030T195256Z` (2026-10-30). Different chains, two different programs, different builds.
  The timing and traffic before the close match the closes that passed.
- **Why it hurts.** The faulting thread dies holding a kernel-wide tty lock, so any later final close of a chain tty
  blocks for good in uninterruptible sleep. The closing process cannot exit, and TERM and KILL do nothing. Only a reboot
  or power cycle clears it.
- **What it did to a stop.** In the 2026-10-30 run the miner released its chain ports before powering the boards off, so
  the fault in the first close left boards 1 and 2 powered. They went dark only through the board controllers' own
  loss-of-heartbeat shutdown, about 88 s after their last heartbeat. The process stayed alive past KILL.

Guidance, ours:

1. **Power the boards off, and verify them dark, before closing the chain ports.** Never the other way round. The
   Mujina reference firmware's stop now does this, with a bounded wait for each board and for each port release. That
   change has not been exercised against a fault.
2. **Do not block a stop on a close returning.** Bound each wait, log which port and thread a close was on, and go on.
3. **A process that survives KILL after closing these ports is a kernel fault, not a live power owner.** Treat the
   tty lock as held and the unit as needing a power cycle; do not keep sending it TERM and KILL, and do not read it as
   proof the boards are still being driven. Prove dark from the supply and the board controllers instead.
4. **Reboot between sessions that open and close the chain ports,** and before the next run after any such fault check
   that the kernel is untainted and no chain tty is held.

Not established: the fault rate per close, and the behaviour once the driver is fixed
([#54](https://github.com/Blockscale-Solutions/bzm2-hwref/issues/54)).

## Stock supply, fan power and the wall's overhead

`[BZM2-RDS-010]` `[BZM2-RDS-011]` `[BZM2-RDS-012]`

This section models the gap between what the RDS draws at the wall and what its supply delivers to the boards, from the
eleven clean RDS-PROF-01 holds (run ids in the table at the top of this page). It is derived from the raw per-minute
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

Per run, over the last 1,800 s of each hold (`r4-20261021T212909Z` over the last 1,800 s of the hold its supply stream
covers):

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
  steadily with load, from 0.9489 (`r1-20261021T063723Z`) to 0.9294 (`r7-20261023T035144Z`) across the holds.
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
the report divided by the wall reads 1.0798 and 1.0824 at the low profile (`r1-20261021T063723Z`, `r2-20261021T172423Z`),
1.0172 and 1.0110 at regular (`r3-20261021T191033Z`, `r4-20261021T212909Z`), 0.9972 to 0.9987 at high, and 0.9830 to 0.9855
at hp2 (`r7-20261023T035144Z` to `r8-20261026T042113Z`). Per minute the report minus the wall runs from -102 to +322 W; every
positive minute is at or below 4,374 W of wall power and every negative one at or above 4,045 W. This is the same finding
as [Power feeds](#power-feeds), stated over a shorter span (the ratios there are wall over report, over the whole hold,
and agree to within the span). The report is steady from run to run, so a trip derived in its own units can use it. It must
not be read as wall power, and a watts-per-MHz slope taken on it is not the slope at the wall. Our captures show the stock
firmware's own printed wall power and conversion efficiency are built on this field, and they read 89.6 to 93.8 % where the
measured DC/wall is 0.89 to 0.91 above.

![The supply's input report minus the wall, against the wall](../drawings/lab/stock-power/fig-supply-input-report.svg)

Caption: RDS-PROF-01 clean holds `r1-20261021T063723Z` to `r8-20261026T042113Z`, per-minute points. A test-reported
comparison of two instruments, not a rating.

**Not established:** per-board power (the board controller's current field returns the rail voltage, not a current), the
fan law's exponent, the control board's draw apart from the supply's fixed loss, any second witness for the supply's
current sensor, and the supply's DC output pairing ([#45](https://github.com/Blockscale-Solutions/bzm2-hwref/issues/45)).
No stock run held a clock at a second voltage, so none of the above says what the overhead does at a clock off the four
stock maps.
