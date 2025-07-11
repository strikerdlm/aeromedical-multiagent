import pytest

from src.multiline_input import (
    detect_paste_input,
    format_large_text_preview,
    get_multiline_input_simple,
)


def test_detect_paste_short_text():
    assert not detect_paste_input("Hello world")


def test_detect_paste_many_lines():
    text = "\n".join("line" for _ in range(6))
    assert detect_paste_input(text)


def test_detect_paste_formal_indicators():
    text = "Abstract: ...\nIntroduction: ...\nResults: ...\nDOI: 12345"
    assert detect_paste_input(text)


def test_detect_paste_long_line():
    text = "a" * 501
    assert detect_paste_input(text)


def test_format_large_text_preview_lines():
    text = "\n".join(f"line{i}" for i in range(6))
    preview = format_large_text_preview(text, max_lines=3, max_chars=1000)
    assert preview.startswith("line0\nline1\nline2")
    assert "... (3 more lines)" in preview


def test_format_large_text_preview_chars():
    text = "a" * 600
    preview = format_large_text_preview(text, max_lines=10, max_chars=100)
    assert preview.endswith("...")
    assert len(preview) <= 103


def test_get_multiline_input_simple(monkeypatch):
    inputs = iter(["hello", "world", "/send"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    result = get_multiline_input_simple()
    assert result == "hello\nworld"


def test_get_multiline_input_simple_end(monkeypatch):
    inputs = iter(["hello", "END"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    result = get_multiline_input_simple()
    assert result == "hello"


def test_get_multiline_input_simple_interrupt(monkeypatch):
    def raise_interrupt(prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", raise_interrupt)
    result = get_multiline_input_simple()
    assert result == ""
