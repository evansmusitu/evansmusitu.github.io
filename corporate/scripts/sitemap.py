#!/usr/bin/env python3
"""Sitemap *template* generator. No public sitemap without an approved origin.

Returns XML as a pure function; CLI writes only a review artifact under corporate/.
This script never writes to dist, edits DNS or activates indexing.
"""
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree.ElementTree import Element,SubElement,tostring
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=json.loads((ROOT/'dist/manifest.json').read_text(encoding='utf-8'))

def make_sitemap(origin:str,cleared_routes=()):
 u=urlsplit(origin)
 if u.scheme!='https' or not u.hostname or u.username or u.password or u.port is not None or u.query or u.fragment or u.path.strip('/'):
  raise ValueError('Origin must be an explicitly approved canonical HTTPS origin with no path, credentials, port or query')
 gated=set(MANIFEST['gated_routes']);cleared=set(cleared_routes)
 if cleared-gated:raise ValueError('Only explicitly gated routes may be cleared')
 root=Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
 included=[]
 for route in MANIFEST['routes']:
  if route=='/404/' or route in gated-cleared:continue
  item=SubElement(root,'url')
  SubElement(item,'loc').text=origin.rstrip('/')+route
  included.append(route)
 return b'<?xml version="1.0" encoding="UTF-8"?>\n'+tostring(root,encoding='utf-8')+b'\n',included

if __name__=='__main__':
 ap=argparse.ArgumentParser()
 ap.add_argument('--canonical-origin',required=True,help='Owner-approved full HTTPS origin, no path')
 ap.add_argument('--clear-route',action='append',default=[],help='Individually cleared gated route')
 args=ap.parse_args()
 xml,inc=make_sitemap(args.canonical_origin,args.clear_route)
 out=ROOT/'review-artifacts/sitemap-release-candidate.xml'
 out.parent.mkdir(exist_ok=True)
 out.write_bytes(xml)
 print(f'Created UNPUBLISHED review sitemap candidate {out} with {len(inc)} routes. Nothing deployed.')
