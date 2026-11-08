#!/usr/bin/env python3
"""Render a local, self-contained, owner-private international growth dashboard.

Reads only the validated aggregate report produced by international_growth_report.py.
No provider credentials, visitor tracking, remote assets, API calls, email payloads,
raw searches or unverified "qualified leads" can enter the HTML artifact.
"""
from __future__ import annotations
import argparse
import html
import json
import os
from collections import defaultdict
from datetime import date
from pathlib import Path

from international_growth_report import BASE, PRIVATE, PROVIDERS, CHANNELS

SCHEMA="MUSITU-PHASE03-INTERNATIONAL-GROWTH-AGGREGATE-1"
def _txt(raw):
    return html.escape(str(raw),quote=True)
def _int(value):
    if isinstance(value,bool) or not isinstance(value,int) or value<0:
        raise ValueError("Aggregate metric must be nonnegative integer")
    return value
def _position(value):
    if value is None:return "—"
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not (0<=value<=250):
        raise ValueError("Untrusted search position")
    return f"{value:.2f}"
def _validate(report):
    if report.get("document")!=SCHEMA:
        raise ValueError("Only approved private aggregate reporting format is allowed")
    if report.get("query_text_exported") is not False or report.get("visitor_or_contact_identifiers_exported") is not False:
        raise ValueError("Potentially identifying fields in aggregate report")
    if report.get("cross_provider_positions_blended") is not False:
        raise ValueError("Provider positions cannot be blended")
    countries=report.get("country_by_provider_daily",[])
    if not isinstance(countries,list) or not countries:
        raise ValueError("Cannot invent missing country coverage")
    seen=set()
    for row in countries:
        if set(row)!={"provider","date","dimension","clicks","impressions","ctr","average_search_position"}:
            raise ValueError("Unexpected or identifying country fields")
        if row["provider"] not in PROVIDERS:
            raise ValueError("Unapproved search provider")
        country=row["dimension"]
        if not isinstance(country,str) or len(country)!=2 or not country.isupper() or not country.isalpha():
            raise ValueError("Invalid normalized country code")
        day=date.fromisoformat(row["date"]).isoformat()
        key=(row["provider"],day,country)
        if key in seen:raise ValueError("Duplicate country-day-provider row")
        seen.add(key)
        clicks,impressions=_int(row["clicks"]),_int(row["impressions"])
        if clicks>impressions:raise ValueError("Invalid conversion of search metrics")
        _position(row["average_search_position"])
    for row in report.get("qualified_enquiries_by_day_and_channel",[]):
        if set(row)!={"date","channel","qualified_enquiries"}:
            raise ValueError("Unexpected enquiry record field")
        if row["channel"] not in CHANNELS:
            raise ValueError("Unapproved enquiry channel")
        date.fromisoformat(row["date"])
        _int(row["qualified_enquiries"])
    for row in report.get("query_theme_by_provider_daily",[]):
        if set(row)!={"provider","date","dimension","clicks","impressions","ctr","average_search_position"}:
            raise ValueError("Raw search query forbidden in output")
        if row["provider"] not in PROVIDERS or row["dimension"] not in {
            "brand","model_risk","quantitative_methods","creative_3d","education","other"}:
            raise ValueError("Unapproved thematic bucket")
    return countries

def render(report):
    countries=_validate(report)
    totals=defaultdict(lambda:[0,0])
    for row in countries:
        m=totals[row["provider"]]
        m[0]+=row["clicks"];m[1]+=row["impressions"]
    sections=[]
    for provider in ("google","bing"):
        rows=[r for r in countries if r["provider"]==provider]
        if not rows:
            sections.append('<section aria-label="'+_txt(provider)+'">'
                '<h2>'+_txt(provider.capitalize())+'</h2>'
                '<p class="notready">No verified country-level records imported. Not reported as zero traffic.</p></section>')
            continue
        lines=["<tr><th scope=\"col\">Date</th><th scope=\"col\">Country</th>"
               "<th scope=\"col\">Clicks</th><th scope=\"col\">Impressions</th>"
               "<th scope=\"col\">CTR</th><th scope=\"col\">Average position*</th></tr>"]
        for row in sorted(rows,key=lambda x:(x["date"],x["dimension"]),reverse=True):
            ctr=(row["clicks"]/row["impressions"]*100) if row["impressions"] else None
            cells=[row["date"],row["dimension"],str(row["clicks"]),str(row["impressions"]),
                   ("%.2f%%"%ctr) if ctr is not None else "—",_position(row["average_search_position"])]
            lines.append("<tr>"+"".join("<td>"+_txt(s)+"</td>" for s in cells)+"</tr>")
        metric=totals[provider]
        sections.append('<section aria-label="'+_txt(provider)+'"><h2>'+_txt(provider.capitalize())+'</h2>'
                        '<p>Imported country observations: <strong>'+str(len(rows))+'</strong>. '
                        'Clicks: <strong>'+str(metric[0])+'</strong>; '
                        'impressions: <strong>'+str(metric[1])+'</strong>. '
                        'No inferred indexed-page or enquiry count.</p>'
                        '<div class="scroll"><table><thead>'+lines[0]+'</thead><tbody>'
                        +"".join(lines[1:])+'</tbody></table></div></section>')
    enquiries=report.get("qualified_enquiries_by_day_and_channel",[])
    if enquiries:
        items=["<tr><th>Date</th><th>Channel</th><th>Qualified enquiries</th></tr>"]
        for row in sorted(enquiries,key=lambda x:(x["date"],x["channel"]),reverse=True):
            items.append("<tr><td>"+_txt(row["date"])+"</td><td>"+_txt(row["channel"])+
                         "</td><td>"+str(row["qualified_enquiries"])+"</td></tr>")
        lead_html='<div class="scroll"><table><thead>'+items[0]+'</thead><tbody>'+"".join(items[1:])+"</tbody></table></div>"
    else:
        lead_html='<p class="notready">No privacy-reviewed qualified enquiry aggregates supplied. Numbers are unavailable, not zero.</p>'
    start=min(x["date"] for x in countries);end=max(x["date"] for x in countries)
    stylesheet="""body{font:16px/1.6 system-ui,sans-serif;background:#0d1424;color:#f0f3ff;max-width:1180px;padding:1.5rem;margin:0 auto}
    a{color:#b7dcff}h1{font-size:clamp(1.8rem,5vw,2.8rem)}h2{font-size:1.5rem}section{padding:1.5rem 0;border-top:1px solid #53657b}
    p,li{max-width:80ch}header{padding:2rem 0}.muted{color:#bfd0e6}.notready{border-left:4px solid #b4adc9;padding:1rem;background:#222c40}
    .scroll{max-width:100%;overflow:auto}table{border-collapse:collapse;width:100%;min-width:640px}
    th,td{padding:.75rem;text-align:left;border-bottom:1px solid #53657b}th{background:#263249}
    strong{color:#a9ffdb}.pill{display:inline-block;border:1px solid #53657b;border-radius:100px;padding:.3rem 1rem}
    :focus-visible{outline:3px solid #a9ffdb;outline-offset:3px}@media print{body{background:#fff;color:#111}th{background:#eee}strong{color:#111}}"""
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow">'
        '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; style-src &#39;unsafe-inline&#39;; base-uri &#39;none&#39;; form-action &#39;none&#39;">'
        '<title>MUSITU private international search growth dashboard</title><style>'+stylesheet+'</style></head><body>'
        '<header><p class="pill">Private owner report · offline only · no visitor tracking</p>'
        '<h1>MUSITU — International search growth</h1><p class="muted">Imported historical observations from '
        +_txt(start)+' to '+_txt(end)+'. Country performance is separated by provider; this is not a complete live feed.</p></header>'
        +"".join(sections)
        +'<section aria-label="Qualified enquiries"><h2>Qualified enquiries</h2>'+lead_html+'</section>'
        '<section><h2>Reporting methodology and limitations</h2>'
        '<p>Each provider has its own data and sampling assumptions. *Search position is a provider-reported average, not a ranking guarantee. '
        'Never add Google and Bing positions together. Sparse observations may not reflect a complete dataset. '
        'Country metrics, query themes and customer enquiries are independent dimensions and are not joined into country-specific conversions.</p>'
        '<p>This HTML has no external scripts, trackers, fonts, cookies, analytics, credentials, raw queries or personal identifiers. '
        'Do not upload this report to the public website or tracked Git repository.</p></section></body></html>')

def write_dashboard(report, destination):
    output=Path(destination).resolve()
    if output==BASE or BASE in output.parents:
        if PRIVATE not in output.parents:
            raise ValueError("Private dashboard must remain outside tracked source or in ignored review-artifacts")
    output.parent.mkdir(parents=True,exist_ok=True)
    data=render(report)
    fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,"w",encoding="utf-8") as file:file.write(data)
    return output

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--report-json",type=Path,required=True)
    parser.add_argument("--output-html",type=Path,required=True)
    args=parser.parse_args()
    report=json.loads(args.report_json.read_text(encoding="utf-8"))
    path=write_dashboard(report,args.output_html)
    print(json.dumps({"status":"PRIVATE_OFFLINE_DASHBOARD_ONLY","output":str(path),"countries":len(report["country_by_provider_daily"]),
        "bing_connected_claimed":False,"qualified_enquiry_feed_claimed":False}))
