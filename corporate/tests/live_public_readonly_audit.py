#!/usr/bin/env python3
"""GET-only audit of currently live public corporate host.

Never tests an unpublished candidate or a protected preview. Never sends PII,
submits forms, changes DNS/Cloudflare, or exposes HTML bodies in its report.
"""
from __future__ import annotations
from datetime import datetime, timezone
from html.parser import HTMLParser
import json, re, ssl, time, urllib.request, urllib.error
from pathlib import Path
from xml.etree import ElementTree

ORIGIN='https://mftintelligence.com'
ROUTES=['/','/products/','/contact/','/legal/privacy/','/legal/terms/','/404/',
        '/redesign-readonly-nonexistent-20261120/','/robots.txt','/sitemap.xml']
HEADERS=('content-security-policy','x-content-type-options','referrer-policy',
         'permissions-policy','x-frame-options','strict-transport-security')
OUT=Path(__file__).resolve().parents[1]/'review-artifacts'/'live-public-readonly-audit.json'

class Meta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical=None
        self.robots=None
        self.lang=None
        self.images=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='html':self.lang=a.get('lang')
        elif tag=='link' and a.get('rel')=='canonical':self.canonical=a.get('href')
        elif tag=='meta' and a.get('name')=='robots':self.robots=a.get('content')
        elif tag=='img':self.images+=1

def fetch(route):
    req=urllib.request.Request(ORIGIN+route,headers={'User-Agent':'MUSITU-readonly-release-audit/1.0','Accept':'text/html,application/xml,text/plain'})
    t=time.monotonic()
    try:response=urllib.request.urlopen(req,context=ssl.create_default_context(),timeout=20)
    except urllib.error.HTTPError as e:response=e
    with response as response:
        raw=response.read(2_000_000)
        d={'route':route,'status':response.status,'duration_ms':round((time.monotonic()-t)*1000),
           'content_type':response.headers.get('Content-Type','').split(';')[0],
           'bytes':len(raw),
           'security_headers':{name:bool(response.headers.get(name)) for name in HEADERS}}
        if d['content_type']=='text/html':
            parser=Meta();parser.feed(raw.decode('utf-8',errors='replace'))
            d.update({'canonical_expected':parser.canonical==ORIGIN+route,
                      'index_robots':parser.robots,'lang':parser.lang,'images':parser.images})
            if route=='/':
                # Stores a boolean only; never copies the disclosure into public logs.
                footer_html=raw.decode('utf-8',errors='replace').split('<footer class="site-footer">')[-1].split('</footer>')[0]
                footer_text=re.sub('<[^>]*>',' ',footer_html)
                d['footer_has_granular_location']=bool(re.search(r'\b(?:Village|Road|Street)\b',footer_text,re.I))
        if route=='/sitemap.xml' and d['status']==200:
            try:
                root=ElementTree.fromstring(raw)
                locs=[x.text for x in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
                d['sitemap_loc_count']=len(locs)
                d['sitemap_all_on_canonical_origin']=bool(locs) and all(loc.startswith(ORIGIN+'/') for loc in locs)
            except (ValueError,ElementTree.ParseError):
                d['sitemap_xml_parse_error']=True
        return d

def main():
    report={'timestamp_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'currently deployed public host only, not redesign or Phase 03 candidate',
            'method':'TLS-verified, GET-only external runner; first-response times are not Core Web Vitals',
            'checks':[],'failures':[],'warnings':[]}
    for route in ROUTES:
        try: report['checks'].append(fetch(route))
        except Exception as exc:report['failures'].append({'route':route,'error_type':type(exc).__name__})
    found={x['route']:x for x in report['checks']}
    for route in ('/','/products/','/contact/','/legal/privacy/','/legal/terms/'):
        d=found.get(route)
        if not d:continue
        if d['status']!=200:report['failures'].append({'route':route,'problem':'expected HTTP 200'})
        if not d.get('canonical_expected'):report['failures'].append({'route':route,'problem':'canonical mismatch or missing'})
        if d.get('index_robots')!='index,follow':report['failures'].append({'route':route,'problem':'unexpected robots directive'})
        for h in HEADERS[:5]:
            if not d['security_headers'][h]:report['failures'].append({'route':route,'problem':'missing '+h})
        if not d['security_headers']['strict-transport-security']:
            report['warnings'].append({'route':route,'problem':'HSTS not observed; verify at zone/edge'})
    missing=found.get('/redesign-readonly-nonexistent-20261120/')
    if missing and missing['status']!=404:report['failures'].append({'route':missing['route'],'problem':'soft 404 / unexpected status'})
    sitemap=found.get('/sitemap.xml')
    if sitemap and sitemap.get('sitemap_loc_count')!=33:
        report['warnings'].append({'route':'/sitemap.xml','problem':'sitemap count diverges from earlier 33-route baseline; check independent release state'})
    home=found.get('/')
    if home and home.get('footer_has_granular_location'):
        report['warnings'].append({'route':'/','problem':'granular geographic disclosure in marketing footer; legal/privacy approval required'})
    report['passed_observed_contract']=not report['failures']
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if report['failures']:raise SystemExit(1)

if __name__=='__main__':main()
