# MUSITU — Corporate correspondence address publication handoff

Status: **PREPARED; public legal-address change NOT AUTHORIZED OR VERIFIED**  
Applies to: the corporate website only. Does not authorize product, DNS, email-routing, billing or workspace changes.

## Release decision

The website's global footer and general company/homepage copy should avoid granular location and founding-location claims not needed for the visitor's task. Company operator and data-controller identification remain required where applicable. A public, usable business correspondence/service address may replace an existing legal disclosure only once its lawful suitability and precise wording are confirmed.

**Do not replace a legally required physical or service address with only an email address, a fabricated office, a generic city, an unverified virtual office, or a temporary "pending" placeholder.** Do not assert compliance without independent evidence.

## Preferred public arrangement

- **Business correspondence / service address:** a real, externally authorized professional or serviced-office location where MUSITU is permitted to receive correspondence and, if the law requires it, valid service of legal documents. A mail-forwarding-only service is not automatically an acceptable physical registered/service office.
- **Official digital support:** support@mftintelligence.com, prominently available on Contact, Support, Privacy Policy and Terms.
- **Registered office and mandatory particulars:** retain in the appropriate statutory records and include any mandatory disclosures on the public website where and to the extent applicable. A separate public mailing/service address does not change registered-office obligations or relevant regulator filings.
- **No unsupported authority or role:** do not describe a law firm, consultant, office operator or agent as engaged/appointed until authority is documented.

## Exact source locations requiring replacement review

1. `corporate/content/pages.json` → `/legal/privacy/` main content, **Coverage and website operator**, service and correspondence address sentence.
2. `corporate/content/pages.json` → `/legal/terms/` main content, **Purpose and scope**, same sentence.
3. `corporate/templates/footer.html`: global footer no longer needs a granular physical address unless the final legal review specifically requires one on every page.
4. `corporate/content/public-records.json`: public company summary should remain location-neutral unless a factual, deliberately approved geographic statement serves a visitor need.
5. Legal contact method and operator role must stay consistent across Policy, Terms, Contact and Support. Do not inject addresses into JSON-LD or public business claims unless accurate and approved.

## Acceptance evidence before replacing legal address

- [ ] The operator confirms a **genuine** usable professional/public correspondence or service address.
- [ ] Right to use the address for MUSITU's business is documented, including postal handling and any permitted legal-document service.
- [ ] A qualified local legal/privacy reviewer determines which physical, registered-office, legal-identity, controller and electronic-transactions disclosures must remain public under applicable law.
- [ ] The reviewer explicitly approves the **exact final public wording** of the Privacy Policy and Terms and any necessary registered-office or regulator particulars.
- [ ] Test correspondence from an independent sender to the service address and a response/receipt mechanism have been independently evidenced where appropriate.
- [ ] Replace the two source legal address sentences **atomically** with the approved text; do not commit a made-up address, unresolved placeholder or an owner's private location unnecessarily.
- [ ] Run source and exact-artifact production tests, human accessibility/security review and protected staging acceptance; fail closed if route texts differ.
- [ ] The owner approves the final public identification and an authorized operator controls deployment/rollback.
- [ ] Following a lawful public release, update search indexing and check cached exposure; previous public HTML and Git history cannot be assumed to disappear merely because current pages change.

## Prepared Phase 03 change set (not a legal release approval)

- Global website footer: concise MUSITU identity, no unnecessarily granular address and a working email link.
- Homepage/company pages and public route-data descriptions: neutral international company positioning.
- **Privacy Policy and Terms remain unchanged pending legally approved replacement**. This temporary state can still expose existing public data; do not describe the address transition as complete.
- Automated source and production checks assert the marketing cleanup while preserving the existing legal disclosure for now.
- **PR #35 stays draft/unmerged; production release remains on HOLD** until other release gates and correspondence acceptance are complete.

No private address, customer identifiers, legal registration records, credentials or speculative compliance assertions belong in this handoff.
