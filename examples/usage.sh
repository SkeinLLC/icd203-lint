#!/usr/bin/env bash
# Example invocations.

# Lint a single report.
icd203-lint advisory.md

# Lint every markdown file under reports/, treating warnings as failures.
icd203-lint reports/ --severity warn

# Only check confidence calibration.
icd203-lint advisory.md --select assessment-no-confidence --select single-source-overconfidence

# Output a SARIF file for code-scanning upload.
icd203-lint reports/ --format sarif > findings.sarif

# Run as a pre-commit hook (after adding the repo to .pre-commit-config.yaml).
pre-commit run icd203-lint --all-files
