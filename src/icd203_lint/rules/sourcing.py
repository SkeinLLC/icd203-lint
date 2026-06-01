"""Rule: single-source-overconfidence.

Flags moderate or high confidence claims that are not corroborated by at
least two distinct sources in a small window around the claim.

The detector uses four signals, in order:

  1. Anti-corroboration: words like "single", "lone", "sole", "one" right
     before a source noun ("a single Mandiant blog post"). When present,
     the claim is single-source by the analyst's own admission. Flag.

  2. Corroboration phrase: "corroborating", "corroborated", "joint",
     "multiple", "also reported by", and so on. When present in the
     window, the claim is multi-source. Skip.

  3. Distinct vendor names. If two or more distinct vendor names appear in
     the window, skip.

  4. Citation count. Two or more markdown citations / footnote refs in the
     window also count as multi-source.

If none of the multi-source signals fire, the claim is single-source and
gets flagged.

ICD-203 §2(a): source quality and credibility.
"""

from __future__ import annotations

import re

from icd203_lint.core import Document, Finding, Severity
from icd203_lint.rules.base import Rule, VENDOR_SOURCE_RE

_CITATION_RE = re.compile(r"\[\^[\w-]+\]|\[[^\]]+\]\([^)]+\)")
_HIGH_OR_MOD_CONF_RE = re.compile(
    r"\b(?:moderate|high)\s+confidence\b"
    r"|\b(?:moderate|high)-confidence\b"
    r"|\bwith\s+(?:moderate|high)\s+confidence\b",
    re.IGNORECASE,
)

_ANTI_CORROB_RE = re.compile(
    r"\b(?:single|lone|sole|one)\s+"
    r"(?:[A-Z][\w-]*\s+)?"
    r"(?:[A-Z][\w-]*\s+)?"
    r"(?:report|advisory|blog|post|paper|writeup|study|note|source|signal|tip|vendor)\b",
    re.IGNORECASE,
)

_CORROB_RE = re.compile(
    r"\b(?:corroborating|corroborated|corroboration"
    r"|joint(?:ly)?(?:\s+(?:advisory|reporting|report))?"
    r"|two\s+independent|three\s+independent|multiple\s+independent"
    r"|multiple\s+(?:sources|reports|advisories|vendors)"
    r"|cross-?referenced|cross-?checked"
    r"|also\s+reported\s+by|separately\s+confirmed)\b",
    re.IGNORECASE,
)


def _distinct_vendors(text: str) -> int:
    vendors = {m.group(0).lower().replace(" ", "") for m in VENDOR_SOURCE_RE.finditer(text)}
    return len(vendors)


class SingleSourceOverconfidenceRule(Rule):
    id = "single-source-overconfidence"
    name = "Moderate or high confidence on apparently single-source claim"
    description = (
        "Moderate / high confidence requires corroboration. If only one distinct "
        "source is in the window, drop to low confidence or add a second source. "
        "ICD-203 §2(a)."
    )
    severity = Severity.WARN

    def check(self, document: Document) -> list[Finding]:
        out: list[Finding] = []
        sents = document.sentences
        for idx, sent in enumerate(sents):
            if not _HIGH_OR_MOD_CONF_RE.search(sent.text):
                continue
            window = sent.text
            if idx > 0:
                window = sents[idx - 1].text + " " + window
            if idx + 1 < len(sents):
                window += " " + sents[idx + 1].text

            # 1. Anti-corroboration wins.
            if _ANTI_CORROB_RE.search(window):
                out.append(
                    self.finding(
                        sent,
                        "Moderate / high confidence claim that names a single source "
                        "by its own admission ('single', 'lone', or 'sole'). Add a second "
                        "independent source or drop to low confidence.",
                    )
                )
                continue

            # 2. Explicit corroboration phrase.
            if _CORROB_RE.search(window):
                continue

            # 3. Two or more distinct vendor names.
            n_vendors = _distinct_vendors(window)
            if n_vendors >= 2:
                continue

            # 4. Two or more citations.
            n_citations = len(_CITATION_RE.findall(window))
            if n_citations >= 2:
                continue

            out.append(
                self.finding(
                    sent,
                    f"Moderate / high confidence claim backed by only {n_vendors} distinct "
                    "vendor source(s) and no corroboration phrase. Cite a second independent "
                    "source or drop to low confidence.",
                )
            )
        return out
