#!/usr/bin/env python3
"""Manage the plugin version recorded in the plugin/marketplace manifests.

The same version string appears in four spots across three JSON files
(see SPOTS); this module is the single implementation of the invariants:
well-formed bare X.Y.Z, all spots agree, and bumps only go up.
"""

import json
import re
from pathlib import Path

VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")

SPOTS = [
    ("plugins/fortuita-arcana/.claude-plugin/plugin.json", ("version",)),
    ("plugins/fortuita-arcana/plugin.json", ("version",)),
    (".github/plugin/marketplace.json", ("metadata", "version")),
    (".github/plugin/marketplace.json", ("plugins", 0, "version")),
]


class VersionError(Exception):
    pass


def parse_version(text):
    if not isinstance(text, str) or not VERSION_RE.match(text):
        raise VersionError(
            f"invalid version {text!r}: expected X.Y.Z "
            "(no v prefix, no leading zeros, no pre-release suffix)"
        )
    return tuple(int(part) for part in text.split("."))


def spot_label(path, keys):
    return f"{path}:{'.'.join(str(key) for key in keys)}"


def read_spots(root):
    found = []
    for path, keys in SPOTS:
        file = root / path
        try:
            data = json.loads(file.read_text())
        except FileNotFoundError:
            raise VersionError(f"missing manifest: {path}")
        except json.JSONDecodeError as exc:
            raise VersionError(f"unparseable JSON in {path}: {exc}")
        value = data
        for key in keys:
            try:
                value = value[key]
            except (KeyError, IndexError, TypeError):
                raise VersionError(f"missing key {spot_label(path, keys)}")
        found.append((spot_label(path, keys), value))
    return found


def current_version(root):
    found = read_spots(root)
    values = {value for _, value in found}
    if len(values) != 1:
        detail = "\n".join(f"  {label} = {value!r}" for label, value in found)
        raise VersionError(f"version drift between manifests:\n{detail}")
    value = values.pop()
    parse_version(value)
    return value
