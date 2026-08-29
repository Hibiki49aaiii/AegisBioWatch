#!/usr/bin/env python3
"""Read-only geometry probe for route-1be C4.1/+1V8 -> C302.1/+1V8.

The script loads a reproduced accepted route-1bd PCB, validates its executed
source evidence, and records endpoint/corridor geometry. It never saves or
modifies the board.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import pcbnew  # type: ignore

ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bd'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1bd-r13.kicad_pcb'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1bd.json'
CORRIDOR=(39.5,14.0,42.3,20.3)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def pt(v): return [round(mm(v.x),6),round(mm(v.y),6)]
def rect_obj(o):
    b=o.GetBoundingBox()
    return [round(mm(b.GetX()),6),round(mm(b.GetY()),6),round(mm(b.GetRight()),6),round(mm(b.GetBottom()),6)]
def intersects(a,b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])
def track_rect(t):
    a=pt(t.GetStart()); b=pt(t.GetEnd()); half=mm(t.GetWidth())/2.0
    return [min(a[0],b[0])-half,min(a[1],b[1])-half,max(a[0],b[0])+half,max(a[1],b[1])+half]
def rotation(fp):
    if hasattr(fp,'GetOrientationDegrees'):
        return round(float(fp.GetOrientationDegrees()),6)
    return round(float(fp.GetOrientation().AsDegrees()),6)

def fp_data(fp):
    pads=[]
    for p in fp.Pads():
        size=p.GetSize()
        pads.append({
          'number':str(p.GetNumber()),'net':p.GetNetname(),'position_mm':pt(p.GetPosition()),
          'size_mm':[round(mm(size.x),6),round(mm(size.y),6)],
          'bbox_mm':rect_obj(p),'layers':str(p.GetLayerSet().FmtHex()) if hasattr(p.GetLayerSet(),'FmtHex') else None
        })
    return {
      'reference':fp.GetReference(),'value':fp.GetValue(),'rotation_deg':rotation(fp),
      'bbox_mm':rect_obj(fp),'pads':sorted(pads,key=lambda x:x['number'])
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--route1bd-drc-json',required=True)
    ap.add_argument('--route1bd-pin-net-audit',required=True)
    ap.add_argument('--output',required=True)
    args=ap.parse_args()

    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha:
        raise SystemExit('route1be probe route1bd report/PCB SHA mismatch')
    d=loadj(args.route1bd_drc_json); a=loadj(args.route1bd_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=119:
        raise SystemExit('route1be probe route1bd DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268:
        raise SystemExit('route1be probe route1bd pin/net gate failed')

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={f.GetReference():f for f in board.GetFootprints()}
    if 'C4' not in fps or 'C302' not in fps:
        raise SystemExit('route1be probe missing C4/C302')

    c4=fp_data(fps['C4']); c302=fp_data(fps['C302'])
    if c4['value']!='100nF' or c302['value']!='1uF':
        raise SystemExit(f"route1be probe value gate failed C4={c4['value']} C302={c302['value']}")
    p4={p['number']:p for p in c4['pads']}; p302={p['number']:p for p in c302['pads']}
    expected_nets=(p4.get('1',{}).get('net'),p4.get('2',{}).get('net'),p302.get('1',{}).get('net'),p302.get('2',{}).get('net'))
    if expected_nets!=('+1V8','GND','+1V8','GND'):
        raise SystemExit(f'route1be probe net gate failed: {expected_nets}')
    if p4['1']['position_mm']!=[41.005,14.975]:
        raise SystemExit(f"route1be probe C4.1 coordinate changed: {p4['1']['position_mm']}")
    if p302['2']['position_mm']!=[41.265,19.585]:
        raise SystemExit(f"route1be probe C302.2 coordinate changed: {p302['2']['position_mm']}")

    nearby_fps=[]
    nearby_pads=[]
    for fp in board.GetFootprints():
        fd=fp_data(fp)
        if intersects(fd['bbox_mm'],CORRIDOR):
            nearby_fps.append({'reference':fd['reference'],'value':fd['value'],'bbox_mm':fd['bbox_mm'],'rotation_deg':fd['rotation_deg']})
        for p in fd['pads']:
            if intersects(p['bbox_mm'],CORRIDOR):
                nearby_pads.append({'reference':fd['reference'],**p})

    nearby_copper=[]
    for item in board.GetTracks():
        kind=type(item).__name__
        net=item.GetNetname() if hasattr(item,'GetNetname') else ''
        width=round(mm(item.GetWidth()),6) if hasattr(item,'GetWidth') else None
        if isinstance(item,pcbnew.PCB_VIA):
            pos=pt(item.GetPosition()); half=(width or 0)/2.0
            bbox=[pos[0]-half,pos[1]-half,pos[0]+half,pos[1]+half]
            if intersects(bbox,CORRIDOR):
                nearby_copper.append({'kind':'via','net':net,'position_mm':pos,'size_mm':width,'bbox_mm':[round(x,6) for x in bbox]})
        else:
            bbox=track_rect(item)
            if intersects(bbox,CORRIDOR):
                nearby_copper.append({
                  'kind':'track','class':kind,'net':net,'start_mm':pt(item.GetStart()),'end_mm':pt(item.GetEnd()),
                  'width_mm':width,'layer':board.GetLayerName(item.GetLayer()),'bbox_mm':[round(x,6) for x in bbox]
                })

    out={
      'revision':'r13-route1be-c4-c302-1v8-geometry-probe',
      'source_route1bd_sha256':srcsha,
      'source_gate':{'rule_violations':0,'unconnected_items':119,'pin_net_audit':'PASS','audited_nodes':268},
      'board_modified':False,
      'corridor_mm':list(CORRIDOR),
      'C4':c4,'C302':c302,
      'endpoint_vector_mm':{
        'from':p4['1']['position_mm'],'to':p302['1']['position_mm'],
        'dx':round(p302['1']['position_mm'][0]-p4['1']['position_mm'][0],6),
        'dy':round(p302['1']['position_mm'][1]-p4['1']['position_mm'][1],6)
      },
      'nearby_footprints':sorted(nearby_fps,key=lambda x:x['reference']),
      'nearby_pads':sorted(nearby_pads,key=lambda x:(x['reference'],x['number'])),
      'nearby_copper':nearby_copper,
      'release_status':'NOT_FOR_GERBER'
    }
    Path(args.output).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
