"""Testy encji."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.infopigula.api import News
from custom_components.infopigula.const import MAX_STATE_LENGTH, RELEASE_URL
from custom_components.infopigula.sensor import build_state


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_sensors(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    release_json: dict[str, Any],
    config_entry: MockConfigEntry,
) -> None:
    aioclient_mock.get(RELEASE_URL, json=release_json)
    await _setup(hass, config_entry)

    poland = hass.states.get("sensor.wydarzenia_polska")
    assert poland is not None
    assert poland.state == (
        "Pierwszy tytuł z kraju. • Drugi tytuł z kraju. • Wiadomość bez pogrubienia."
    )
    assert poland.attributes["release"] == "Wydanie 01.01.2030"
    assert poland.attributes["published"] == "2030-01-01T03:00:00"
    assert [n["title"] for n in poland.attributes["news"]] == [
        "Pierwszy tytuł z kraju.",
        "Drugi tytuł z kraju.",
        "Wiadomość bez pogrubienia.",
    ]
    assert poland.attributes["summary"].startswith(
        "1. Pierwszy tytuł z kraju. Pierwszy akapit. Drugi akapit.\n\n2. "
    )

    world = hass.states.get("sensor.wydarzenia_swiat")
    assert world is not None
    assert world.state == "Tytuł ze świata."
    assert world.attributes["news"][0]["source"] == "Rmf24"


async def test_update_every_three_hours(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    release_json: dict[str, Any],
    config_entry: MockConfigEntry,
) -> None:
    aioclient_mock.get(RELEASE_URL, json=release_json)
    await _setup(hass, config_entry)
    assert aioclient_mock.call_count == 1

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(hours=2))
    await hass.async_block_till_done()
    assert aioclient_mock.call_count == 1

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(hours=3, minutes=1))
    await hass.async_block_till_done()
    assert aioclient_mock.call_count == 2


async def test_missing_category_is_unavailable(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    release_json: dict[str, Any],
    config_entry: MockConfigEntry,
) -> None:
    release_json["categories"] = release_json["categories"][:1]
    aioclient_mock.get(RELEASE_URL, json=release_json)
    await _setup(hass, config_entry)
    assert hass.states.get("sensor.wydarzenia_swiat").state == STATE_UNAVAILABLE
    assert hass.states.get("sensor.wydarzenia_polska").state != STATE_UNAVAILABLE


def test_state_is_truncated() -> None:
    news = [News(str(i), "x" * 120, "", None, None, None, None, "") for i in range(3)]
    state = build_state(news)
    assert len(state) == MAX_STATE_LENGTH
    assert state.endswith("…")
