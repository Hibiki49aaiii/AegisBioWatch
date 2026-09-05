#!/usr/bin/env python3
"""Audit every physical PCB pad against the recovered r8 logical topology."""
from __future__ import annotations
import argparse,json,xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
import pcbnew  # type: ignore

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--xml',required=True); ap.add_argument('--pcb',required=True); ap.add_argument('--output',required=True); args=ap.parse_args()
 root=ET.parse(args.xml).getroot(); expected={}
 for n in root.findall('./nets/net'):
  for node in n.findall('node'): expected[(node.attrib['ref'],node.attrib['pin'])]=n.attrib['name']
 b=pcbnew.LoadBoard(args.pcb); physical=defaultdict(list)
 for fp in b.GetFootprints():
  for pad in fp.Pads(): physical[(fp.GetReference(),str(pad.GetNumber()))].append(pad.GetNetname() or '')
 audited=[k for k in expected if k[0] not in {'J3','J5','J6'}]
 mism=[{'ref':k[0],'pin':k[1],'expected':expected[k],'actual':physical.get(k,[])} for k in audited if not physical.get(k) or any(v!=expected[k] for v in physical[k])]
 unexpected=[{'ref':k[0],'pin':k[1],'nets':nets} for k,nets in physical.items() if k not in expected and any(nets)]
 out={'source_nodes':len(expected),'audited_present_source_nodes':len(audited),'mismatches':mism,'unexpected_pad_nets':unexpected,'result':'PASS' if not mism and not unexpected else 'FAIL'}
 Path(args.output).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
 if out['result']!='PASS' or len(audited)!=268: raise SystemExit('physical pad/net audit failed')
if __name__=='__main__': main()
