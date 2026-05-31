from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class FrameEntry:
    id: str | None = None
    title: str | None = None
    summary: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class FramePart:
    entries: list[FrameEntry] = field(default_factory=list)
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class FrameDocument:
    facts: FramePart | None = None
    rules: FramePart | None = None
    acts: FramePart | None = None
    map: FramePart | None = None
    expect: FramePart | None = None
    extensions: dict[str, Any] = field(default_factory=dict)
