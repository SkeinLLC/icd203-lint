"""Rule registry. Add a new rule here to make it available to the CLI."""

from __future__ import annotations

from icd203_lint.rules.assessment import AssessmentNoConfidenceRule
from icd203_lint.rules.attribution import AttributionUnsourcedRule
from icd203_lint.rules.base import Rule
from icd203_lint.rules.quotes import QuoteUnattributedRule
from icd203_lint.rules.sourcing import SingleSourceOverconfidenceRule
from icd203_lint.rules.tense import FutureUnhedgedRule

_RULES: list[type[Rule]] = [
    AssessmentNoConfidenceRule,
    AttributionUnsourcedRule,
    SingleSourceOverconfidenceRule,
    FutureUnhedgedRule,
    QuoteUnattributedRule,
]


def all_rules() -> list[Rule]:
    """Return one fresh instance of every registered rule."""
    return [cls() for cls in _RULES]


def get_rule(rule_id: str) -> Rule | None:
    for cls in _RULES:
        if cls.id == rule_id:
            return cls()
    return None


def rule_ids() -> list[str]:
    return [cls.id for cls in _RULES]


def rule_catalog() -> list[dict]:
    return [
        {
            "id": cls.id,
            "name": cls.name,
            "description": cls.description,
            "severity": cls.severity.value,
        }
        for cls in _RULES
    ]
