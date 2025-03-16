"""Common test fixtures and configuration for pytest."""

from pathlib import Path

import pytest


@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_plantuml_file(test_data_dir: Path) -> Path:
    """Return the path to a sample PlantUML file."""
    return test_data_dir / "sample.puml"


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for test outputs."""
    return tmp_path / "output"
