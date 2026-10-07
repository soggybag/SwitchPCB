# 3PDT Footswitch Board (SwitchPCB v2)

A small board that solders onto a standard 3PDT stomp switch and gives every Super-Freq pedal the same true-bypass wiring. It's a KiCad 10 update of the Eagle `SwitchPCB` (2022).

## Circuit (same as the Eagle board)

- **Engaged:** input jack → IN, OUT → output jack, and LED cathode → GND (LED on).
- **Bypassed:**
  - input jack → output jack, through the BYPASS link;
  - the circuit's IN is shorted to GND (stops oscillation and pops).

## Pads (seen from inside the box, left to right)

| Pad | Net | Goes to |
|---|---|---|
| IJ | input jack tip | input jack |
| IN | circuit input | pedal header pin 1 |
| LED | LED cathode | pedal header pin 2 |
| G | ground | pedal header pin 3 |
| OUT | circuit output | pedal header pin 4 |
| OJ | output jack tip | output jack |

- **Ribbon:** the middle four pads line up with the pedal boards' 1×4 header (IN / LED / GND / OUT, 2.54 mm), so a 4-way ribbon runs straight with no twist.
- **Jack grounds:** wire them to the pedal board's IG/OG pads, as before.

## Build

1. Push the switch's lugs through the board from the **unprinted side**. The printed side, with the labels, faces into the box. This matches the pedal boards, where the front faces inside.
2. Solder the nine lugs.
3. Wire the pads.

## Changes from the Eagle version

- **Lug slots:** the lug holes are now **plated slots, 2.8 × 1.3 mm** (the PedalDivision size), on the switch's lug grid: 5.3 mm between poles × 4.7 mm between throws, as in your Eagle `3PDT_PCM`. The pads are 3.8 × 2.4 mm. The slots hold the switch square while you solder. (Eagle v1 used 2.8 mm round holes.)
- **Which row is "engaged" changed.** It's now the row nearest the pads. Electrically it's the same switch, but every track now runs straight on the front copper: no vias, nothing on the back.
- **Pad order is reversed from v1, on purpose.** The old Eagle pedal boards had their pots on the top layer, so from inside the box their pads read OUT · G · LED · IN, which matched the v1 switch board (you confirmed the ribbon ran straight on 2026-10-06). The new KiCad pedal boards (UF1, UF3 v1.1, Hyper, Rat, Trem v2, Penfold) put the pots on the back, so from inside they read **IN · LED · GND · OUT**. v2 matches them.
  - **v2 switch + new KiCad pedal board:** straight ribbon.
  - **v1 switch + new KiCad pedal board:** fit the v1 board **upside down**, with the lugs through from its printed side. The pads are plated through, and the order then matches. Or cross the four wires.
  - **v2 switch + old Eagle pedal board:** the same: flip it, or cross the wires.
- **Board size:** 17.15 × 20.95 mm (same as before).
- **Tracks:** 0.5 mm.
- **Labels:** IJ / IN / LED / G / OUT / OJ, plus "SUPER-FREQ 3PDT v2".
- **3D model:** the blue 3PDT model is attached.

## Files

- `production/SwitchPCB.zip`: Gerbers + drill files for JLCPCB (no assembly; everything is hand-soldered).
- `scripts/`:
  - `build_switchpcb.py`: writes the schematic and library;
  - `buildpcb_switchpcb.py`: places the board;
  - `route_switchpcb.py`: adds the hand-placed tracks.

  Don't re-run them after editing the board in KiCad; they overwrite it.
