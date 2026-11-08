#!/usr/bin/env python3
"""Offline privacy-preserving international search reports from normalized, owner-authorized exports.

No provider authentication, live data claim, visitor instrumentation, DNS writes,
customer identity collection or public website publication.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "review-artifacts"
PROVIDERS = {"google", "bing"}
COUNTRY_FIELDS = ["provider", "date", "country_code", "clicks", "impressions", "average_position"]
QUERY_FIELDS = ["provider", "date", "query", "clicks", "impressions", "average_position"]
ENQUIRY_FIELDS = ["date", "channel", "qualified_enquiries"]
CHANNELS = {"google_organic", "bing_organic", "other_organic", "unattributed"}
MAX_ROWS = 250000


def _private_input(path: Path) -> Path:
    p = Path(path).resolve(strict=True)
    if not p.is_file():
        raise ValueError("Input must be a regular file")
    if BASE == p or BASE in p.parents:
        if PRIVATE != p.parent and PRIVATE not in p.parents:
            raise ValueError("Sensitive exports must be outside the tracked source tree")
    return p


def _csv(path: Path, columns: list[str]):
    with _private_input(path).open(newline="", encoding="utf-8-sig") as f:
        rows = csv.DictReader(f)
        if rows.fieldnames != columns:
            raise ValueError("Unexpected columns in private normalized export")
        for number, row in enumerate(rows, 1):
            if number > MAX_ROWS:
                raise ValueError("Private export exceeds bounded row limit")
            if None in row or any(value is None for value in row.values()):
                raise ValueError("Malformed CSV row")
            yield row


def _date(value: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Date must be YYYY-MM-DD")
    d = date.fromisoformat(value)
    if d < date(2020, 1, 1) or d > date.today():
        raise ValueError("Export date outside historical range")
    return value


def _count(value: str) -> int:
    if not re.fullmatch(r"\d{1,12}", value):
        raise ValueError("Metric must be a nonnegative whole number")
    return int(value)


def _metric(row: dict) -> tuple[str, str, int, int, float | None]:
    provider = row["provider"].strip().lower()
    if provider not in PROVIDERS:
        raise ValueError("Unapproved search provider")
    day = _date(row["date"])
    clicks, impressions = _count(row["clicks"]), _count(row["impressions"])
    if clicks > impressions:
        raise ValueError("Clicks exceed impressions")
    raw = row["average_position"].strip()
    if not raw and impressions == 0:
        position = None
    else:
        if not re.fullmatch(r"\d{1,3}(?:\.\d{1,5})?", raw):
            raise ValueError("Invalid average search position")
        position = float(raw)
        if not (0 <= position <= 250):
            raise ValueError("Average search position outside bounded range")
    return provider, day, clicks, impressions, position


def _update(table: dict, key: tuple, clicks: int, impressions: int, position: float | None):
    entry = table[key]
    entry[0] += clicks
    entry[1] += impressions
    if impressions:
        entry[2] += impressions * position


def _out(key: tuple, values: list) -> dict:
    clicks, impressions, position_total = values
    return {"provider": key[0], "date": key[1], "dimension": key[2],
            "clicks": clicks, "impressions": impressions,
            "ctr": round(clicks / impressions, 5) if impressions else None,
            "average_search_position": round(position_total / impressions, 2) if impressions else None}


def _theme(query: str) -> str:
    s = query.casefold()
    if any(word in s for word in ("musitu", "mftintelligence", "mft intelligence")):
        return "brand"
    if any(word in s for word in ("model risk", "backtest", "walk-forward", "drawdown")):
        return "model_risk"
    if any(word in s for word in ("optimization", "optimisation", "quantitative", "numerical", "statistics")):
        return "quantitative_methods"
    if any(word in s for word in ("3d", "glb", "animation", "3-d")):
        return "creative_3d"
    if any(word in s for word in ("education", "chemistry", "revision", "learning")):
        return "education"
    return "other"


def make_report(country_file: Path, query_file: Path | None = None,
                enquiry_file: Path | None = None) -> dict:
    countries = defaultdict(lambda: [0, 0, 0.0])
    themes = defaultdict(lambda: [0, 0, 0.0])
    enquiries = {}
    seen = set()
    for row in _csv(country_file, COUNTRY_FIELDS):
        provider, day, clicks, impressions, position = _metric(row)
        code = row["country_code"]
        if not re.fullmatch(r"[A-Z]{2}", code):
            raise ValueError("Country label requires normalized uppercase ISO alpha-2 shape")
        key = (provider, day, code)
        if key in seen:
            raise ValueError("Duplicate country observation")
        seen.add(key)
        _update(countries, key, clicks, impressions, position)
    if not countries:
        raise ValueError("No real country observations; cannot create an empty misleading report")
    if query_file is not None:
        for row in _csv(query_file, QUERY_FIELDS):
            provider, day, clicks, impressions, position = _metric(row)
            query = row["query"].strip()
            if not query or len(query) > 300:
                raise ValueError("Invalid search query export row")
            if "@" in query or re.search(r"\b\d{8,}\b", query):
                continue  # Suppress sensitive raw query strings entirely.
            _update(themes, (provider, day, _theme(query)), clicks, impressions, position)
    if enquiry_file is not None:
        for row in _csv(enquiry_file, ENQUIRY_FIELDS):
            day, channel = _date(row["date"]), row["channel"]
            if channel not in CHANNELS:
                raise ValueError("Unapproved enquiry attribution")
            key = (day, channel)
            if key in enquiries:
                raise ValueError("Duplicate qualified enquiry count")
            enquiries[key] = _count(row["qualified_enquiries"])
    country_rows = [_out(k, countries[k]) for k in sorted(countries)]
    return {
        "document": "MUSITU-PHASE03-INTERNATIONAL-GROWTH-AGGREGATE-1",
        "source_type": "private_normalized_export",
        "live_search_console_access_verified": False,
        "live_bing_webmaster_access_verified": False,
        "sitemap_submission_claimed": False,
        "indexing_claimed": False,
        "query_text_exported": False,
        "visitor_or_contact_identifiers_exported": False,
        "cross_provider_positions_blended": False,
        "country_by_provider_daily": country_rows,
        "query_theme_by_provider_daily": [_out(k, themes[k]) for k in sorted(themes)],
        "qualified_enquiries_by_day_and_channel": [
            {"date": k[0], "channel": k[1], "qualified_enquiries": enquiries[k]}
            for k in sorted(enquiries)],
        "coverage": {
            "countries_present": sorted({row["dimension"] for row in country_rows}),
            "data_first_date": min(row["date"] for row in country_rows),
            "data_last_date": max(row["date"] for row in country_rows),
            "providers_present": sorted({row["provider"] for row in country_rows}),
            "query_export_supplied": query_file is not None,
            "enquiry_export_supplied": enquiry_file is not None,
        },
        "interpretation": (
            "Average search position is a provider-specific impression-weighted metric, "
            "not an exact rank. Google/Bing positions are never blended. Country, query "
            "themes and qualified enquiry counts are separate dimensions; do not infer "
            "country-level queries or conversions by joining these tables. No live "
            "provider readback or indexing outcome is established by an offline export."
        ),
    }


def write_private_report(report: dict, destination: Path) -> Path:
    destination = Path(destination).resolve()
    if BASE == destination or BASE in destination.parents:
        if PRIVATE not in destination.parents:
            raise ValueError("Private reports must never enter build/source/webroot")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="No-network, private international search export normalization")
    parser.add_argument("--country-csv", type=Path, required=True)
    parser.add_argument("--query-csv", type=Path)
    parser.add_argument("--enquiry-csv", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = make_report(args.country_csv, args.query_csv, args.enquiry_csv)
    output = write_private_report(report, args.output)
    print(json.dumps({
        "status": "PRIVATE_EXPORT_ONLY",
        "country_rows": len(report["country_by_provider_daily"]),
        "theme_rows": len(report["query_theme_by_provider_daily"]),
        "qualified_enquiry_rows": len(report["qualified_enquiries_by_day_and_channel"]),
        "live_provider_connected": False,
        "output": str(output),
    }, sort_keys=True))
