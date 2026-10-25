"""Tests of the API client and release parsing."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import pytest
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.infopigula.api import (
    InfopigulaClient,
    InfopigulaError,
    parse_release,
    split_content,
)
from custom_components.infopigula.const import RELEASE_URL


def test_parse_release(release_json: dict[str, Any]) -> None:
    release = parse_release(release_json)
    assert release.title == "Wydanie 01.01.2030"
    assert release.published == datetime(2030, 1, 1, 3, 0)
    assert list(release.categories) == ["Polska", "Świat"]

    poland = release.categories["Polska"]
    # sorted by "order", not by the position in the JSON
    assert [n.id for n in poland] == ["p1", "p2", "p3"]
    first = poland[0]
    assert first.title == "Pierwszy tytuł z kraju."
    assert first.text == "Pierwszy akapit. Drugi akapit."
    assert first.rating == 4.14
    assert first.votes == 152
    assert first.source == "Interia"
    assert first.source_url == "https://example.com/p1"
    assert first.url == "https://infopigula.pl/news/p1"
    # &nbsp; replaced by a plain space
    assert poland[1].text == "Treść drugiej wiadomości."
    assert poland[2].source is None and poland[2].rating is None


def test_split_content_without_bold() -> None:
    assert split_content("<p>Pierwsze zdanie. Drugie zdanie.</p>") == (
        "Pierwsze zdanie.",
        "Drugie zdanie.",
    )


def test_split_content_empty() -> None:
    assert split_content("") == ("", "")


def test_parse_release_rejects_unexpected_format() -> None:
    with pytest.raises(InfopigulaError):
        parse_release({"message": "error"})


async def test_client_get_release(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, release_json: dict[str, Any]
) -> None:
    aioclient_mock.get(RELEASE_URL, json=release_json)
    release = await InfopigulaClient(async_get_clientsession(hass)).async_get_release()
    assert len(release.categories["Świat"]) == 1


async def test_client_http_error(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    aioclient_mock.get(RELEASE_URL, status=500)
    with pytest.raises(InfopigulaError):
        await InfopigulaClient(async_get_clientsession(hass)).async_get_release()


async def test_client_connection_error(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(RELEASE_URL, exc=aiohttp.ClientError("boom"))
    with pytest.raises(InfopigulaError):
        await InfopigulaClient(async_get_clientsession(hass)).async_get_release()
