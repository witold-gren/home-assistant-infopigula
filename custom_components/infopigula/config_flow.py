"""Konfiguracja z interfejsu: jedno potwierdzenie, bez danych logowania."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import InfopigulaClient, InfopigulaError
from .const import DOMAIN


class InfopigulaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Dodanie integracji - sprawdza tylko, czy wydanie da się pobrać."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            client = InfopigulaClient(async_get_clientsession(self.hass))
            try:
                await client.async_get_release()
            except InfopigulaError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="Infopiguła", data={})
        return self.async_show_form(step_id="user", errors=errors)
