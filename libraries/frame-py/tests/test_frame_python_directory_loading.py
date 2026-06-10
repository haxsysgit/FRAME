from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from frame import load_frame_dir, validate_frame

REPO_ROOT = ROOT.parent
ORGANIZE_FIT_DIR = (
    REPO_ROOT
    / "Frame lab"
    / "evaluations"
    / "fits"
    / "frame-five-part-v0.2.0"
    / "organize"
)


def test_load_frame_dir_reads_real_020_yaml_fit() -> None:
    frame = load_frame_dir(ORGANIZE_FIT_DIR)

    assert frame.facts is not None
    assert frame.rules is not None
    assert frame.map is not None
    assert frame.expect is not None
    assert frame.acts is not None

    assert frame.facts.header.file == "facts"
    assert frame.facts.header.schema_version == "0.2.0"
    assert frame.rules.header.file == "rules"
    assert frame.map.body["entrypoints"]["cli"]["path"] == "organize.py"
    assert frame.expect.body["checks"]["cli_help"]["proof_type"] == "smoke_test"
    assert frame.acts.body["runs"][0]["id"] == "inspect_fixture"


def test_validate_frame_strict_accepts_real_020_yaml_fit() -> None:
    frame = load_frame_dir(ORGANIZE_FIT_DIR)

    report = validate_frame(frame, mode="strict")

    assert report.is_valid is True
    assert report.errors == []


def test_validate_frame_strict_rejects_missing_required_part(tmp_path: Path) -> None:
    fixture = tmp_path / "missing-part"
    fixture.mkdir()

    for name, text in {
        "facts.yaml": "frame:\n  file: facts\n  schema_version: '0.2.0'\n  role: current_project_truth\n  status: draft\nprofile:\n  summary: x\n  family: utility-cli\n  system_role: y\n  complexity: tiny\n",
        "rules.yaml": "frame:\n  file: rules\n  schema_version: '0.2.0'\n  role: project_instruction_blueprint\n  status: draft\nrules: []\n",
        "map.yaml": "frame:\n  file: map\n  schema_version: '0.2.0'\n  role: repo_context_map\n  status: draft\nroots: {}\npaths: {}\ngroups: {}\nentrypoints: {}\nmanaged_paths: {}\nunmapped_paths: []\n",
        "expect.yaml": "frame:\n  file: expect\n  schema_version: '0.2.0'\n  role: project_correctness_contract\n  status: draft\noutcomes: {}\nmust_hold: {}\ndone_when: {}\nchecks: {}\nproof: []\nhandoff: {}\n",
    }.items():
        (fixture / name).write_text(text, encoding="utf-8")

    frame = load_frame_dir(fixture)
    report = validate_frame(frame, mode="strict")

    assert report.is_valid is False
    assert any("acts" in error.lower() for error in report.errors)


def test_validate_frame_strict_rejects_mixed_schema_versions(tmp_path: Path) -> None:
    fixture = tmp_path / "mixed-versions"
    fixture.mkdir()

    parts = {
        "facts.yaml": "facts",
        "rules.yaml": "rules",
        "map.yaml": "map",
        "expect.yaml": "expect",
        "acts.yaml": "acts",
    }

    for filename, file_name in parts.items():
        version = "0.1.0" if file_name == "acts" else "0.2.0"
        body = "summary: test\nruns: []\nblockers: []\nhandoff: {}\n" if file_name == "acts" else "rules: []\n" if file_name == "rules" else "profile:\n  summary: x\n  family: utility-cli\n  system_role: y\n  complexity: tiny\n" if file_name == "facts" else "roots: {}\npaths: {}\ngroups: {}\nentrypoints: {}\nmanaged_paths: {}\nunmapped_paths: []\n" if file_name == "map" else "outcomes: {}\nmust_hold: {}\ndone_when: {}\nchecks: {}\nproof: []\nhandoff: {}\n"
        (fixture / filename).write_text(
            f"frame:\n  file: {file_name}\n  schema_version: '{version}'\n  role: test\n  status: draft\n" + body,
            encoding="utf-8",
        )

    frame = load_frame_dir(fixture)
    report = validate_frame(frame, mode="strict")

    assert report.is_valid is False
    assert any("schema_version" in error for error in report.errors)
