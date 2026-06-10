from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from frame_python.load import load_frame, load_frame_file
from frame_python.validate import validate_frame


def test_load_frame_preserves_unknown_top_level_extensions() -> None:
    data = {
        "facts": {
            "entries": [
                {
                    "id": "project.identity",
                    "summary": "Tiny CLI project.",
                    "payload": {"kind": "cli"},
                }
            ]
        },
        "custom": {"note": "keep me"},
    }

    frame = load_frame(data)

    assert frame.facts is not None
    assert len(frame.facts.entries) == 1
    assert frame.facts.entries[0].id == "project.identity"
    assert frame.extensions == {"custom": {"note": "keep me"}}


def test_load_frame_file_reads_json_fixture(tmp_path: Path) -> None:
    path = tmp_path / "frame.json"
    path.write_text(
        json.dumps(
            {
                "rules": {
                    "entries": [
                        {
                            "id": "behavior.scope",
                            "summary": "Stay within CLI scope.",
                            "payload": {"priority": "high"},
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    frame = load_frame_file(path)

    assert frame.rules is not None
    assert frame.rules.entries[0].id == "behavior.scope"


def test_validate_frame_provisional_warns_for_missing_candidate_parts() -> None:
    frame = load_frame(
        {
            "facts": {
                "entries": [
                    {
                        "id": "project.identity",
                        "summary": "Tiny CLI project.",
                        "payload": {"kind": "cli"},
                    }
                ]
            }
        }
    )

    report = validate_frame(frame, mode="provisional")

    assert report.is_valid is True
    assert report.errors == []
    assert any("rules" in warning for warning in report.warnings)
    assert any("expect" in warning for warning in report.warnings)


def test_validate_frame_strict_rejects_duplicate_ids_within_same_part() -> None:
    frame = load_frame(
        {
            "facts": {
                "entries": [
                    {"id": "dup", "payload": {}},
                    {"id": "dup", "payload": {}},
                ]
            }
        }
    )

    report = validate_frame(frame, mode="strict")

    assert report.is_valid is False
    assert any("duplicate" in error.lower() for error in report.errors)
