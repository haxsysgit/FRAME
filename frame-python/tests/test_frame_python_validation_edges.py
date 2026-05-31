from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from frame_python.load import load_frame
from frame_python.validate import validate_frame


def test_strict_rejects_non_mapping_top_level_shape() -> None:
    try:
        load_frame(["not", "a", "mapping"])
    except TypeError as exc:
        assert "mapping" in str(exc).lower()
    else:
        raise AssertionError("Expected TypeError for non-mapping top-level input")


def test_provisional_reports_unknown_top_level_keys() -> None:
    frame = load_frame(
        {
            "facts": {"entries": []},
            "mystery": {"x": 1},
        }
    )

    report = validate_frame(frame, mode="provisional")

    assert any("mystery" in warning for warning in report.warnings)
