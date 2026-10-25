"""Infopiguła: the day's most important news from Poland and the world in Home Assistant."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import InfopigulaClient
from .const import DOMAIN, LEGACY_OBJECT_IDS
from .coordinator import InfopigulaConfigEntry, InfopigulaCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: InfopigulaConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    _migrate_entity_ids(hass, entry)
    client = InfopigulaClient(async_get_clientsession(hass))
    coordinator = InfopigulaCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: InfopigulaConfigEntry) -> bool:
    """Unload the integration."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def _migrate_entity_ids(hass: HomeAssistant, entry: InfopigulaConfigEntry) -> None:
    """Rename entities created by early versions (sensor.wydarzenia_*) to sensor.infopigula_*.

    Only the default ids are renamed; ids changed by the user are left alone.
    """
    registry = er.async_get(hass)
    for key, legacy_object_id in LEGACY_OBJECT_IDS.items():
        entity_id = registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_{key}")
        if entity_id != f"sensor.{legacy_object_id}":
            continue
        new_entity_id = f"sensor.{DOMAIN}_{key}"
        if registry.async_get(new_entity_id) is None:
            registry.async_update_entity(entity_id, new_entity_id=new_entity_id)
