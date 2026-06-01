"""icd203-lint: a linter for analytic writing.

Flags ICD-203 violations in markdown and plain-text analytic reports:
missing confidence levels on assessments, unsourced attribution claims,
single-source overconfidence, unhedged future-tense projections, and
direct quotes without attribution.

Public API:
    from icd203_lint import lint_text, lint_file, all_rules, Finding, Severity
"""

from icd203_lint.core import (
    Document,
    Finding,
    Severity,
    lint_file,
    lint_text,
    split_sentences,
)
from icd203_lint.registry import all_rules, get_rule

__all__ = [
    "Document",
    "Finding",
    "Severity",
    "all_rules",
    "get_rule",
    "lint_file",
    "lint_text",
    "split_sentences",
]

__version__ = "0.1.0"
