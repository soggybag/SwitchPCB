"""Generate the SwitchPCB v2 KiCad project (schematic, symbol, footprints, unrouted board).
Transcribed from the Eagle SwitchPCB (2022). Run with KiCad's python from the project folder:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 scripts/build_switchpcb.py
Then route with _tools/autoroute.py. Don't re-run after hand edits: it overwrites the board."""
import json, os, re, shutil, uuid
U = lambda: str(uuid.uuid4())
P = os.getcwd()
NAME = 'SwitchPCB'
KSYM = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/'

# ---------------- nets (Eagle SwitchPCB.sch) ----------------
# 3PDT pins: pole A = 1,2,3 (2 = common), pole B = 4,5,6, pole C = 7,8,9
# Engaged throws are 3/6/9 (the row nearest the pads), bypass throws 1/4/7: this lets every
# track run straight on the board. Electrically the same as the Eagle board (which throw is
# "on" just depends on the switch state).
SW = {'3': 'IN', '2': 'IJ', '1': 'BYPASS',      # input pole: jack -> circuit, or -> bypass link
      '6': 'LED', '5': 'GND', '4': 'IN',        # LED to ground when on; circuit input grounded when off
      '9': 'OUT', '8': 'OJ', '7': 'BYPASS'}     # output pole
PADS = [('J1', 'IJ', 'IN JACK'), ('J2', 'IN', 'IN'), ('J3', 'LED', 'LED'),
        ('J4', 'GND', 'GND'), ('J5', 'OUT', 'OUT'), ('J6', 'OJ', 'OUT JACK')]

# ---------------- footprints ----------------
def fp_text(kind, txt, x, y, layer, hide=False, size=1.0):
    return ('\t(property "%s" "%s" (at %g %g 0) (layer "%s")%s (uuid "%s") (effects (font (size %g %g) (thickness 0.15))))\n'
            % (kind, txt, x, y, layer, ' (hide yes)' if hide else '', U(), size, size))
def rect(x0, y0, x1, y1, layer, w):
    return '\t(fp_rect (start %g %g) (end %g %g) (stroke (width %g) (type solid)) (fill no) (layer "%s") (uuid "%s"))\n' % (x0, y0, x1, y1, w, layer, U())

fs = ['(footprint "3PDT_Footswitch_Lugs" (version 20241229) (generator "pcbnew") (generator_version "9.0") (layer "F.Cu")\n',
      '\t(descr "3PDT latching footswitch (blue stomp switch), solder lugs. Lug grid 5.3 mm between poles x 4.7 mm between throws, plated slots 2.8 x 1.3 mm (PedalDivision 3PDT size) with 3.8 x 2.4 mm pads; the slots hold the switch square while soldering. Pole A = 1-3, B = 4-6, C = 7-9; 2/5/8 = commons. The switch body goes on the side this footprint is placed on.")\n',
      '\t(tags "3PDT footswitch stomp")\n',
      fp_text('Reference', 'REF**', 0, -9.6, 'F.SilkS'), fp_text('Value', '3PDT', 0, 9.6, 'F.Fab'),
      rect(-7.62, -7.62, 7.62, 7.62, 'F.SilkS', 0.12), rect(-8.5, -8.5, 8.5, 8.5, 'F.Fab', 0.1),
      rect(-8.85, -8.85, 8.85, 8.85, 'F.CrtYd', 0.05)]
n = 1
for x in (-5.3, 0, 5.3):
    for y in (-4.7, 0, 4.7):
        fs.append('\t(pad "%d" thru_hole %s (at %g %g) (size 3.8 2.4) (drill oval 2.8 1.3) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "%s"))\n'
                  % (n, 'rect' if n == 1 else 'oval', x, y, U()))
        n += 1
fs.append('\t(model "${KIPRJMOD}/3dmodels/3PDT_FS.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n)\n')
open(P + '/SwitchPCB.pretty/3PDT_Footswitch_Lugs.kicad_mod', 'w').write(''.join(fs))

open(P + '/SwitchPCB.pretty/WirePad_D1.2mm_OD2.032mm.kicad_mod', 'w').write(''.join([
    '(footprint "WirePad_D1.2mm_OD2.032mm" (version 20241229) (generator "pcbnew") (generator_version "9.0") (layer "F.Cu")\n',
    '\t(descr "Wire / ribbon solder pad, 1.2 mm hole, 2.032 mm pad (as the Eagle SwitchPCB pads). 2.54 mm pitch rows.")\n',
    '\t(attr through_hole)\n',
    fp_text('Reference', 'REF**', 0, -2, 'F.Fab', hide=True, size=0.8), fp_text('Value', 'PAD', 0, 2, 'F.Fab', hide=True, size=0.8),
    rect(-1.27, -1.27, 1.27, 1.27, 'F.CrtYd', 0.05),
    '\t(pad "1" thru_hole circle (at 0 0) (size 2.032 2.032) (drill 1.2) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "%s"))\n)\n' % U()]))

open(P + '/fp-lib-table', 'w').write('(fp_lib_table\n\t(version 7)\n\t(lib (name "SwitchPCB")(type "KiCad")(uri "${KIPRJMOD}/SwitchPCB.pretty")(options "")(descr "3PDT footswitch board parts"))\n)\n')
open(P + '/sym-lib-table', 'w').write('(sym_lib_table\n\t(version 7)\n\t(lib (name "SwitchPCB")(type "KiCad")(uri "${KIPRJMOD}/SwitchPCB.kicad_sym")(options "")(descr "3PDT footswitch symbol"))\n)\n')

# ---------------- symbol: 3PDT as three SPDT units ----------------
def eff(hide=False):
    return '(effects (font (size 1.27 1.27))%s)' % (' (hide yes)' if hide else '')
def pin(num, x, y, ang):
    return '\t\t\t(pin passive line (at %g %g %d) (length 2.54) (name "~" %s) (number "%s" %s))\n' % (x, y, ang, eff(), num, eff())
def sym_body(name):
    s = ['\t(symbol "%s"\n' % name, '\t\t(pin_names (offset 0) (hide yes))\n\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)\n',
         '\t\t(property "Reference" "SW" (at 0 5.08 0) %s)\n' % eff(), '\t\t(property "Value" "3PDT" (at 0 -5.08 0) %s)\n' % eff(),
         '\t\t(property "Footprint" "SwitchPCB:3PDT_Footswitch_Lugs" (at 0 0 0) %s)\n' % eff(True),
         '\t\t(property "Datasheet" "" (at 0 0 0) %s)\n' % eff(True),
         '\t\t(property "Description" "3PDT latching footswitch, three SPDT units (pin 2/5/8 = common)" (at 0 0 0) %s)\n' % eff(True)]
    base = name.split(':')[-1]
    s.append('\t\t(symbol "%s_0_1"\n' % base)
    s.append('\t\t\t(rectangle (start -3.175 3.81) (end 3.175 -3.81) (stroke (width 0) (type default)) (fill (type background)))\n')
    for cx, cy in ((-2.032, 0), (2.032, 2.54), (2.032, -2.54)):
        s.append('\t\t\t(circle (center %g %g) (radius 0.4572) (stroke (width 0) (type default)) (fill (type none)))\n' % (cx, cy))
    s.append('\t\t\t(polyline (pts (xy -1.651 0.254) (xy 1.651 2.286)) (stroke (width 0) (type default)) (fill (type none)))\n\t\t)\n')
    for u in (1, 2, 3):
        a, c, b = (str(3 * u - 2), str(3 * u - 1), str(3 * u))
        s.append('\t\t(symbol "%s_%d_1"\n' % (base, u) + pin(a, 5.08, 2.54, 180) + pin(c, -5.08, 0, 0) + pin(b, 5.08, -2.54, 180) + '\t\t)\n')
    s.append('\t\t(embedded_fonts no)\n\t)\n')
    return ''.join(s)
open(P + '/SwitchPCB.kicad_sym', 'w').write('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") (generator_version "9.0")\n'
                                           + sym_body('SW_3PDT_x3') + ')\n')

def lib_block(path, name, newname):
    s = open(path).read(); i = s.index('(symbol "%s"' % name); d = 0; j = i
    while True:
        c = s[j]
        if c == '(': d += 1
        elif c == ')':
            d -= 1
            if d == 0: break
        elif c == '"':
            j += 1
            while s[j] != '"':
                if s[j] == '\\': j += 1
                j += 1
        j += 1
    return s[i:j + 1].replace('(symbol "%s"' % name, '(symbol "%s"' % newname, 1)

# ---------------- schematic ----------------
ROOT = U()
items = []
def label(name, x, y, left):
    items.append('\t(label "%s" (at %g %g %d) (effects (font (size 1.27 1.27)) (justify %s bottom)) (uuid "%s"))\n'
                 % (name, x, y, 180 if left else 0, 'right' if left else 'left', U()))
def wire(x0, y0, x1, y1):
    items.append('\t(wire (pts (xy %g %g) (xy %g %g)) (stroke (width 0) (type default)) (uuid "%s"))\n' % (x0, y0, x1, y1, U()))
def prop(k, v, x, y, hide=False):
    return '\t\t(property "%s" "%s" (at %g %g 0) %s)\n' % (k, v, x, y, eff(hide))
def symbol(lib, ref, val, fp, x, y, unit, pins, rot=0, extra=''):
    # everything on this board is hand-soldered: keep it out of BOM and position files
    s = '\t(symbol (lib_id "%s") (at %g %g %d) (unit %d) (exclude_from_sim no) (in_bom no) (on_board yes) (in_pos_files no) (dnp no) (uuid "%s")\n' % (
        lib, x, y, rot, unit, U())
    s += prop('Reference', ref, x, y - 6.35) + prop('Value', val, x, y + 6.35) + prop('Footprint', fp, x, y, True)
    s += prop('Datasheet', '', x, y, True) + prop('Description', '', x, y, True) + extra
    s += ''.join('\t\t(pin "%s" (uuid "%s"))\n' % (p, U()) for p in pins)
    s += '\t\t(instances (project "%s" (path "/%s" (reference "%s") (unit %d))))\n\t)\n' % (NAME, ROOT, ref, unit)
    items.append(s)

X = 127.0
for u, Y in ((1, 76.2), (2, 96.52), (3, 116.84)):
    a, c, b = str(3 * u - 2), str(3 * u - 1), str(3 * u)
    symbol('SwitchPCB:SW_3PDT_x3', 'SW1', '3PDT', 'SwitchPCB:3PDT_Footswitch_Lugs', X, Y, u, [a, c, b])
    wire(X - 5.08, Y, X - 10.16, Y); label(SW[c], X - 10.16, Y, True)
    wire(X + 5.08, Y - 2.54, X + 10.16, Y - 2.54); label(SW[a], X + 10.16, Y - 2.54, False)
    wire(X + 5.08, Y + 2.54, X + 10.16, Y + 2.54); label(SW[b], X + 10.16, Y + 2.54, False)
for i, (ref, net, val) in enumerate(PADS):
    x, y = 177.8, 71.12 + i * 7.62
    symbol('Connector_Generic:Conn_01x01', ref, val, 'SwitchPCB:WirePad_D1.2mm_OD2.032mm', x, y, 1, ['1'])
    wire(x - 5.08, y, x - 10.16, y); label(net, x - 10.16, y, True)
note = ('3PDT true bypass with input grounding (from the Eagle SwitchPCB, 2022).\\n'
        'ON: input jack -> IN, OUT -> output jack, LED cathode -> GND.\\n'
        'BYPASS: input jack -> output jack through the BYPASS link; circuit IN shorted to GND.\\n'
        'J2-J5 match the pedal boards\' 1x4 ribbon header: IN / LED / GND / OUT.')
items.append('\t(text "%s" (exclude_from_sim no) (at 101.6 139.7 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "%s"))\n' % (note, U()))
items.append('\t(text "Jacks and ribbon pads" (exclude_from_sim no) (at 160.02 63.5 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "%s"))\n' % U())
libsyms = sym_body('SwitchPCB:SW_3PDT_x3') + lib_block(KSYM + 'Connector_Generic.kicad_sym', 'Conn_01x01', 'Connector_Generic:Conn_01x01')
sch = ('(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid "%s") (paper "A5")\n'
       '\t(title_block (title "3PDT Footswitch Board") (rev "2.0") (company "Super-Freq"))\n'
       '\t(lib_symbols\n%s\t)\n%s\t(sheet_instances (path "/" (page "1")))\n\t(embedded_fonts no)\n)\n') % (ROOT, libsyms, ''.join(items))
open(P + '/%s.kicad_sch' % NAME, 'w').write(sch)
print('schematic, symbol and footprints written')
