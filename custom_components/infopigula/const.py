"""Constants of the Infopiguła integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "infopigula"

BASE_URL: Final = "https://infopigula.pl"
# Latest release - the same public endpoint the website uses for visitors who
# are not logged in (3 news items from Poland and 3 from the world).
RELEASE_URL: Final = f"{BASE_URL}/api/v1/user-dashboard/release"
NEWS_URL: Final = f"{BASE_URL}/news/{{news_id}}"

# A new release comes out once a day, so polling more often makes no sense.
UPDATE_INTERVAL: Final = timedelta(hours=3)
REQUEST_TIMEOUT: Final = 30

# Category names as returned by the API (Polish data)
CATEGORY_POLAND: Final = "Polska"
CATEGORY_WORLD: Final = "Świat"

# Entity ids used before 0.1.0 (sensor.<object_id>), migrated to sensor.infopigula_<key>
LEGACY_OBJECT_IDS: Final = {"poland": "wydarzenia_polska", "world": "wydarzenia_swiat"}

# Maximum length of an entity state in Home Assistant
MAX_STATE_LENGTH: Final = 255
