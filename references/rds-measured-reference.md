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
[Voltage-Stack Topology Examples](bzm2-voltage-stack-examples.md). This page holds the observations: board identity,
heat, rails and level deviation, power feeds, and two behaviours of a hashing chain (live clock changes and the error
ratio at a fixed start). Each section ends its claims at what was observed, and says what was not measured.

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

Not yet established: whether a domain this far from its board's mean costs anything in errors, and the deviation at
the stock firmware's higher profiles.

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
  and then 1.038 % on a later run, and board 0 read 1.075 % and then 1.985 %. A single reading at a fixed threshold is
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
