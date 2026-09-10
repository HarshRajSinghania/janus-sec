"""Tests for config.toml parse errors."""

from pathlib import Path

from janus_sec.config import ConfigError, load_config


def test_load_config_invalid_toml_raises_config_error(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text("this is not = valid toml [")

    try:
        load_config(config_path)
    except ConfigError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected ConfigError")

    assert str(config_path) in message
    assert "Invalid TOML" in message


def test_load_config_missing_ignore_path_raises_config_error(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "[[ignore]]\ncheck_type = \"group_readable\"\n"
    )

    try:
        load_config(config_path)
    except ConfigError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected ConfigError")

    assert str(config_path) in message
    assert "[[ignore]]" in message
    assert "'path'" in message
