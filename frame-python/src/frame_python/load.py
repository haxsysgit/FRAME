from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from frame_python.model import FrameDocument, FrameEntry, FramePart

KNOWN_PARTS = ("facts", "rules", "acts", "map", "expect")
KNOWN_ENTRY_FIELDS = {"id", "title", "summary", "payload", "extensions"}


def load_frame(data: Mapping[str, Any]) -> FrameDocument:
    if not isinstance(data, Mapping):
        raise TypeError("FRAME document top-level input must be a mapping")

    frame_kwargs: dict[str, Any] = {}
    extensions: dict[str, Any] = {}

    for key, value in data.items():
        if key in KNOWN_PARTS:
            frame_kwargs[key] = _load_part(value, part_name=key)
        else:
            extensions[key] = value

    frame_kwargs["extensions"] = extensions
    return FrameDocument(**frame_kwargs)


def load_frame_file(path: str | Path) -> FrameDocument:
    file_path = Path(path)
    data = json.loads(file_path.read_text(encoding="utf-8"))
    return load_frame(data)


def _load_part(value: Any, *, part_name: str) -> FramePart:
    if not isinstance(value, Mapping):
        raise TypeError(f"FRAME part '{part_name}' must be a mapping")

    raw_entries = value.get("entries", [])
    if not isinstance(raw_entries, list):
        raise TypeError(f"FRAME part '{part_name}' entries must be a list")

    entries = [_load_entry(item, part_name=part_name) for item in raw_entries]
    part_extensions = {key: item for key, item in value.items() if key != "entries"}
    return FramePart(entries=entries, extensions=part_extensions)


def _load_entry(value: Any, *, part_name: str) -> FrameEntry:
    if not isinstance(value, Mapping):
        raise TypeError(f"Entries in part '{part_name}' must be mappings")

    payload = value.get("payload", {})
    if not isinstance(payload, Mapping):
        raise TypeError(f"Entry payload in part '{part_name}' must be a mapping")

    raw_extensions = value.get("extensions", {})
    if not isinstance(raw_extensions, Mapping):
        raise TypeError(f"Entry extensions in part '{part_name}' must be a mapping")

    extra_fields = {
        key: item
        for key, item in value.items()
        if key not in KNOWN_ENTRY_FIELDS
    }
    extensions = dict(raw_extensions) | extra_fields

    return FrameEntry(
        id=value.get("id"),
        title=value.get("title"),
        summary=value.get("summary"),
        payload=dict(payload),
        extensions=extensions,
    )
