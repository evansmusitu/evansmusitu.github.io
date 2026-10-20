# MUSITU Intelligence — Portable Source Fingerprint Receipt v1

- From Documents mode, select 1–3 files and preview evidence locally.
- Click **Save portable source receipt** to download a deterministic metadata-only JSON receipt.
- Later, select the original files in Documents mode and click **Verify saved receipt** to choose the JSON.
- The browser recomputes each complete original file's SHA-256 and compares it to the receipt. Verification does not require a question, AI request, or login.
- A mismatch means different bytes, filenames or sizes. A match means identical local bytes, **not** verified publisher identity, authenticity, accurate excerpts, truth, or a digital signature.
- JSON receipts contain plaintext filenames, sizes and SHA-256. They are not encrypted, signed, server-stored, timestamp-authoritative, revocable, or cloud-synchronized. Hash values alone should never be treated as a high-security proof of possession.
- Existing encrypted workspace slots and plaintext Markdown evidence packs are unchanged. Never upload confidential documents or API credentials.
- Format name: `musitu.source-fingerprint-receipt.v1`. Strict schema, supported extensions and length limits; extras, duplicates and oversize receipts are rejected before hashing.
