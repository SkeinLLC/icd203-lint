# Changelog

All notable changes to this project will be documented here. Format: [Keep a Changelog](https://keepachangelog.com/). Versioning: [SemVer](https://semver.org/).

## [0.1.0] - 2026-06-01

### Added
- Five default rules: `assessment-no-confidence`, `attribution-unsourced`, `single-source-overconfidence`, `future-unhedged`, `quote-unattributed`.
- CLI with file, directory, and stdin input. Text, JSON, SARIF, and GitHub Actions output formats. Per-rule selection and ignore flags. Severity floor with `info` / `warn` / `error`. Inline directive support (`<!-- icd203-lint: ignore=rule-id -->`).
- Markdown-aware sentence parsing: skips fenced code blocks, inline code, headings, tables, and HTML comments.
- 20 test fixtures (10 clean, 10 with violations) covering each rule.
- GitHub Action (`action.yml`) and pre-commit hook (`.pre-commit-hooks.yaml`) wrappers.
- Long-form primer (`docs/icd203-primer.md`) on ICD-203 for analysts outside the IC.

### Known limitations
- The vendor name list in `rules/base.py` is opinionated and U.S./U.K.-centric. PRs welcome for Asia-Pacific vendor coverage.
- The attribution rule's actor list is hand-maintained. Roughly current as of mid-2026; long tail of less common names is incomplete.
- No `analysis-of-alternatives` rule yet (ICD-203 §2(d)). Tracked under the roadmap.
