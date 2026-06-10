from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def test_pyproject_declares_minimal_package_metadata() -> None:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

    project = data["project"]
    dependencies = set(project.get("dependencies", []))

    assert project["name"] == "frame"
    assert project["requires-python"] == ">=3.11"
    assert project["readme"] == "README.md"
    assert project["license"]
    assert project["authors"]
    assert project["urls"]["Homepage"]
    assert project["classifiers"]
    assert "PyYAML" in dependencies
    assert "jsonschema" in dependencies

    optional = project["optional-dependencies"]
    dev_dependencies = set(optional["dev"])
    assert "pytest" in dev_dependencies
    assert "build" in dev_dependencies
