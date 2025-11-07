import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Base directory for JSON fixtures."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def load_json_fixture(fixtures_dir: Path) -> Callable[[str], Any]:
    """Return a loader that reads JSON fixtures relative to the fixtures dir."""

    def _loader(relative_path: str) -> Any:
        fixture_path = fixtures_dir / relative_path
        with fixture_path.open(encoding="utf-8") as file:
            return json.load(file)

    return _loader


@pytest.fixture
def make_args() -> Callable[..., SimpleNamespace]:
    """Factory fixture for building argparse-like namespaces."""

    def _factory(**overrides: Any) -> SimpleNamespace:
        defaults = {
            "search": False,
            "search_string": None,
            "days": 3,
            "verbose": False,
        }
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    return _factory
