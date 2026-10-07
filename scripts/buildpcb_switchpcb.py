"""Place the SwitchPCB v2 board (unrouted). Run from the project folder with KiCad's python, then
_tools/autoroute.py. Layout as the Eagle board: 6 pads along the top edge, footswitch below.

Orientation: like the pedal boards, F (front) faces INTO the box and the switch body sits on the
back (B, panel side). Seen from inside, the pads read IJ IN LED GND OUT OJ left to right, so the
middle four line up with the pedal boards' IN/LED/GND/OUT header and the ribbon runs straight."""
import pcbnew, uuid
MM = pcbnew.FromMM
P = '.'
NETS = {'3': 'IN', '2': 'IJ', '1': 'BYPASS', '6': 'LED', '5': 'GND', '4': 'IN', '9': 'OUT', '8': 'OJ', '7': 'BYPASS'}
# (ref, net, schematic value, silk label)
PADS = [('J1', 'IJ', 'IN JACK', 'IJ'), ('J2', 'IN', 'IN', 'IN'), ('J3', 'LED', 'LED', 'LED'),
        ('J4', 'GND', 'GND', 'G'), ('J5', 'OUT', 'OUT', 'OUT'), ('J6', 'OJ', 'OUT JACK', 'OJ')]
X0, Y0, W, H = 100.0, 100.0, 17.15, 20.95          # Eagle board: 17.13 x 20.95 mm
CX, CY = X0 + 8.575, Y0 + 12.37                     # switch centre (Eagle 8.89, 8.89)
PY = Y0 + 2.21                                      # pad row (Eagle y 19.05)


def keep_netclass():
    """pcbnew.SaveBoard rewrites the .kicad_pro with a 0.2 mm default class: put 0.5 mm / 0.25 mm back."""
    import json
    pro = P + '/SwitchPCB.kicad_pro'; p = json.load(open(pro))
    for c in p['net_settings']['classes']:
        if c['name'] == 'Default': c['track_width'] = 0.5; c['clearance'] = 0.25
    json.dump(p, open(pro, 'w'), indent=2)

sw = pcbnew.FootprintLoad(P + '/SwitchPCB.pretty', '3PDT_Footswitch_Lugs')
pads = [pcbnew.FootprintLoad(P + '/SwitchPCB.pretty', 'WirePad_D1.2mm_OD2.032mm') for _ in PADS]
b = pcbnew.BOARD()
b.SetFileName(P + '/SwitchPCB.kicad_pcb')
nets = {}
for n in sorted(set(NETS.values()) | {p[1] for p in PADS}):
    ni = pcbnew.NETINFO_ITEM(b, '/' + n); b.Add(ni); nets[n] = ni

sw.SetFPID(pcbnew.LIB_ID('SwitchPCB', '3PDT_Footswitch_Lugs'))
b.Add(sw); sw.SetReference('SW1'); sw.SetValue('3PDT')
sw.SetPosition(pcbnew.VECTOR2I(MM(CX), MM(CY)))
sw.Flip(sw.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
sw.SetOrientationDegrees(0)      # flipped: pole A (1-3) ends up on the left, under the IJ/IN pads
for p in sw.Pads(): p.SetNet(nets[NETS[p.GetNumber()]])
sw.SetExcludedFromBOM(True); sw.SetExcludedFromPosFiles(True)
sw.Reference().SetVisible(False)

for i, (f, (ref, net, val, lab)) in enumerate(zip(pads, PADS)):
    f.SetFPID(pcbnew.LIB_ID('SwitchPCB', 'WirePad_D1.2mm_OD2.032mm'))
    b.Add(f); f.SetReference(ref); f.SetValue(val)
    f.SetPosition(pcbnew.VECTOR2I(MM(CX + (i - 2.5) * 2.54), MM(PY)))
    for p in f.Pads(): p.SetNet(nets[net])
    f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True)
    t = pcbnew.PCB_TEXT(b); t.SetText(lab); t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(MM(0.8), MM(0.8))); t.SetTextThickness(MM(0.13))
    t.SetPosition(pcbnew.VECTOR2I(MM(CX + (i - 2.5) * 2.54), MM(PY + 2.05))); b.Add(t)

for x0, y0, x1, y1 in ((X0, Y0, X0 + W, Y0), (X0 + W, Y0, X0 + W, Y0 + H), (X0 + W, Y0 + H, X0, Y0 + H), (X0, Y0 + H, X0, Y0)):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1))
    s.SetStart(pcbnew.VECTOR2I(MM(x0), MM(y0))); s.SetEnd(pcbnew.VECTOR2I(MM(x1), MM(y1))); b.Add(s)
for txt, y, layer in (('SUPER-FREQ 3PDT v2', Y0 + H - 0.95, pcbnew.F_SilkS),):
    t = pcbnew.PCB_TEXT(b); t.SetText(txt); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(0.8), MM(0.8))); t.SetTextThickness(MM(0.13))
    t.SetPosition(pcbnew.VECTOR2I(MM(CX), MM(y))); b.Add(t)
import re
sch = open(P + '/SwitchPCB.kicad_sch').read()
uu = {}
for m in re.finditer(r'\(unit (\d)\)[^\n]*\(uuid "([0-9a-f-]+)"\)\n\t\t\(property "Reference" "(\w+)"', sch):
    if m.group(3) not in uu or m.group(1) == '1': uu[m.group(3)] = m.group(2)
for f in b.GetFootprints():
    f.SetPath(pcbnew.KIID_PATH('/' + uu[f.GetReference()])); f.SetSheetname('Root'); f.SetSheetfile('SwitchPCB.kicad_sch')
pcbnew.SaveBoard(P + '/SwitchPCB.kicad_pcb', b)
keep_netclass()
print('board written')
