"""Stałe integracji Infopiguła."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "infopigula"

BASE_URL: Final = "https://infopigula.pl"
# Najnowsze wydanie - ten sam publiczny endpoint, z którego korzysta strona
# dla niezalogowanych (3 wiadomości z Polski i 3 ze świata).
RELEASE_URL: Final = f"{BASE_URL}/api/v1/user-dashboard/release"
NEWS_URL: Final = f"{BASE_URL}/news/{{news_id}}"

# Wydanie ukazuje się raz dziennie, więc częstsze odpytywanie nie ma sensu.
UPDATE_INTERVAL: Final = timedelta(hours=3)
REQUEST_TIMEOUT: Final = 30

# Nazwy kategorii w API -> klucz encji
CATEGORY_POLAND: Final = "Polska"
CATEGORY_WORLD: Final = "Świat"

# Maksymalna długość stanu encji w Home Assistant
MAX_STATE_LENGTH: Final = 255
