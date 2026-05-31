from __future__ import annotations

from frame_python.load import KNOWN_PARTS
from frame_python.model import FrameDocument, FramePart
from frame_python.report import ValidationReport


def validate_frame(frame: FrameDocument, mode: str = "strict") -> ValidationReport:
    if mode not in {"strict", "provisional"}:
        raise ValueError("mode must be 'strict' or 'provisional'")

    report = ValidationReport()

    for part_name in KNOWN_PARTS:
        part = getattr(frame, part_name)
        if part is None:
            if mode == "provisional":
                report.warnings.append(f"Candidate part '{part_name}' is missing")
            continue

        _validate_part(report, part_name, part)

    for key in frame.extensions:
        if mode == "provisional":
            report.warnings.append(
                f"Unknown top-level key '{key}' preserved in extensions"
            )

    return report


def _validate_part(report: ValidationReport, part_name: str, part: FramePart) -> None:
    seen_ids: set[str] = set()

    for entry in part.entries:
        if entry.id:
            if entry.id in seen_ids:
                report.errors.append(
                    f"Duplicate entry id '{entry.id}' found in part '{part_name}'"
                )
            seen_ids.add(entry.id)
