"""Rule: attribution-unsourced.

Flags actor naming that is not accompanied by a TTP fingerprint, a vendor
report, or another sourcing chain in the same or an adjacent sentence.

This is the rule that catches "Lazarus is responsible" with nothing behind
it. ICD-203 §2(a), source credibility, and §2(c), distinguishing intelligence
from judgment.
"""

from __future__ import annotations

from icd203_lint.core import Document, Finding, Severity
from icd203_lint.rules.base import (
    ACTOR_RE,
    Rule,
    has_sourcing,
)


# Phrases that strengthen the attribution claim into something requiring sourcing.
_ATTRIBUTION_VERBS = (
    "attributed",
    "is responsible",
    "are responsible",
    "is behind",
    "are behind",
    "conducted by",
    "carried out by",
    "linked to",
    "tied to",
    "the work of",
    "operated by",
    "associated with",
)


class AttributionUnsourcedRule(Rule):
    id = "attribution-unsourced"
    name = "Attribution claim without TTP or sourcing chain"
    description = (
        "Naming a threat actor demands a defensible basis: a TTP overlap, "
        "infrastructure overlap, recovered artifact, or a cited report. "
        "ICD-203 §2(a) and §2(c)."
    )
    severity = Severity.ERROR

    def check(self, document: Document) -> list[Finding]:
        out: list[Finding] = []
        sents = document.sentences
        for idx, sent in enumerate(sents):
            actor_hit = ACTOR_RE.search(sent.text)
            if not actor_hit:
                continue
            lower = sent.text.lower()
            is_attribution = any(v in lower for v in _ATTRIBUTION_VERBS) or _looks_like_blame(sent.text)
            if not is_attribution:
                continue

            # Sourcing can live in the same sentence, the previous sentence, or the next one.
            window_text = sent.text
            if idx > 0:
                window_text += " " + sents[idx - 1].text
            if idx + 1 < len(sents):
                window_text += " " + sents[idx + 1].text

            if has_sourcing(window_text):
                continue

            out.append(
                self.finding(
                    sent,
                    f"Attribution to '{actor_hit.group(0)}' without a TTP or sourcing chain "
                    "in this or an adjacent sentence. Cite a report, an ATT&CK technique, "
                    "or an infrastructure/code overlap.",
                )
            )
        return out


def _looks_like_blame(text: str) -> bool:
    """Heuristic: sentence has actor + verb-of-action without sourcing."""
    lower = text.lower()
    blame_verbs = (
        " targeted ",
        " hit ",
        " breached ",
        " compromised ",
        " deployed ",
        " ran ",
        " operated ",
        " launched ",
        " conducted ",
    )
    return any(v in lower for v in blame_verbs)
