"""Rule: quote-unattributed.

Flags direct quotations of four or more words that are not accompanied by
an attribution phrase or speaker name in the same or adjacent sentence.

ICD-203 §2(a): properly describes quality and credibility of underlying
sources. Paraphrase or attribute.
"""

from __future__ import annotations

import re

from icd203_lint.core import Document, Finding, Severity
from icd203_lint.rules.base import QUOTE_ATTR_RE, QUOTE_RE, Rule, word_count


_MIN_QUOTE_WORDS = 4

# Short markdown emphasis quotes inside running prose: 'the "Storm-0501" actor'
# are already <4 words so the threshold above handles them.

# Section heading inside a quote (rare) gets skipped.
_SECTION_QUOTE_RE = re.compile(r"\b(?:section|chapter|appendix)\b", re.IGNORECASE)


class QuoteUnattributedRule(Rule):
    id = "quote-unattributed"
    name = "Direct quote without attribution"
    description = (
        "Direct quotations of four or more words should be attributed to a "
        "named speaker, document, or report. Paraphrase if attribution isn't "
        "possible. ICD-203 §2(a)."
    )
    severity = Severity.WARN

    def check(self, document: Document) -> list[Finding]:
        out: list[Finding] = []
        sents = document.sentences
        for idx, sent in enumerate(sents):
            for m in QUOTE_RE.finditer(sent.text):
                inner = m.group(1).strip()
                if word_count(inner) < _MIN_QUOTE_WORDS:
                    continue
                # Build a window: previous sentence, this sentence, next sentence.
                window = sent.text
                if idx > 0:
                    window = sents[idx - 1].text + " " + window
                if idx + 1 < len(sents):
                    window += " " + sents[idx + 1].text
                if QUOTE_ATTR_RE.search(window):
                    continue
                # Allow section/chapter quotes ("see section \"X\"").
                if _SECTION_QUOTE_RE.search(window):
                    continue
                out.append(
                    self.finding(
                        sent,
                        f"Direct quote ({word_count(inner)} words) without attribution. "
                        "Name a speaker, a document, or paraphrase.",
                    )
                )
        return out
