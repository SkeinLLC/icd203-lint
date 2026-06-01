# Contributing

Thanks for thinking about it. A few notes to make the contribution flow smooth.

## Setup

```
git clone https://github.com/SkeinLLC/icd203-lint
cd icd203-lint
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
```

If pytest is green and ruff is clean, you have a working dev setup.

## Adding a new rule

Three steps.

1. Create the rule module under `src/icd203_lint/rules/`. Subclass `Rule` from `rules.base`. Give it a unique `id`, a short `name`, a one-paragraph `description`, and a `severity` from `Severity.INFO`, `WARN`, or `ERROR`. Implement `check(self, document)` returning a list of `Finding`s.

2. Register it. Add the class to the `_RULES` list in `src/icd203_lint/registry.py`. The order in that list is the order findings are emitted; keep related rules near each other.

3. Add fixtures. Drop at least one positive case under `tests/fixtures/good/` (expected to produce zero findings) and at least one negative case under `tests/fixtures/bad/` (expected to fire the new rule). The filename of the bad fixture should hint at the rule id; the test in `tests/test_fixtures.py` uses the prefix to verify the right rule fires. Also add direct unit tests in `tests/test_rules.py`.

The bar for a new rule: it should be defensible against a working analyst's pushback. If a rule's false-positive rate is going to be high, it should be `info` severity, opt-in, or clearly fixable with an inline directive. Don't ship rules that punish good writing.

## Tuning an existing rule

Tuning changes need a regression test. If you tighten the assessment-no-confidence rule so it catches one more pattern, write a fixture under `bad/` that shows the new pattern and a fixture under `good/` that shows a similar pattern that should not fire. Without both, the tuning is half a change.

## Style

Ruff is configured in `pyproject.toml`. Run `ruff check src tests` before pushing. Line length is 100. Use double quotes for strings. Prefer regex constants at module top with `re.compile(..., re.IGNORECASE)` over inline patterns inside checks.

Comments are dry by default. Explain the why, not the what. Reference ICD-203 section numbers when relevant ("ICD-203 §2(a)" for sourcing, "§2(b)" for confidence, "§2(c)" for distinguishing intel from judgment, "§2(d)" for analysis of alternatives).

## What we won't merge

- Rules that require a network call or an LLM. The whole point of `icd203-lint` is that it runs offline, in CI, deterministically.
- Rules that depend on heavy NLP libraries (spaCy, NLTK). Keep the install fast and the dependency surface small.
- Rules that overlap substantially with anti-slop or general prose linting. That's a separate repo.

## Questions

Open an issue or start a discussion. PRs that come with a rationale ("here's the pattern, here's a fixture, here's why it matters") get reviewed faster than PRs that only ship code.
