"""Rule: future-unhedged.

Flags future-tense sentences that read as analytic predictions but lack
an estimative qualifier from the ICD-203 ladder.

"The group will pivot to financial services" is a bare-future projection.
"The group will likely pivot to financial services" is a real prediction
the reader can argue with. The rule asks for the latter.

ICD-203 §2(b): expressing and explaining uncertainties.
"""

from __future__ import annotations

import re

from icd203_lint.core import Document, Finding, Severity
from icd203_lint.rules.base import (
    ACTOR_RE,
    FUTURE_RE,
    Rule,
    has_estimative,
)


# Subjects that suggest a real predictive claim (vs. operational announcement).
_PREDICTIVE_SUBJECT_RE = re.compile(
    r"\b(?:actor|actors|group|operator|operators|adversar(?:y|ies)|attacker|attackers"
    r"|threat\s+actor|threat\s+group|campaign|campaigns|operators?|crew"
    r"|ransomware|malware|botnet|infostealer|loader|exploit|exploits"
    r"|we|they|the\s+group|the\s+actors?)\b",
    re.IGNORECASE,
)

# Operational scheduled events that don't need estimative language.
_OPERATIONAL_RE = re.compile(
    r"\b(?:patch|update|release|GA|deprecate(?:d|s)?|sunset|EOL|end\s+of\s+life"
    r"|will\s+be\s+added\s+to\s+KEV|will\s+be\s+published|will\s+be\s+released)\b"
    r"|\bCVE-\d{4}-\d+\b",
    re.IGNORECASE,
)

# Modal "would" / "could" / "may" / "might" inside a conditional are not bare future.
_CONDITIONAL_RE = re.compile(r"\b(?:if|unless|when|once|should)\b", re.IGNORECASE)


class FutureUnhedgedRule(Rule):
    id = "future-unhedged"
    name = "Future-tense prediction without an estimative qualifier"
    description = (
        "Bare future-tense projections about adversary behavior should be "
        "calibrated with estimative language (likely / probable / very likely / "
        "roughly even / unlikely / almost certain). ICD-203 §2(b)."
    )
    severity = Severity.WARN

    def check(self, document: Document) -> list[Finding]:
        out: list[Finding] = []
        for sent in document.sentences:
            if not FUTURE_RE.search(sent.text):
                continue
            if has_estimative(sent.text):
                continue
            # Conditional clauses ("if X, the group will Y") are weaker hits; skip.
            if _CONDITIONAL_RE.search(sent.text):
                continue
            # Skip operational announcements about patches/releases/CVE schedules.
            if _OPERATIONAL_RE.search(sent.text):
                continue
            # Only flag if there's a predictive subject or a named actor.
            if not (_PREDICTIVE_SUBJECT_RE.search(sent.text) or ACTOR_RE.search(sent.text)):
                continue
            out.append(
                self.finding(
                    sent,
                    "Future-tense projection without an estimative qualifier. Add a "
                    "phrase from the ICD-203 ladder (e.g. 'likely', 'very likely', "
                    "'roughly even chance').",
                )
            )
        return out
