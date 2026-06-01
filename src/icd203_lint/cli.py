"""Command-line interface.

Usage:
    icd203-lint [PATH ...] [options]

If PATH is a directory, every .md / .markdown / .txt file under it is linted
recursively. If PATH is "-" or omitted, input is read from stdin.

Exit codes:
    0 -- no findings at or above the severity floor
    1 -- findings at or above the severity floor
    2 -- usage error or I/O error
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from icd203_lint import __version__
from icd203_lint.core import Finding, Severity, lint_file, lint_text
from icd203_lint.registry import all_rules, get_rule, rule_catalog, rule_ids

EXIT_OK = 0
EXIT_FOUND = 1
EXIT_USAGE = 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="icd203-lint",
        description="Lint analytic writing for ICD-203 violations.",
    )
    p.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to lint. '-' or omitted reads stdin.",
    )
    p.add_argument(
        "--select",
        action="append",
        default=[],
        metavar="RULE",
        help="Only run the given rule id. Repeatable.",
    )
    p.add_argument(
        "--ignore",
        action="append",
        default=[],
        metavar="RULE",
        help="Skip the given rule id. Repeatable.",
    )
    p.add_argument(
        "--severity",
        choices=["info", "warn", "error"],
        default="warn",
        help="Severity floor. Findings below this severity are not reported (default: warn).",
    )
    p.add_argument(
        "--format",
        choices=["text", "json", "sarif", "github"],
        default="text",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable color output even if stdout is a TTY.",
    )
    p.add_argument(
        "--list-rules",
        action="store_true",
        help="Print the catalog of available rules and exit.",
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"icd203-lint {__version__}",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Print findings only. Suppress the summary line.",
    )
    return p


def _select_rules(select: list[str], ignore: list[str]) -> list:
    if select:
        rules = []
        for rid in select:
            r = get_rule(rid)
            if r is None:
                print(f"icd203-lint: unknown rule id '{rid}'", file=sys.stderr)
                sys.exit(EXIT_USAGE)
            rules.append(r)
    else:
        rules = all_rules()
    if ignore:
        rules = [r for r in rules if r.id not in ignore]
    return rules


def _iter_paths(paths: list[str]):
    """Yield (path, source) for each input. Source 'stdin' means read sys.stdin."""
    if not paths or paths == ["-"]:
        yield ("<stdin>", "stdin")
        return
    for raw in paths:
        if raw == "-":
            yield ("<stdin>", "stdin")
            continue
        p = Path(raw)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and f.suffix.lower() in {".md", ".markdown", ".txt"}:
                    yield (str(f), "file")
        else:
            yield (str(p), "file")


def _severity_at_or_above(findings: list[Finding], floor: Severity) -> list[Finding]:
    return [f for f in findings if not (f.severity < floor)]


def _print_text(findings: list[Finding], use_color: bool) -> None:
    by_file: dict[str, list[Finding]] = {}
    for f in findings:
        by_file.setdefault(f.file, []).append(f)
    for path in sorted(by_file):
        if use_color:
            sys.stdout.write(f"\x1b[1m{path}\x1b[0m\n")
        else:
            sys.stdout.write(f"{path}\n")
        for f in by_file[path]:
            sev = f.severity.value
            if use_color:
                color = {
                    "error": "\x1b[31m",
                    "warn": "\x1b[33m",
                    "info": "\x1b[36m",
                }.get(sev, "")
                reset = "\x1b[0m"
                head = f"  {color}{sev:5}{reset} {f.line:>4}:{f.column:<3} {f.rule_id}"
            else:
                head = f"  {sev:5} {f.line:>4}:{f.column:<3} {f.rule_id}"
            sys.stdout.write(head + "\n")
            sys.stdout.write(f"        {f.message}\n")
            sys.stdout.write(f"        > {f.snippet[:160]}\n")


def _print_github(findings: list[Finding]) -> None:
    """GitHub Actions workflow-command format. Renders inline annotations."""
    for f in findings:
        level = {"error": "error", "warn": "warning", "info": "notice"}[f.severity.value]
        msg = f.message.replace("\n", " ").replace("%", "%25").replace("\r", "%0D")
        sys.stdout.write(
            f"::{level} file={f.file},line={f.line},col={f.column}::"
            f"[{f.rule_id}] {msg}\n"
        )


def _print_sarif(findings: list[Finding]) -> None:
    """Minimal SARIF 2.1.0 output for code-scanning integration."""
    rule_index = {r["id"]: i for i, r in enumerate(rule_catalog())}
    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "icd203-lint",
                        "version": __version__,
                        "informationUri": "https://github.com/SkeinLLC/icd203-lint",
                        "rules": [
                            {
                                "id": r["id"],
                                "name": r["name"],
                                "shortDescription": {"text": r["name"]},
                                "fullDescription": {"text": r["description"]},
                                "defaultConfiguration": {
                                    "level": _sarif_level(r["severity"]),
                                },
                            }
                            for r in rule_catalog()
                        ],
                    },
                },
                "results": [
                    {
                        "ruleId": f.rule_id,
                        "ruleIndex": rule_index.get(f.rule_id, 0),
                        "level": _sarif_level(f.severity.value),
                        "message": {"text": f.message},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": f.file},
                                    "region": {
                                        "startLine": f.line,
                                        "startColumn": f.column,
                                    },
                                }
                            }
                        ],
                    }
                    for f in findings
                ],
            }
        ],
    }
    json.dump(sarif, sys.stdout, indent=2)
    sys.stdout.write("\n")


def _sarif_level(sev: str) -> str:
    return {"error": "error", "warn": "warning", "info": "note"}.get(sev, "warning")


def _print_json(findings: list[Finding]) -> None:
    json.dump([f.to_dict() for f in findings], sys.stdout, indent=2)
    sys.stdout.write("\n")


def _print_rule_catalog(use_color: bool) -> None:
    for r in rule_catalog():
        if use_color:
            sys.stdout.write(f"\x1b[1m{r['id']}\x1b[0m  ({r['severity']})\n")
        else:
            sys.stdout.write(f"{r['id']}  ({r['severity']})\n")
        sys.stdout.write(f"  {r['name']}\n")
        sys.stdout.write(f"  {r['description']}\n\n")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    use_color = (not args.no_color) and sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

    if args.list_rules:
        _print_rule_catalog(use_color)
        return EXIT_OK

    # Validate rule ids before any work.
    for rid in list(args.select) + list(args.ignore):
        if rid not in rule_ids():
            print(f"icd203-lint: unknown rule id '{rid}'", file=sys.stderr)
            return EXIT_USAGE

    rules = _select_rules(args.select, args.ignore)
    floor = Severity(args.severity)
    all_findings: list[Finding] = []
    files_seen = 0

    for path, kind in _iter_paths(args.paths):
        files_seen += 1
        try:
            if kind == "stdin":
                text = sys.stdin.read()
                findings = lint_text(text, rules=rules, path=path)
            else:
                findings = lint_file(path, rules=rules)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"icd203-lint: {path}: {exc}", file=sys.stderr)
            return EXIT_USAGE
        all_findings.extend(_severity_at_or_above(findings, floor))

    if args.format == "json":
        _print_json(all_findings)
    elif args.format == "sarif":
        _print_sarif(all_findings)
    elif args.format == "github":
        _print_github(all_findings)
    else:
        _print_text(all_findings, use_color=use_color)

    if not args.quiet and args.format == "text":
        plural = "" if files_seen == 1 else "s"
        n = len(all_findings)
        if n == 0:
            sys.stdout.write(f"\nicd203-lint: clean. {files_seen} file{plural} scanned.\n")
        else:
            sys.stdout.write(
                f"\nicd203-lint: {n} finding{'' if n == 1 else 's'} "
                f"in {files_seen} file{plural}.\n"
            )

    return EXIT_FOUND if all_findings else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
