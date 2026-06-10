"""FRAME Python SDK — v0.1.0

Load, validate, translate, and mechanically verify FRAME project context files.

Package layout:
    frame.models        — Dataclass models for FRAME documents and parts
    frame.loaders       — YAML/JSON file loading into typed models
    frame.validators    — Schema validation + mechanical command verification
    frame.translators   — Format conversion (YAML ↔ JSON ↔ typed models)
    frame.computations  — Graph building, cross-referencing, consistency reports
    frame.helpers       — Shared utilities
"""

from frame.models.model import FrameDocument, FrameEntry, FramePart
from frame.loaders.loader import load_frame, load_frame_file
from frame.validators.schema_validator import validate_frame
from frame.computations.report import ValidationReport

__all__ = [
    "FrameDocument",
    "FrameEntry",
    "FramePart",
    "ValidationReport",
    "load_frame",
    "load_frame_file",
    "validate_frame",
]
