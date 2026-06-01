"""CLI smoke tests."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

from icd203_lint.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_clean_file_exits_zero(capsys, monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False, raising=False)
    rc = main([str(FIXTURES / "good" / "01-assessment-with-confidence.md")])
    assert rc == 0


def test_cli_dirty_file_exits_one(capsys):
    rc = main([str(FIXTURES / "bad" / "01-assess-no-confidence.md")])
    assert rc == 1
    captured = capsys.readouterr()
    assert "assessment-no-confidence" in captured.out


def test_cli_directory_recursion(capsys):
    rc = main([str(FIXTURES / "good")])
    assert rc == 0


def test_cli_json_format(capsys):
    rc = main([str(FIXTURES / "bad" / "01-assess-no-confidence.md"), "--format", "json"])
    assert rc == 1
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert data[0]["rule_id"] == "assessment-no-confidence"


def test_cli_sarif_format(capsys):
    rc = main([str(FIXTURES / "bad" / "01-assess-no-confidence.md"), "--format", "sarif"])
    assert rc == 1
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["version"] == "2.1.0"
    assert data["runs"][0]["results"][0]["ruleId"] == "assessment-no-confidence"


def test_cli_github_format(capsys):
    rc = main([str(FIXTURES / "bad" / "01-assess-no-confidence.md"), "--format", "github"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "::error " in captured.out or "::warning " in captured.out


def test_cli_select(capsys):
    rc = main(
        [
            str(FIXTURES / "bad" / "10-mixed-bad-report.md"),
            "--select",
            "assessment-no-confidence",
            "--format",
            "json",
        ]
    )
    assert rc == 1
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data
    assert all(item["rule_id"] == "assessment-no-confidence" for item in data)


def test_cli_ignore(capsys):
    rc = main(
        [
            str(FIXTURES / "bad" / "10-mixed-bad-report.md"),
            "--ignore",
            "assessment-no-confidence",
            "--format",
            "json",
        ]
    )
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert all(item["rule_id"] != "assessment-no-confidence" for item in data)


def test_cli_unknown_rule_id(capsys):
    rc = main(["--select", "no-such-rule", str(FIXTURES / "good")])
    assert rc == 2


def test_cli_list_rules(capsys):
    rc = main(["--list-rules"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "assessment-no-confidence" in captured.out
    assert "attribution-unsourced" in captured.out


def test_cli_stdin(capsys, monkeypatch):
    fake = "We assess that the operators are based in Brazil.\n"
    monkeypatch.setattr("sys.stdin", io.StringIO(fake))
    rc = main(["-", "--format", "json"])
    assert rc == 1
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data[0]["rule_id"] == "assessment-no-confidence"


def test_cli_severity_floor_filters_warns(capsys):
    """At severity=error, the unattributed-quote (warn) finding should not fire."""
    rc = main(
        [
            str(FIXTURES / "bad" / "09-quote-unattributed.md"),
            "--severity",
            "error",
            "--format",
            "json",
        ]
    )
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    # quote-unattributed is severity warn, so it should be filtered out;
    # exit code should be 0 because no remaining findings meet the floor.
    assert rc == 0
    assert data == []


def test_cli_inline_ignore_directive(tmp_path, capsys):
    p = tmp_path / "with-ignore.md"
    p.write_text(
        "# Test\n"
        "We assess that the operators are based in Brazil. "
        "<!-- icd203-lint: ignore=assessment-no-confidence -->\n",
        encoding="utf-8",
    )
    rc = main([str(p), "--format", "json"])
    assert rc == 0


def test_cli_file_disable_directive(tmp_path, capsys):
    p = tmp_path / "with-disable.md"
    p.write_text(
        "<!-- icd203-lint: disable-file -->\n"
        "# Test\nWe assess that the operators are based in Brazil.\n",
        encoding="utf-8",
    )
    rc = main([str(p)])
    assert rc == 0
