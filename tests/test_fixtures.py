"""Golden tests against the fixtures directory.

Every file under tests/fixtures/good must produce zero findings.
Every file under tests/fixtures/bad must produce at least one finding,
and the filename hints which rule should fire.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from icd203_lint import lint_file

FIXTURES = Path(__file__).parent / "fixtures"

# Map filename-prefix hints to expected rule ids. Used for "bad" fixtures so we
# don't just confirm "some rule fires" but the right one.
BAD_HINTS = {
    "01-assess-no-confidence": "assessment-no-confidence",
    "02-our-judgment-no-confidence": "assessment-no-confidence",
    "03-attribution-bare-blame": "attribution-unsourced",
    "04-attribution-no-context": "attribution-unsourced",
    "05-single-source-high": "single-source-overconfidence",
    "06-single-source-moderate": "single-source-overconfidence",
    "07-future-unhedged": "future-unhedged",
    "08-future-bare-shall": "future-unhedged",
    "09-quote-unattributed": "quote-unattributed",
    "10-mixed-bad-report": None,  # multiple rules; just ensure non-empty
}


@pytest.mark.parametrize("md", sorted((FIXTURES / "good").glob("*.md")))
def test_good_fixtures_have_no_findings(md: Path):
    findings = lint_file(md)
    assert findings == [], (
        f"expected no findings in {md.name}, got: "
        + ", ".join(f"{f.rule_id}@{f.line}" for f in findings)
    )


@pytest.mark.parametrize("md", sorted((FIXTURES / "bad").glob("*.md")))
def test_bad_fixtures_have_findings(md: Path):
    findings = lint_file(md)
    assert findings, f"expected at least one finding in {md.name}"
    expected = BAD_HINTS.get(md.stem)
    if expected is None:
        return
    rule_ids = {f.rule_id for f in findings}
    assert expected in rule_ids, (
        f"expected rule '{expected}' to fire in {md.name}, "
        f"got: {sorted(rule_ids)}"
    )
