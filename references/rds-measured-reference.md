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
