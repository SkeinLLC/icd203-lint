"""Tests for the core Document / sentence model."""

from __future__ import annotations

from icd203_lint.core import Document, split_sentences


def test_split_sentences_basic():
    text = "Hello world. This is a test! Is it? Yes."
    sents = list(split_sentences(text))
    assert [s.text for s in sents] == [
        "Hello world.",
        "This is a test!",
        "Is it?",
        "Yes.",
    ]


def test_split_sentences_abbreviations():
    text = "Per the U.S. advisory, we assess with low confidence. The actor used e.g. SMB."
    sents = list(split_sentences(text))
    assert len(sents) == 2
    assert "U.S." in sents[0].text


def test_split_sentences_keeps_line_numbers():
    text = "First sentence.\n\nSecond sentence on line three."
    sents = list(split_sentences(text))
    assert sents[0].line == 1
    assert sents[1].line == 3


def test_skip_fenced_code_blocks():
    text = (
        "Real prose here.\n\n"
        "```\n"
        "The group will pivot to financial services.\n"
        "```\n\n"
        "More real prose."
    )
    doc = Document.from_text(text)
    joined = " ".join(s.text for s in doc.sentences)
    assert "Real prose here." in joined
    assert "More real prose." in joined
    assert "pivot to financial services" not in joined


def test_skip_inline_code():
    text = "Run `the group will pivot` as a code sample. Now consider this."
    doc = Document.from_text(text)
    joined = " ".join(s.text for s in doc.sentences)
    assert "as a code sample" in joined
    assert "the group will pivot" not in joined


def test_skip_atx_headers():
    text = "# We assess that the operator is based in Brazil\n\nReal sentence here."
    doc = Document.from_text(text)
    joined = " ".join(s.text for s in doc.sentences)
    # Headers are blanked out, so the heading text doesn't count as a sentence.
    assert "We assess" not in joined
    assert "Real sentence" in joined


def test_skip_tables():
    text = "Intro sentence.\n\n| col | val |\n| --- | --- |\n| we | assess that we forgot confidence |\n\nOutro sentence."
    doc = Document.from_text(text)
    joined = " ".join(s.text for s in doc.sentences)
    assert "Intro sentence" in joined
    assert "Outro sentence" in joined
    assert "forgot confidence" not in joined


def test_inline_ignore_directive_registered():
    text = (
        "We assess that the operators are based in Brazil. "
        "<!-- icd203-lint: ignore=assessment-no-confidence -->\n"
    )
    doc = Document.from_text(text)
    assert 1 in doc.line_ignores
    assert "assessment-no-confidence" in doc.line_ignores[1]


def test_file_disable_directive_registered():
    text = "<!-- icd203-lint: disable-file -->\nWe assess things.\n"
    doc = Document.from_text(text)
    assert "*" in doc.file_ignores


def test_file_disable_specific_rules():
    text = (
        "<!-- icd203-lint: disable-file=assessment-no-confidence,future-unhedged -->\n"
        "We assess things.\n"
    )
    doc = Document.from_text(text)
    assert "assessment-no-confidence" in doc.file_ignores
    assert "future-unhedged" in doc.file_ignores
