# SwitchPCB v2.0: archived revision

- **Git tag:** `v2.0` (commit `96c7a1a`, 2026-10-16)
- **Tag note:** v2.0: first JLC order of the KiCad 3PDT board (silk 'SUPER-FREQ 3PDT v2'), bare PCB, 2026-10
- **Archived:** 2026-10-23 with `_tools/archive_version.py`

## Finding a part

1. Open `SwitchPCB_ibom.html` in a browser. Type a reference (R14) or a value (100k) in the filter box; the part lights up on the board.
   - Hover over a pad to see its net.
   - F / B switch sides.
2. Find the same reference in `SwitchPCB_schematic.pdf` with Cmd-F.
3. `SwitchPCB_board_front.pdf` / `_back.pdf` are printable: page 1 has the outlines and references, page 2 the copper. The back is mirrored, as you see it holding the board.

## Files

- `SwitchPCB_board_back.pdf`
- `SwitchPCB_board_front.pdf`
- `SwitchPCB_ibom.html`
- `SwitchPCB_render_bottom.png`
- `SwitchPCB_render_top.png`
- `SwitchPCB_schematic.pdf`
- `docs`/
- `parts.csv`
- `production`/

`production/` holds the files sent to JLCPCB for this revision: SwitchPCB.zip.
