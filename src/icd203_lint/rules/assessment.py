"""Rule: assessment-no-confidence.

Flags sentences that read like analytic judgments (e.g., starting with
"We assess", "Our assessment", "We judge") but do not carry an explicit
confidence level (low / moderate / high).

This is the most-cited ICD-203 standard: every major analytic judgment
should be accompanied by a calibrated confidence statement.
"""

from __future__ import annotations

from icd203_lint.core import Document, Finding, Severity
from icd203_lint.rules.base import (
    Rule,
    has_confidence,
    is_assessment_sentence,
)


class AssessmentNoConfidenceRule(Rule):
    id = "assessment-no-confidence"
    name = "Assessment sentence without a confidence level"
    description = (
        "Sentences that present an analytic judgment should carry an explicit "
        "low / moderate / high confidence label. ICD-203 §2(b)."
    )
    severity = Severity.ERROR

    def check(self, document: Document) -> list[Finding]:
        out: list[Finding] = []
        for sent in document.sentences:
            if not is_assessment_sentence(sent.text):
                continue
            if has_confidence(sent.text):
                continue
            out.append(
                self.finding(
                    sent,
                    "Analytic judgment without explicit confidence (low / moderate / high). "
                    "Add a confidence statement, e.g. 'we assess with moderate confidence...'.",
                )
            )
        return out
