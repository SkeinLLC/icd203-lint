"""Core types and the document/sentence model used by every rule.

A Document parses raw markdown or plain text into:
- a list of Sentence objects with line/column anchors
- a record of "skip regions" (fenced code blocks, inline code, tables, headers)
- a record of per-line and per-file ignore directives

Rules read sentences and emit Findings.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Severity(str, Enum):
    """Three-level severity. Maps to CLI exit code behavior."""

    INFO = "info"
    WARN = "warn"
    ERROR = "error"

    def __lt__(self, other: object) -> bool:
        order = {"info": 0, "warn": 1, "error": 2}
        if isinstance(other, Severity):
            return order[self.value] < order[other.value]
        return NotImplemented


@dataclass
class Finding:
    """One lint hit. Line numbers are 1-indexed."""

    rule_id: str
    message: str
    severity: Severity
    line: int
    column: int
    snippet: str
    file: str = "<input>"

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "message": self.message,
            "severity": self.severity.value,
            "line": self.line,
            "column": self.column,
            "snippet": self.snippet,
            "file": self.file,
        }


@dataclass
class Sentence:
    """A sentence with positional anchors into the raw document text."""

    text: str
    line: int
    column: int
    start_offset: int
    end_offset: int

    def __post_init__(self) -> None:
        self.text = self.text.strip()


@dataclass
class Document:
    """Parsed document with sentences and lint metadata."""

    path: str
    text: str
    sentences: list[Sentence] = field(default_factory=list)
    file_ignores: set[str] = field(default_factory=set)
    line_ignores: dict[int, set[str]] = field(default_factory=dict)

    @classmethod
    def from_text(cls, text: str, path: str = "<input>") -> Document:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        doc = cls(path=path, text=text)
        doc._parse_ignore_directives()
        cleaned = _strip_skip_regions(text)
        doc.sentences = list(split_sentences(cleaned, text))
        return doc

    def _parse_ignore_directives(self) -> None:
        """Parse inline ignore comments.

        Supported forms:
            <!-- icd203-lint: disable-file -->
            <!-- icd203-lint: disable-file=rule-a,rule-b -->
            <!-- icd203-lint: ignore -->
            <!-- icd203-lint: ignore=rule-a,rule-b -->
        """
        disable_file_pat = re.compile(
            r"<!--\s*icd203-lint:\s*disable-file(?:=([^>\s]+))?\s*-->", re.IGNORECASE
        )
        ignore_line_pat = re.compile(
            r"<!--\s*icd203-lint:\s*ignore(?:=([^>\s]+))?\s*-->", re.IGNORECASE
        )

        for m in disable_file_pat.finditer(self.text):
            ids = m.group(1)
            if ids is None:
                self.file_ignores.add("*")
            else:
                for rid in ids.split(","):
                    self.file_ignores.add(rid.strip())

        for idx, line in enumerate(self.text.split("\n"), start=1):
            for m in ignore_line_pat.finditer(line):
                ids = m.group(1)
                bucket = self.line_ignores.setdefault(idx, set())
                if ids is None:
                    bucket.add("*")
                else:
                    for rid in ids.split(","):
                        bucket.add(rid.strip())

    def is_ignored(self, rule_id: str, line: int) -> bool:
        if "*" in self.file_ignores or rule_id in self.file_ignores:
            return True
        bucket = self.line_ignores.get(line, set())
        return "*" in bucket or rule_id in bucket


_ABBREVIATIONS = {
    "u.s.",
    "u.k.",
    "e.g.",
    "i.e.",
    "etc.",
    "mr.",
    "mrs.",
    "ms.",
    "dr.",
    "vs.",
    "no.",
    "co.",
    "inc.",
    "ltd.",
    "jr.",
    "sr.",
    "st.",
    "fig.",
    "vol.",
    "ch.",
    "p.",
    "pp.",
}


def _strip_skip_regions(text: str) -> str:
    """Replace regions that shouldn't be linted with same-length whitespace.

    Same-length replacement preserves line and column offsets, so sentence
    positions still map back to the original document.
    """
    out = list(text)

    fenced = re.compile(r"(?ms)^(\s*)(```|~~~)[^\n]*\n.*?^\1\2\s*$")
    for m in fenced.finditer(text):
        for i in range(m.start(), m.end()):
            if out[i] != "\n":
                out[i] = " "

    inline = re.compile(r"`[^`\n]+`")
    for m in inline.finditer(text):
        for i in range(m.start(), m.end()):
            if out[i] != "\n":
                out[i] = " "

    for m in re.finditer(r"(?m)^\s{0,3}#{1,6}\s+[^\n]*$", text):
        for i in range(m.start(), m.end()):
            out[i] = " "

    for m in re.finditer(r"(?m)^\s*\|[^\n]*$", text):
        for i in range(m.start(), m.end()):
            out[i] = " "

    for m in re.finditer(r"(?s)<!--.*?-->", text):
        for i in range(m.start(), m.end()):
            if out[i] != "\n":
                out[i] = " "

    return "".join(out)


_SENT_END = re.compile(r"[.!?]+[\"'\)\]]*")


def split_sentences(cleaned_text: str, original_text: str | None = None):
    """Yield Sentence objects from `cleaned_text`.

    The cleaned text has the same length as the original, so offsets are
    interchangeable. Positions are 1-indexed.
    """
    src = original_text if original_text is not None else cleaned_text
    line_starts = [0]
    for i, ch in enumerate(src):
        if ch == "\n":
            line_starts.append(i + 1)

    def pos(offset: int) -> tuple[int, int]:
        line = 1
        for li, ls in enumerate(line_starts):
            if ls <= offset:
                line = li + 1
            else:
                break
        col = offset - line_starts[line - 1] + 1
        return line, col

    initialism = re.compile(r"(?:[a-z]\.)+", re.IGNORECASE)

    i = 0
    n = len(cleaned_text)
    while i < n:
        while i < n and cleaned_text[i].isspace():
            i += 1
        if i >= n:
            break
        start = i
        while i < n:
            m = _SENT_END.search(cleaned_text, i)
            if not m:
                i = n
                break
            end = m.end()
            wstart = m.start()
            while wstart > start and not cleaned_text[wstart - 1].isspace():
                wstart -= 1
            token = cleaned_text[wstart : m.end()].lower().strip("()[]\"'")

            is_abbrev = token in _ABBREVIATIONS or bool(initialism.fullmatch(token))
            if is_abbrev:
                i = end
                continue
            if end < n and cleaned_text[end - 1] == "." and cleaned_text[end].isdigit():
                i = end
                continue
            i = end
            break
        sent_text = cleaned_text[start:i]
        line, col = pos(start)
        if sent_text.strip():
            yield Sentence(
                text=sent_text.strip(),
                line=line,
                column=col,
                start_offset=start,
                end_offset=i,
            )


def lint_text(
    text: str,
    rules: list | None = None,
    path: str = "<input>",
) -> list[Finding]:
    """Lint raw text. If `rules` is None, all registered rules are used."""
    from icd203_lint.registry import all_rules

    doc = Document.from_text(text, path=path)
    selected = rules if rules is not None else all_rules()
    findings: list[Finding] = []
    for rule in selected:
        for f in rule.check(doc):
            f.file = path
            if doc.is_ignored(f.rule_id, f.line):
                continue
            findings.append(f)
    findings.sort(key=lambda f: (f.line, f.column, f.rule_id))
    return findings


def lint_file(path: str | Path, rules: list | None = None) -> list[Finding]:
    p = Path(path)
    return lint_text(p.read_text(encoding="utf-8"), rules=rules, path=str(p))
