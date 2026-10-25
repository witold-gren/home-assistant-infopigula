"""Coordinator: one request for the latest release every 3 hours."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import InfopigulaClient, InfopigulaError, Release
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

type InfopigulaConfigEntry = ConfigEntry[InfopigulaCoordinator]


class InfopigulaCoordinator(DataUpdateCoordinator[Release]):
    """Fetch the latest release every UPDATE_INTERVAL."""

    config_entry: InfopigulaConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: InfopigulaConfigEntry, client: InfopigulaClient
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            # the same release all day long - no needless state writes
            always_update=False,
        )
        self.client = client

    async def _async_update_data(self) -> Release:
        try:
            return await self.client.async_get_release()
        except InfopigulaError as err:
            raise UpdateFailed(str(err)) from err
