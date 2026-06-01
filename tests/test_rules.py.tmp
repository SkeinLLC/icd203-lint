"""Tests for individual rules."""

from __future__ import annotations

from icd203_lint import lint_text
from icd203_lint.rules.assessment import AssessmentNoConfidenceRule
from icd203_lint.rules.attribution import AttributionUnsourcedRule
from icd203_lint.rules.quotes import QuoteUnattributedRule
from icd203_lint.rules.sourcing import SingleSourceOverconfidenceRule
from icd203_lint.rules.tense import FutureUnhedgedRule


# ---------------------------------------------------------------------------
# assessment-no-confidence
# ---------------------------------------------------------------------------

def test_assessment_without_confidence_flags():
    text = "We assess that the operators are based in Brazil."
    findings = lint_text(text, rules=[AssessmentNoConfidenceRule()])
    assert len(findings) == 1
    assert findings[0].rule_id == "assessment-no-confidence"


def test_assessment_with_low_confidence_passes():
    text = "We assess with low confidence that the operators are based in Brazil."
    findings = lint_text(text, rules=[AssessmentNoConfidenceRule()])
    assert findings == []


def test_assessment_with_high_confidence_passes():
    text = (
        "Our assessment, with high confidence, is that the regional subsidiary "
        "was the entry vector."
    )
    findings = lint_text(text, rules=[AssessmentNoConfidenceRule()])
    assert findings == []


def test_non_assessment_sentence_is_ignored():
    text = "The patch was released on May 4."
    findings = lint_text(text, rules=[AssessmentNoConfidenceRule()])
    assert findings == []


def test_we_judge_without_confidence_flags():
    text = "We judge that the campaign will continue."
    findings = lint_text(text, rules=[AssessmentNoConfidenceRule()])
    assert len(findings) == 1


# ---------------------------------------------------------------------------
# attribution-unsourced
# ---------------------------------------------------------------------------

def test_bare_attribution_flags():
    text = "Lazarus is responsible for the wiper deployment."
    findings = lint_text(text, rules=[AttributionUnsourcedRule()])
    assert len(findings) == 1
    assert findings[0].rule_id == "attribution-unsourced"


def test_attribution_with_vendor_source_passes():
    text = (
        "The intrusion is the work of APT41 based on a CrowdStrike report from March "
        "and overlap with three ATT&CK techniques."
    )
    findings = lint_text(text, rules=[AttributionUnsourcedRule()])
    assert findings == []


def test_attribution_with_adjacent_sourcing_passes():
    text = (
        "Mandiant published a writeup last week. APT41 conducted the campaign. "
        "The report details infrastructure overlap with the 2024 cluster."
    )
    findings = lint_text(text, rules=[AttributionUnsourcedRule()])
    assert findings == []


def test_bare_actor_action_flags():
    text = "Volt Typhoon targeted the regional utility in April."
    findings = lint_text(text, rules=[AttributionUnsourcedRule()])
    assert len(findings) == 1


def test_no_actor_no_flag():
    text = "The group conducted the campaign."
    findings = lint_text(text, rules=[AttributionUnsourcedRule()])
    assert findings == []


# ---------------------------------------------------------------------------
# single-source-overconfidence
# ---------------------------------------------------------------------------

def test_high_confidence_single_source_flags():
    text = (
        "We assess with high confidence that the group will pivot to financial services, "
        "based on a single Mandiant blog post."
    )
    findings = lint_text(text, rules=[SingleSourceOverconfidenceRule()])
    assert len(findings) == 1
    assert findings[0].rule_id == "single-source-overconfidence"


def test_high_confidence_multi_source_passes():
    text = (
        "We assess with high confidence that the actor uses LOTL techniques, based on "
        "Microsoft Threat Intelligence reporting, a CISA advisory, and a Mandiant follow-up."
    )
    findings = lint_text(text, rules=[SingleSourceOverconfidenceRule()])
    assert findings == []


def test_low_confidence_single_source_is_ok():
    text = (
        "We assess with low confidence that the loader is a successor to SmokeLoader, "
        "based on a single Volexity blog post."
    )
    findings = lint_text(text, rules=[SingleSourceOverconfidenceRule()])
    assert findings == []


# ---------------------------------------------------------------------------
# future-unhedged
# ---------------------------------------------------------------------------

def test_bare_future_flags():
    text = "The group will pivot to financial services next quarter."
    findings = lint_text(text, rules=[FutureUnhedgedRule()])
    assert len(findings) == 1
    assert findings[0].rule_id == "future-unhedged"


def test_estimative_future_passes():
    text = "The group will likely pivot to financial services next quarter."
    findings = lint_text(text, rules=[FutureUnhedgedRule()])
    assert findings == []


def test_very_likely_future_passes():
    text = "Operators are very likely to weaponize the CVE within 30 days."
    findings = lint_text(text, rules=[FutureUnhedgedRule()])
    assert findings == []


def test_operational_future_passes():
    text = "CVE-2026-1234 will be added to the CISA KEV catalog on June 5."
    findings = lint_text(text, rules=[FutureUnhedgedRule()])
    assert findings == []


def test_conditional_future_passes():
    text = "If the operator persists, the group will rotate infrastructure."
    findings = lint_text(text, rules=[FutureUnhedgedRule()])
    assert findings == []


# ---------------------------------------------------------------------------
# quote-unattributed
# ---------------------------------------------------------------------------

def test_unattributed_quote_flags():
    text = (
        'The actor "maintains long-term persistence through valid accounts and built-in tools."'
    )
    findings = lint_text(text, rules=[QuoteUnattributedRule()])
    assert len(findings) == 1
    assert findings[0].rule_id == "quote-unattributed"


def test_attributed_quote_passes():
    text = (
        'According to CISA, the actor "maintains long-term persistence '
        'through valid accounts and built-in tools."'
    )
    findings = lint_text(text, rules=[QuoteUnattributedRule()])
    assert findings == []


def test_short_quote_passes():
    text = 'The actor used a "Storm-0501" variant of the loader.'
    findings = lint_text(text, rules=[QuoteUnattributedRule()])
    assert findings == []


def test_per_report_attribution_passes():
    text = (
        'Per the Mandiant M-Trends 2026 report, "median dwell time fell '
        'to nine days for ransomware intrusions this year."'
    )
    findings = lint_text(text, rules=[QuoteUnattributedRule()])
    assert findings == []
