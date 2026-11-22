"""Verify the published static artifact excludes source-side internal material.

This does not remove information already published in earlier Git revisions.
Lawful address/operator disclosures in the Privacy Policy and Terms remain intact.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
INTERNAL_NAMES = {
    "RELEASE_GATES.json",
    "phase03-publication-approvals.json",
    "localization-pilot.json",
    "seo-routes.json",
    "research_review.py",
    "RELEASE_REVIEW.md",
}
FORBIDDEN_EXTENSIONS = {".md", ".py", ".pem", ".key", ".env", ".csv", ".zip", ".sqlite"}
SECRET_PATTERNS = (
    re.compile(r"sk-(?:proj|tinyfish|live|test)-[A-Za-z0-9_-]{10,}", re.IGNORECASE),
    re.compile(r"ghp_[A-Za-z0-9_]{25,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{25,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def test_artifact_is_a_static_public_subset_and_not_the_source_repository():
    assert DIST.is_dir()
    files = [p for p in DIST.rglob("*") if p.is_file()]
    assert files
    assert not any(p.suffix.lower() in FORBIDDEN_EXTENSIONS for p in files)
    assert not any(p.name in INTERNAL_NAMES for p in files)
    assert not any("editorial" in p.relative_to(DIST).parts for p in files)
    assert not any("review-artifacts" in p.relative_to(DIST).parts for p in files)
    assert not (DIST / ".github").exists()
    assert not (DIST / "content").exists()
    assert not (DIST / "scripts").exists()
    assert not (DIST / "manifest.json").exists(), "Do not publish release-gate or build provenance fields"
    assert not (DIST / "build-manifest.json").exists()


def test_generated_public_text_has_no_credentials_or_review_only_records():
    allowed_text = {".html", ".js", ".css", ".xml", ".json", ".txt"}
    for path in DIST.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in allowed_text:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in SECRET_PATTERNS:
            assert not pattern.search(text), path.relative_to(DIST)
        assert "private_registration_disclosure" not in text, path.relative_to(DIST)
        assert "CORRESPONDENCE_ADDRESS_PUBLICATION_HANDOFF" not in text, path.relative_to(DIST)
        assert "owner_approved_deployment" not in text, path.relative_to(DIST)


def test_default_review_build_cannot_accidentally_publish_international_routes():
    manifest = json.loads((DIST.parent / "review-artifacts" / "build-manifest.json").read_text(encoding="utf-8"))
    assert manifest["production_approved"] is False
    assert manifest["build_mode"] == "review"
    assert manifest["indexing_enabled"] is False
    assert manifest["route_count"] == 38
    assert manifest["phase03_publication_routes"] == []
    assert manifest["phase03_publication_indexable"] is False
    assert not (DIST / "fr").exists()
    assert not (DIST / "research" / "articles").exists()
    assert not (DIST / "sitemap.xml").exists()
    assert "Disallow: /" in (DIST / "robots.txt").read_text(encoding="utf-8")


if __name__ == "__main__":
    test_artifact_is_a_static_public_subset_and_not_the_source_repository()
    test_generated_public_text_has_no_credentials_or_review_only_records()
    print("Generated artifact publication boundary: PASS (no internal source files or secret patterns)")
