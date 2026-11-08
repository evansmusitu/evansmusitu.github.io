# Phase 03 international search growth — private reporting contract

This source-only instrument processes **authorized normalized CSV exports** for MUSITU corporate Search Console/Bing search data, and optionally manually approved **aggregated** qualified enquiry counts. A separate connected Windsor.ai Google Search Console account now returns authenticated provider data; the offline report script itself has **no API/network access**. There is no analytics cookie, visitor collection or publication. Google historical sitemap submission is evidenced; Bing live submission remains unverified. Provider account connection and source readback are separate release gates.

## Source CSV format

- country.csv: provider,date,country_code,clicks,impressions,average_position (country code is normalized uppercase two-letter code; source ownership and actual code mapping must be independently checked)
- queries.csv (optional): provider,date,query,clicks,impressions,average_position
- enquiries.csv (optional): date,channel,qualified_enquiries (channel must be google_organic, bing_organic, other_organic, or unattributed; **aggregate counts only**; not names, addresses, emails, IPs or visit-level records)

Country and query reports are **independent dimensions**. Never join them to infer per-country query performance or country-level conversions. Both providers are always reported separately; average search position is not a guaranteed rank. Queries are bucketed into fixed thematic groups, raw search queries never persist to the output, and potentially sensitive terms containing email markers or long numbers are suppressed. Qualification of enquiries must be established separately by the owner; source counts do not certify them.

Keep all input CSVs outside the repository or under the ignored corporate/review-artifacts directory, in an owner-approved private workspace. The script rejects output in the public dist webroot or tracked source. Reports are created with permissions 0600, no overwriting. The script does not generate sample traffic or default to zeros when evidence is missing.

Command (from corporate directory, after actual approved exports exist):
python3 scripts/international_growth_report.py --country-csv /private/country.csv --query-csv /private/queries.csv --enquiry-csv /private/enquiries.csv --output review-artifacts/international-private-report.json

## Activation requirements

1. Confirm live Google Domain property verification (historical owner notification dated September 7, 2026 is available) and live Bing verified URL property (historical notification dated September 7); distinguish notifications from latest provider account status.
2. Obtain trustworthy country/date search-performance and query/date exports with accurate GSC/Bing dimension mapping and permissions. Preserve original provider, date, and search-platform definitions. Do not mark live connection until fresh provider readback.
3. Check that the 33 public canonical core routes are valid, and separately audit indexing, crawl and sitemap processing in each provider account. An offline report or public robots/sitemap check cannot prove indexing or submission.
4. Approve a specific enquiry-qualification rule and a minimal, privacy-reviewed daily aggregate source. Do not add client tracking or email payloads without appropriate privacy controls.
5. Review source recency, gap coverage, and approved country focus before operational reporting. Historical October Google 15-click milestone is **not** a present-day country/rank baseline.
6. Maintain the existing hourly public corporate monitor and daily alert watch for new provider notices. Full growth reporting remains blocked until authenticated data import is actually evidenced.

## Connected-account evidence on 8 November 2026

Windsor.ai confirmed an authenticated Google Search Console Domain property `sc-domain:mftintelligence.com`. Its provider Sitemaps report had the canonical corporate `https://mftintelligence.com/sitemap.xml` submitted/downloaded 6 November with zero reported sitemap issues. **Latest provider readback returned 99 submitted URLs, whereas the earlier provider readback and the live public sitemap monitor each showed 33. This discrepancy must be reconciled and does not prove 99 currently indexable pages.** This establishes Google sitemap existence/submission *before the current release*. It is not evidence that any URL from unpublished PR #35 is in the Google index. Live Bing analytics remain unconnected. Domain-property reports may include `payments.mftintelligence.com` and other subdomains, so use corporate hostname filters for corporate-only analysis; cross-dimension grouped totals from the connector have not yet reconciled. Do not claim an exact present-day country or ranking baseline from these sparse results. The private offline reporting contract remains optional and does not replace live provider snapshots.

## Sparse current Google performance baseline

Connected, read-only Search Console reporting for 2026-10-12 through 2026-11-07 inclusive returned exact hostname `mftintelligence.com` with Zimbabwe **1 click, 5 impressions** and provider average position **1.2**. Separately querying page `https://mftintelligence.com/` returned **0 clicks, 3 impressions**. These are independent groupings with inconsistent totals, not an additive funnel; no other countries were reported. No raw search queries or customer data were exported. Use the enabled daily Search & Growth Watch for new material anomalies, including the documented 99-versus-33 sitemap-count mismatch. Live Bing Webmaster data remains unconnected and qualified enquiries need separate privacy-reviewed aggregates.
