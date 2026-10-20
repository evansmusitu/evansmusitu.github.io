# MUSITU Intelligence — Reproducible Evidence Chain v1

This is an **offline evidence selection replay** capability; it is not a digital signature, cloud workspace, independently fact-checked research result, or proof of a document's authorship.

Use **Documents** → choose 1–3 originals → enter a question → **Preview local evidence** → **Save reproducible evidence chain (.json)**. To verify on another visit or device, supply the original files and click **Independently recheck evidence chain**. No prior conversation, server login, document preview, AI call, third-party data upload or account is required.

Each JSON file holds:
- The original question in **plaintext**, with filenames, byte counts and SHA-256 hashes. Do not share if sensitive.
- Original extracted character count, scanned window count and lexical keyword match/fallback status.
- SHA-256 of the actual selected bounded excerpt and hashes with character offsets for selected passages (without passage text).
- A deterministic extractor and BM25 method version identifier.

The verifier checks original SHA-256 and then independently re-extracts text and re-runs the exact bounded BM25 passage selection. It confirms byte equality **and** reproducibility of selected excerpts and source positions. Differences can reflect a modified document or a future parser/retrieval-version change.

Bounds remain 1–3 local files; TXT/MD/CSV/JSON 64 KiB each, searchable PDF 2 MiB / 20 pages, DOCX 1 MiB; extracted text <=160k characters/file and submitted excerpts up to 4,800 characters for one file or 1,500 per file for comparisons. Scanned/encrypted PDFs are unsupported. Full originals are not saved or sent to MUSITU's backend. The manifest includes no document excerpts but includes plaintext question and metadata.

**Security disclaimer:** The receipt is not signed or encrypted; an adversary can forge a new bundle and files. Matching hashes establish local byte equality with the supplied files, not publisher authenticity, a trusted timestamp, independent fact checking, or a validated source assertion. Browser or operating system compromise can invalidate these assurances.
