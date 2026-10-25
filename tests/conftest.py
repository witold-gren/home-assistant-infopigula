"""Shared fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.infopigula.const import DOMAIN


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable custom_components in tests."""


@pytest.fixture
def release_json() -> dict[str, Any]:
    return json.loads((Path(__file__).parent / "fixtures" / "release.json").read_text("utf-8"))


@pytest.fixture
def config_entry() -> MockConfigEntry:
    return MockConfigEntry(domain=DOMAIN, title="Infopiguła", data={})
