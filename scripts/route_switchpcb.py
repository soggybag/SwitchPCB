"""Hand-route SwitchPCB v2 (all on F.Cu, 0.5 mm). Run after buildpcb_switchpcb.py."""
import pcbnew
MM = pcbnew.FromMM
ROUTES = {
    'IJ':     [(102.22, 102.21), (100.8, 103.63), (100.8, 112.37), (103.28, 112.37)],    # left margin to pole A common
    'IN':     [(104.77, 102.21), (103.28, 103.70), (103.28, 107.67)],                      # to A engaged throw
    'IN ':    [(103.28, 107.67), (105.93, 107.67), (105.93, 117.07), (108.58, 117.07)],    # A throw to B bypass throw (input grounding)
    'LED':    [(107.31, 102.21), (107.31, 103.50), (108.58, 104.77), (108.58, 107.67)],
    'GND':    [(109.84, 102.21), (111.23, 103.60), (111.23, 112.37), (108.58, 112.37)],    # between poles B and C to B common
    'OUT':    [(112.39, 102.21), (112.39, 103.50), (113.88, 104.99), (113.88, 107.67)],
    'OJ':     [(114.92, 102.21), (116.35, 103.64), (116.35, 112.37), (113.88, 112.37)],    # right margin to pole C common
    'BYPASS': [(103.28, 117.07), (103.28, 119.80), (113.88, 119.80), (113.88, 117.07)],    # along the bottom edge
}
b = pcbnew.LoadBoard('SwitchPCB.kicad_pcb')
for t in list(b.GetTracks()): b.Remove(t)
for name, pts in ROUTES.items():
    net = b.FindNet('/' + name.strip())
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetLayer(pcbnew.F_Cu); t.SetWidth(MM(0.5)); t.SetNet(net)
        t.SetStart(pcbnew.VECTOR2I(MM(x0), MM(y0))); t.SetEnd(pcbnew.VECTOR2I(MM(x1), MM(y1))); b.Add(t)
pcbnew.SaveBoard('SwitchPCB.kicad_pcb', b)
import json  # SaveBoard resets the project's default net class; restore 0.5 mm / 0.25 mm
p = json.load(open('SwitchPCB.kicad_pro'))
for c in p['net_settings']['classes']:
    if c['name'] == 'Default': c['track_width'] = 0.5; c['clearance'] = 0.25
json.dump(p, open('SwitchPCB.kicad_pro', 'w'), indent=2)
print('routed')
