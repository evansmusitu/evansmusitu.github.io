"""Fail-closed governance checks for the unified corporate release.

The source tests can be green while business/legal/hosted approval remains HOLD.
Keep evidence references non-personal; never put mailbox conversations, identities,
registration records, reviewer identities or staging secrets in public Git.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
RELEASE = json.loads((ROOT / "RELEASE_GATES.json").read_text(encoding="utf-8"))
CANDIDATE = RELEASE["current_unified_candidate"]


def test_governance_stays_hold_despite_source_ci_success():
    assert RELEASE["production_release_decision"] == "HOLD"
    assert RELEASE["owner_approved_deployment"] is False
    assert CANDIDATE["production_approved"] is False
    assert CANDIDATE["deployed"] is False
    assert CANDIDATE["live_accepted"] is False
    assert CANDIDATE["source_status"] == "automated_source_qualified_at_recorded_commit_only"
    assert "require fresh exact-commit CI" in CANDIDATE["evidence_caveat"]


def test_provenance_does_not_misstate_exact_candidate():
    assert CANDIDATE["release_pr"] == 39
    assert CANDIDATE["release_branch"] == "corporate-unified-release-candidate-20261120"
    assert CANDIDATE["last_verified_source_ci_run"] == 44695006097
    assert re.fullmatch(r"[0-9a-f]{40}", CANDIDATE["last_verified_source_commit"])
    assert CANDIDATE["scope"] == "corporate_site_only"
    assert CANDIDATE["core_routes"] == 34
    assert CANDIDATE["optional_phase03_routes"] == 15
    assert CANDIDATE["phase03_default_publish_flag"] == "0"
    assert "historical" in RELEASE["release_history_note"].lower()


def test_release_requires_independent_non_source_acceptance():
    mandatory = (
        "human_real_device_acceptance",
        "manual_accessibility_acceptance",
        "legal_privacy_operator_signoff",
        "actual_hosted_candidate_security_and_performance",
        "external_origin_support_thread_and_authenticated_reply",
        "production_restore_and_rollback_rehearsal",
        "international_editorial_and_language_review",
    )
    assert all(CANDIDATE[name] == "not_evidenced" for name in mandatory)
    assert "Do not merge, deploy" in CANDIDATE["release_instruction"]
    # External review receipts belong in approved private storage, not public Git.
    assert "@" not in json.dumps(CANDIDATE)


def test_phase03_default_off_and_ci_never_deploys():
    build = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
    assert "os.environ.get('MUSITU_PUBLISH_PHASE03','0')" in build
    assert "'production_approved':False" in build
    workflow = (ROOT.parent / ".github/workflows/corporate-phase03-seo.yml").read_text(encoding="utf-8")
    assert "tests/test_release_governance.py" in workflow
    assert not re.search(r"(?i)\\b(?:wrangler\\s+pages\\s+deploy|cloudflare\\s+pages\\s+deploy)\\b", workflow)


def test_marketing_location_neutral_and_legal_text_not_replaced():
    footer = (ROOT / "templates/footer.html").read_text(encoding="utf-8")
    assert "International outlook" in footer
    assert not re.search(r"(?i)\\b(?:village|road|street|residential address|incorporation number)\\b", footer)
    pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
    assert "support@mftintelligence.com" in pages["/contact/"]["main"]
    for route in ("/legal/privacy/", "/legal/terms/"):
        page = pages[route]["main"].lower()
        assert "support@mftintelligence.com" in page
        assert "address" in page and "musitu" in page
    assert "registration number" not in pages["/"]["main"].lower()
