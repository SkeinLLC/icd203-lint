"""Rule base class and shared regex helpers."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from icd203_lint.core import Document, Finding, Severity, Sentence


class Rule(ABC):
    """Base class for every lint rule."""

    id: str = ""
    name: str = ""
    description: str = ""
    severity: Severity = Severity.WARN

    @abstractmethod
    def check(self, document: Document) -> list[Finding]:
        ...

    def finding(self, sentence: Sentence, message: str) -> Finding:
        return Finding(
            rule_id=self.id,
            message=message,
            severity=self.severity,
            line=sentence.line,
            column=sentence.column,
            snippet=sentence.text[:200],
        )


# --- Shared vocabulary patterns ---------------------------------------------

ESTIMATIVE_PATTERNS = [
    r"almost\s+no\s+chance",
    r"\bremote\b",
    r"very\s+unlikely",
    r"highly\s+improbable",
    r"\bunlikely\b",
    r"\bimprobable\b",
    r"roughly\s+even\s+(?:chance|odds)",
    r"\blikely\b",
    r"\bprobable\b",
    r"\bprobably\b",
    r"very\s+likely",
    r"highly\s+probable",
    r"almost\s+certain(?:ly)?",
    r"nearly\s+certain(?:ly)?",
]
ESTIMATIVE_RE = re.compile("|".join(ESTIMATIVE_PATTERNS), re.IGNORECASE)

CONFIDENCE_RE = re.compile(
    r"\b(?:low|moderate|high)\s+confidence\b"
    r"|\bwith\s+(?:low|moderate|high)\s+confidence\b"
    r"|\b(?:low|moderate|high)-confidence\b"
    r"|\bconfidence\s*[:=]\s*(?:low|moderate|high)\b",
    re.IGNORECASE,
)

ASSESSMENT_OPENERS_RE = re.compile(
    r"(?:^|[^A-Za-z0-9])"
    r"(?:we\s+(?:assess|judge|estimate|conclude)"
    r"|our\s+(?:assessment|judgment|estimate)"
    r"|(?:the\s+)?(?:bottom\s+line|key\s+judgment|main\s+judgment)"
    r"|i\s+(?:assess|judge|estimate))",
    re.IGNORECASE,
)

SOURCING_RE = re.compile(
    r"\b(?:based\s+on|according\s+to|per\s+[A-Z]|reported\s+by|cited\s+in"
    r"|attributed\s+by|drawing\s+on|drawn\s+from|sourced\s+from)\b"
    r"|\[[^\]]+\]\([^)]+\)"
    r"|\[\^[\w-]+\]"
    r"|\(\s*(?:see|cf\.?|ref\.?)\s+[^)]+\)"
    r"|\bCVE-\d{4}-\d+\b"
    r"|\bT\d{4}(?:\.\d+)?\b"
    r"|\b(?:report|advisory|blog|writeup|post|paper|study|note)\b",
    re.IGNORECASE,
)

VENDOR_SOURCE_RE = re.compile(
    r"\b(?:Mandiant|FireEye|CrowdStrike|Microsoft|Recorded\s+Future"
    r"|Kaspersky|ESET|Sophos|Palo\s+Alto|Unit\s*42|SecureWorks|Symantec|Cisco\s+Talos|Talos"
    r"|Trellix|Trend\s+Micro|Volexity|Proofpoint|Mimecast|Cloudflare|Akamai"
    r"|CISA|NCSC|ENISA|JPCERT|ACSC|FBI|NSA|MS-ISAC"
    r"|Anthropic|Google\s+TAG|TAG|Citizen\s+Lab|PwC|Deloitte|KPMG|EY)\b",
)

KNOWN_ACTORS = [
    r"\b(?:Storm|Sangria\s+Tempest|Mint\s+Sandstorm|Aqua\s+Blizzard|Forest\s+Blizzard"
    r"|Midnight\s+Blizzard|Cadet\s+Blizzard|Volt\s+Typhoon|Salt\s+Typhoon|Flax\s+Typhoon"
    r"|Brass\s+Typhoon|Charcoal\s+Typhoon|Silk\s+Typhoon)(?:-\d+)?\b",
    r"\b(?:APT|FIN|UNC|TA)\d{1,5}\b",
    r"\b(?:Fancy\s+Bear|Cozy\s+Bear|Voodoo\s+Bear|Wizard\s+Spider|Mummy\s+Spider"
    r"|Carbon\s+Spider|Indrik\s+Spider|Lazarus|Andariel|Bluenoroff|Kimsuky"
    r"|Sandworm|Turla|Equation|Lapsus\$|Lapsus|Conti|Black\s+Basta|BlackCat|ALPHV"
    r"|LockBit|REvil|Clop|Cl0p|Akira|Royal|Play|RansomHub|Scattered\s+Spider"
    r"|Muddy\s?Water|MuddyWater|OilRig|Charming\s+Kitten|APT-?C-\d+)\b",
]
ACTOR_RE = re.compile("|".join(KNOWN_ACTORS), re.IGNORECASE)

FUTURE_RE = re.compile(
    r"\b(?:will|shall|won't|wo\s?n['']t)\s+(?:[a-z]+\s+)?[a-z]+"
    r"|\b(?:is|are|will\s+be)\s+going\s+to\s+[a-z]+",
    re.IGNORECASE,
)

QUOTE_RE = re.compile(
    r"[“\"]"
    r"((?:[^\"“”\n]{0,400}?))"
    r"[”\"]",
)

QUOTE_ATTR_RE = re.compile(
    r"\b(?:said|wrote|stated|told|writes|notes|noted|argues|argued|reports|reported"
    r"|according\s+to"
    r"|per\s+(?:the\s+|a\s+|an\s+|its\s+|their\s+)?[A-Z][\w-]*"
    r"|in\s+a\s+(?:report|statement|interview|post|blog|writeup|paper|study)"
    r"|in\s+the\s+(?:report|statement|interview|post|blog|writeup|paper|study|advisory))\b",
    re.IGNORECASE,
)


def has_estimative(text: str) -> bool:
    return bool(ESTIMATIVE_RE.search(text))


def has_confidence(text: str) -> bool:
    return bool(CONFIDENCE_RE.search(text))


def has_sourcing(text: str) -> bool:
    return bool(SOURCING_RE.search(text) or VENDOR_SOURCE_RE.search(text))


def is_assessment_sentence(text: str) -> bool:
    return bool(ASSESSMENT_OPENERS_RE.search(text))


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w$-]+\b", text))
