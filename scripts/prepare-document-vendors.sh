#!/usr/bin/env bash
set -euo pipefail
# The exact package versions are pinned in package.json.
# All parsing code is hosted from the same GitHub Pages origin, not a remote CDN.
mkdir -p assets/vendor
test -s node_modules/pdfjs-dist/build/pdf.mjs
test -s node_modules/pdfjs-dist/build/pdf.worker.mjs
test -s node_modules/mammoth/mammoth.browser.min.js
cp node_modules/pdfjs-dist/build/pdf.mjs assets/vendor/pdf.mjs
cp node_modules/pdfjs-dist/build/pdf.worker.mjs assets/vendor/pdf.worker.mjs
cp node_modules/mammoth/mammoth.browser.min.js assets/vendor/mammoth.browser.min.js
test -s assets/vendor/pdf.mjs
test -s assets/vendor/pdf.worker.mjs
test -s assets/vendor/mammoth.browser.min.js
echo "Local self-hosted PDF.js and Mammoth browser extraction libraries prepared."
sha256sum assets/vendor/*.mjs assets/vendor/mammoth.browser.min.js
