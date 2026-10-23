"""Klient publicznego API Infopigułki (tylko odczyt najnowszego wydania)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from html.parser import HTMLParser
import re
from typing import Any

import aiohttp

from .const import NEWS_URL, RELEASE_URL, REQUEST_TIMEOUT


class InfopigulaError(Exception):
    """Błąd pobierania lub odczytu wydania."""


@dataclass(frozen=True)
class News:
    """Jedna wiadomość z wydania."""

    id: str
    title: str
    text: str
    rating: float | None
    votes: int | None
    source: str | None
    source_url: str | None
    url: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "text": self.text,
            "rating": self.rating,
            "votes": self.votes,
            "source": self.source,
            "source_url": self.source_url,
            "url": self.url,
        }


@dataclass(frozen=True)
class Release:
    """Wydanie: tytuł, data publikacji i wiadomości pogrupowane w kategorie."""

    id: str
    title: str
    published: datetime | None
    categories: dict[str, list[News]] = field(default_factory=dict)


class _TextExtractor(HTMLParser):
    """Zbiera tekst z HTML, osobno pierwszy pogrubiony fragment (tytuł)."""

    BLOCKS = frozenset({"p", "br", "div", "li", "h1", "h2", "h3", "h4"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self._strong_depth = 0
        self._title_done = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("strong", "b"):
            self._strong_depth += 1
        elif tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("strong", "b") and self._strong_depth:
            self._strong_depth -= 1
            if not self._strong_depth and self.title_parts:
                self._title_done = True
        elif tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._strong_depth and not self._title_done:
            self.title_parts.append(data)
        else:
            self.parts.append(data)


def _clean(text: str) -> str:
    """Zwija białe znaki: akapity rozdzielone spacją, bez wielokrotnych spacji."""
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def split_content(html: str) -> tuple[str, str]:
    """Dzieli treść wiadomości na (tytuł, reszta tekstu).

    W Infopigułce pierwsze pogrubione zdanie to tytuł wiadomości. Gdy go nie
    ma, tytułem jest pierwsze zdanie tekstu.
    """
    parser = _TextExtractor()
    parser.feed(html or "")
    parser.close()
    title = _clean("".join(parser.title_parts))
    body = _clean("".join(parser.parts))
    if not title:
        first, sep, rest = body.partition(". ")
        title, body = (first + ".", rest) if sep else (body, "")
    return title, body


def _float(value: Any) -> float | None:
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def parse_release(data: dict[str, Any]) -> Release:
    """Zamienia JSON wydania na obiekt Release."""
    if not isinstance(data, dict) or not isinstance(data.get("categories"), list):
        raise InfopigulaError("Nieoczekiwany format odpowiedzi API")
    categories: dict[str, list[News]] = {}
    for category in data["categories"]:
        name = category.get("name")
        if not name:
            continue
        items = sorted(category.get("news") or [], key=lambda n: _int(n.get("order")) or 0)
        news_list = []
        for item in items:
            news_id = str(item.get("id") or "")
            title, text = split_content(item.get("content") or "")
            if not title:
                continue
            # źródło to obiekt {name, url, image}; starsze wydania mogą mieć tekst
            source = item.get("source")
            if isinstance(source, dict):
                source_name, source_url = source.get("name") or None, source.get("url") or None
            else:
                source_name, source_url = (str(source) if source else None), None
            news_list.append(
                News(
                    id=news_id,
                    title=title,
                    text=text,
                    rating=_float(item.get("rating")),
                    votes=_int(item.get("totalVotes")),
                    source=source_name,
                    source_url=source_url,
                    url=NEWS_URL.format(news_id=news_id) if news_id else "",
                )
            )
        categories[name] = news_list
    return Release(
        id=str(data.get("id") or ""),
        title=str(data.get("title") or ""),
        published=_parse_datetime(data.get("publishDate")),
        categories=categories,
    )


class InfopigulaClient:
    """Pobiera najnowsze wydanie."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def async_get_release(self) -> Release:
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(
                    RELEASE_URL, headers={"Accept": "application/json"}
                )
                response.raise_for_status()
                data = await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise InfopigulaError(f"Nie udało się pobrać wydania: {err}") from err
        except ValueError as err:
            raise InfopigulaError(f"Niepoprawny JSON: {err}") from err
        return parse_release(data)
