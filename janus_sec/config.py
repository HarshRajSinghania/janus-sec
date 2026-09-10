"""User configuration: config.toml, ignore list, and user-added allowlist entries.

Lives at ~/.config/janus-sec/config.toml (XDG_CONFIG_HOME), separate from
the audit log's state directory - config is what the user set up, state is
a record of what happened.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from janus_sec.checks.group_ownership import AllowlistPattern

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Python 3.10 fallback


class ConfigError(ValueError):
    """Raised when user config.toml is malformed or missing required keys."""


@dataclass(frozen=True, slots=True)
class IgnoreEntry:
    path: str
    check_type: str
    note: str = ""


@dataclass(frozen=True, slots=True)
class Config:
    ignore: list[IgnoreEntry]
    allowlist: list[AllowlistPattern]


def default_config_path() -> Path:
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_config) if xdg_config else Path.home() / ".config"
    return base / "janus-sec" / "config.toml"


def load_config(config_path: Path | None = None) -> Config:
    """Load user config. A missing file is not an error - it just means
    no ignore rules and no extra allowlist entries, same as a fresh
    install with nothing customized yet.
    """
    if config_path is None:
        config_path = default_config_path()

    if not config_path.exists():
        return Config(ignore=[], allowlist=[])

    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(
            f"Invalid TOML in config file {config_path}: {exc}"
        ) from exc

    ignore = []
    for index, entry in enumerate(data.get("ignore", [])):
        try:
            ignore.append(
                IgnoreEntry(
                    path=entry["path"],
                    check_type=entry["check_type"],
                    note=entry.get("note", ""),
                )
            )
        except KeyError as exc:
            missing = exc.args[0]
            raise ConfigError(
                f"Config file {config_path}: [[ignore]] entry {index} "
                f"is missing required key {missing!r}"
            ) from exc

    allowlist = []
    for index, entry in enumerate(data.get("allowlist", [])):
        try:
            allowlist.append(
                AllowlistPattern(
                    group=entry["group"],
                    action=entry.get("action", "suppress"),
                    os_name=entry.get("os"),
                )
            )
        except KeyError as exc:
            missing = exc.args[0]
            raise ConfigError(
                f"Config file {config_path}: [[allowlist]] entry {index} "
                f"is missing required key {missing!r}"
            ) from exc

    return Config(ignore=ignore, allowlist=allowlist)


def is_ignored(path: str, check_type: str, config: Config) -> bool:
    return any(
        entry.path == path and entry.check_type == check_type
        for entry in config.ignore
    )


def filter_ignored(findings: list, config: Config) -> list:
    """Remove any finding that matches an ignore-list entry."""
    return [
        f for f in findings
        if not is_ignored(f.path, f.check_type.value, config)
    ]
