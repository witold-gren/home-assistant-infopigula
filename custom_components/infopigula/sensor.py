"""Encje: wydarzenia z Polski i ze świata.

Stan encji ma w Home Assistant najwyżej 255 znaków, więc trzy wiadomości nie
zmieszczą się w nim w całości. Stan to tytuły (w razie potrzeby skrócone),
a pełne wiadomości są w atrybutach:

- ``news`` - lista: tytuł, tekst, ocena, liczba głosów, źródło, linki,
- ``summary`` - cały tekst gotowy do przeczytania (np. przez TTS),
- ``release`` / ``published`` - tytuł i data wydania.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import News
from .const import BASE_URL, CATEGORY_POLAND, CATEGORY_WORLD, DOMAIN, MAX_STATE_LENGTH
from .coordinator import InfopigulaConfigEntry, InfopigulaCoordinator


@dataclass(frozen=True, kw_only=True)
class InfopigulaSensorDescription(SensorEntityDescription):
    """Opis encji: która kategoria wydania i jakie entity_id."""

    category: str
    object_id: str


SENSORS: tuple[InfopigulaSensorDescription, ...] = (
    InfopigulaSensorDescription(
        key="poland",
        translation_key="poland",
        icon="mdi:newspaper-variant-outline",
        category=CATEGORY_POLAND,
        object_id="wydarzenia_polska",
    ),
    InfopigulaSensorDescription(
        key="world",
        translation_key="world",
        icon="mdi:earth",
        category=CATEGORY_WORLD,
        object_id="wydarzenia_swiat",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InfopigulaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(InfopigulaNewsSensor(coordinator, desc) for desc in SENSORS)


def build_state(news: list[News]) -> str:
    """Tytuły połączone w jeden tekst, przycięte do limitu stanu."""
    state = " • ".join(n.title for n in news)
    if len(state) > MAX_STATE_LENGTH:
        state = state[: MAX_STATE_LENGTH - 1].rstrip() + "…"
    return state


def build_summary(news: list[News]) -> str:
    """Pełny tekst wszystkich wiadomości, ponumerowany."""
    return "\n\n".join(
        f"{i}. {n.title}" + (f" {n.text}" if n.text else "") for i, n in enumerate(news, 1)
    )


class InfopigulaNewsSensor(CoordinatorEntity[InfopigulaCoordinator], SensorEntity):
    """Wiadomości z jednej kategorii wydania."""

    entity_description: InfopigulaSensorDescription
    _attr_has_entity_name = True
    _attr_attribution = "Dane: Infopiguła (infopigula.pl)"
    # Długie teksty nie trafiają do bazy recordera - historia nic nie wnosi,
    # a baza by puchła.
    _unrecorded_attributes = frozenset({"news", "summary"})

    def __init__(
        self, coordinator: InfopigulaCoordinator, description: InfopigulaSensorDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = f"{entry_id}_{description.key}"
        # stałe identyfikatory, niezależne od nazwy urządzenia i języka
        self.entity_id = f"sensor.{description.object_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Infopiguła",
            manufacturer="Infopiguła",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=BASE_URL,
        )

    @property
    def _news(self) -> list[News]:
        return self.coordinator.data.categories.get(self.entity_description.category, [])

    @property
    def available(self) -> bool:
        return super().available and bool(self._news)

    @property
    def native_value(self) -> str | None:
        return build_state(self._news) if self._news else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        release = self.coordinator.data
        return {
            "release": release.title,
            "published": release.published.isoformat() if release.published else None,
            "news": [n.as_dict() for n in self._news],
            "summary": build_summary(self._news),
        }
