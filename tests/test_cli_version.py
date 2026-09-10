"""Tests for the top-level --version flag."""

from janus_sec.cli import main


def test_version_flag_prints_version_and_exits_zero(monkeypatch, capsys) -> None:
    import sys

    monkeypatch.setattr(sys, "argv", ["janus-sec", "--version"])
    monkeypatch.setattr("janus_sec.cli.pkg_version", lambda name: "0.2.0")

    try:
        exit_code = main()
    except SystemExit as exc:
        exit_code = exc.code

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "0.2.0" in captured.out


def test_short_version_flag_prints_version_and_exits_zero(monkeypatch, capsys) -> None:
    import sys

    monkeypatch.setattr(sys, "argv", ["janus-sec", "-V"])
    monkeypatch.setattr("janus_sec.cli.pkg_version", lambda name: "0.2.0")

    try:
        exit_code = main()
    except SystemExit as exc:
        exit_code = exc.code

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "0.2.0" in captured.out
