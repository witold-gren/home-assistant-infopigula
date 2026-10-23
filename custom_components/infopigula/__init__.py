"""Infopiguła: najważniejsze wiadomości z Polski i ze świata w Home Assistant."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import InfopigulaClient
from .coordinator import InfopigulaConfigEntry, InfopigulaCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: InfopigulaConfigEntry) -> bool:
    """Uruchamia integrację z wpisu konfiguracji."""
    client = InfopigulaClient(async_get_clientsession(hass))
    coordinator = InfopigulaCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: InfopigulaConfigEntry) -> bool:
    """Wyładowuje integrację."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
