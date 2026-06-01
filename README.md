<!-- icd203-lint: disable-file -->
# icd203-lint

A linter for analytic writing. Flags missing confidence calibration, unsourced attribution, single-source overconfidence, unhedged future-tense projections, and unattributed direct quotes.

Inspired by ICD-203, the Intelligence Community Directive on analytic standards. Built for CTI analysts, vendor researchers, SOC writers, and anyone else who ships analytic prose under uncertainty and would like the prose to hold up under cross-examination.

```
$ icd203-lint advisory.md
advisory.md
  error    5:1   assessment-no-confidence
        Analytic judgment without explicit confidence (low / moderate / high).
        > We assess that Volt Typhoon will continue prepositioning in U.S. networks.
  warn     5:1   future-unhedged
        Future-tense projection without an estimative qualifier.
        > We assess that Volt Typhoon will continue prepositioning in U.S. networks.

icd203-lint: 2 findings in 1 file.
```

## Why bother

Most threat-intel reports skip the parts that make analytic writing reproducible. Confidence calibration is missing or mixed up with likelihood. Attribution gets handed out without a sourcing chain. Moderate-confidence claims rest on a single vendor blog. Future-tense predictions float without estimative language. The result reads as confident, but it does not survive a careful re-read.

ICD-203 fixes this with five habits, applied repeatedly. This linter catches the four or five mistakes that account for most of the slip on a second pass, before the report ships.

The full case for ICD-203 outside the IC is in `docs/icd203-primer.md`. Read that first if the rules below look arbitrary.

## Install

```
pip install icd203-lint
```

Python 3.10 or newer. No required dependencies beyond the standard library. Optional `pip install 'icd203-lint[color]'` adds rich color output.

## Use

```
# lint one file
icd203-lint report.md

# lint a directory tree (recurses into .md, .markdown, .txt)
icd203-lint reports/

# read from stdin
cat advisory.txt | icd203-lint -

# JSON output for piping into tools
icd203-lint reports/ --format json

# SARIF for GitHub code scanning
icd203-lint reports/ --format sarif > findings.sarif

# inline GitHub Actions annotations
icd203-lint reports/ --format github
```

Exit codes: 0 if no findings at or above the severity floor, 1 if findings, 2 on usage error.

## The five default rules

| ID | Severity | What it catches |
|---|---|---|
| `assessment-no-confidence` | error | Sentences that read like analytic judgments ("we assess...", "our assessment...") without a low / moderate / high tag. |
| `attribution-unsourced` | error | Naming a threat actor without a TTP overlap, infrastructure overlap, or cited report in this or an adjacent sentence. |
| `single-source-overconfidence` | warn | Moderate or high confidence claims backed by one source, or qualified by "single" / "lone" / "sole". |
| `future-unhedged` | warn | "The group will pivot..." instead of "the group will likely pivot..." Any bare future-tense projection without estimative language. |
| `quote-unattributed` | warn | Direct quotations of four or more words without a speaker, document, or "according to" marker nearby. |

Run `icd203-lint --list-rules` to see the catalog with full descriptions and severities.

## Selecting and ignoring rules

```
# only run two rules
icd203-lint advisory.md --select assessment-no-confidence --select single-source-overconfidence

# skip a noisy rule
icd203-lint advisory.md --ignore quote-unattributed

# only fail on errors, not warnings
icd203-lint advisory.md --severity error
```

In the document itself, use HTML comments. The directives apply per-line and per-file:

```markdown
<!-- icd203-lint: disable-file=quote-unattributed -->

# Q2 outlook

We assess that operators are based in Brazil. <!-- icd203-lint: ignore=assessment-no-confidence -->
```

## CI integration

### GitHub Actions

Drop this into `.github/workflows/lint.yml`:

```yaml
name: analytic-lint
on: pull_request
jobs:
  icd203:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: SkeinLLC/icd203-lint@v0
        with:
          paths: 'reports/'
          severity: warn
```

The action posts inline annotations on the PR file diff. Configure `select`, `ignore`, `format`, `fail-on-findings`, and `version` via the action inputs (see `action.yml`).

### pre-commit

In `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/SkeinLLC/icd203-lint
    rev: v0.1.0
    hooks:
      - id: icd203-lint
```

There's also an `icd203-lint-strict` variant that only fails on `error` severity, useful when you're rolling this out to a team and want a runway before warnings block commits.

## Output formats

Four output formats, picked by `--format`:

- `text` (default): human-readable, color-aware. Best for local use.
- `json`: a flat array of findings. Easy to grep, easy to script against.
- `sarif`: SARIF 2.1.0. Uploads cleanly to GitHub code scanning, Microsoft Defender for DevOps, and other tools that consume SARIF.
- `github`: GitHub Actions workflow commands. Renders as inline file annotations on PRs.

## What the linter does not do

It does not call any LLM. The rules are deterministic regex + sentence parsing. No network calls, no telemetry, no API keys.

It does not check semantics. A sentence that says "we assess with high confidence that water is wet" passes every rule. The linter catches the patterns that careful editing would catch on a second pass; it does not catch bad judgment.

It does not score writing quality. ICD-203 is about tradecraft, not style. The repo `O2-anti-slop` covers the style side; pair the two.

## Roadmap

- `analysis-of-alternatives`: flag major judgments that don't acknowledge an opposing reading or alternative explanation. ICD-203 §2(d).
- `change-from-prior`: flag judgments that update or contradict a prior public assessment without naming the change. ICD-203 §2(g).
- `relevance-to-customer`: opt-in rule that checks for a stated audience and asset profile in the front matter. ICD-203 §2(e).
- A VS Code extension that runs the rules on save (piggybacking on the same engine as the `anti-slop` extension).

PRs welcome on any of these.

## Contributing

See `CONTRIBUTING.md`. Tests live in `tests/`; new rules go in `src/icd203_lint/rules/`. Every new rule needs a test fixture in both `tests/fixtures/good/` and `tests/fixtures/bad/`.

## License

MIT. See `LICENSE`.

## Related

- `docs/icd203-primer.md`: the long-form case for adopting ICD-203 outside the IC. Read this if the rules look arbitrary.
- ODNI: Intelligence Community Directive 203, "Analytic Standards". The source document.
- Heuer, *Psychology of Intelligence Analysis*, CIA Center for the Study of Intelligence, 1999. The book ICD-203 is the engineering spec for.

If you're building something downstream of this (a hosted version, a VS Code extension, a Word add-in), I'd like to hear about it. Open an issue.
