#!/usr/bin/env python3
"""Find UI Automator node center using resource-id or class. Prints x y for adb input tap."""
import argparse, re, sys
import xml.etree.ElementTree as ET
p=argparse.ArgumentParser()
p.add_argument('xml')
p.add_argument('--resource-id')
p.add_argument('--class-name')
p.add_argument('--text')
p.add_argument('--text-contains')
args=p.parse_args()
root=ET.parse(args.xml).getroot()
for node in root.iter('node'):
 if args.resource_id and node.get('resource-id')!=args.resource_id:continue
 if args.class_name and node.get('class')!=args.class_name:continue
 if args.text and node.get('text')!=args.text:continue
 if args.text_contains and args.text_contains not in (node.get('text') or ''):continue
 m=re.fullmatch(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',node.get('bounds',''))
 if not m:continue
 a,b,c,d=map(int,m.groups())
 if c<=a or d<=b:continue
 print((a+c)//2,(b+d)//2)
 sys.exit(0)
raise SystemExit('Requested UI node not present')
