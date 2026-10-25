# Infopiguła – integracja Home Assistant

Pokazuje w Home Assistant najważniejsze wiadomości dnia z
[Infopiguły](https://infopigula.pl): **3 z Polski i 3 ze świata**.
Nie wymaga konta ani klucza API.

> Nieoficjalna integracja, niezwiązana z Infopigułą. Korzysta z tego samego
> publicznego wydania, które strona pokazuje niezalogowanym gościom, i pobiera
> je raz na 3 godziny. Prawa do treści należą do Infopiguły i autorów źródeł –
> integracja służy do prywatnego wyświetlania wiadomości w domu, nie do ich
> dalszej publikacji. Pełne wydanie i wiadomości premium są dostępne w
> [subskrypcji Infopiguły](https://infopigula.pl/premium).

## Encje

| Encja | Stan | Atrybuty |
|---|---|---|
| `sensor.infopigula_poland` | tytuły 3 wiadomości z Polski | `news`, `summary`, `release`, `published` |
| `sensor.infopigula_world` | tytuły 3 wiadomości ze świata | `news`, `summary`, `release`, `published` |

Stan encji w Home Assistant może mieć najwyżej 255 znaków, więc zawiera same
tytuły połączone znakiem ` • ` (w razie potrzeby skrócone). Pełne wiadomości są
w atrybutach:

- `news` – lista wiadomości; każda ma `title`, `text`, `rating` (ocena
  czytelników 1–5), `votes`, `source` (nazwa źródła), `source_url` (artykuł
  źródłowy) i `url` (wiadomość na infopigula.pl),
- `summary` – cały tekst, ponumerowany, gotowy np. do odczytania przez TTS,
- `release`, `published` – tytuł i data publikacji wydania.

`news` i `summary` nie są zapisywane w historii (recorder), żeby nie powiększać
bazy danych.

Gdy w wydaniu nie ma danej kategorii, encja jest niedostępna (`unavailable`).

## Instalacja

### HACS

1. HACS → ⋮ → **Niestandardowe repozytoria** → adres tego repozytorium,
   typ **Integracja**.
2. Wyszukaj **Infopiguła** → **Pobierz**.
3. Uruchom ponownie Home Assistant.

### Ręcznie

Skopiuj katalog `custom_components/infopigula` do `config/custom_components/`
i uruchom ponownie Home Assistant.

### Konfiguracja

**Ustawienia → Urządzenia i usługi → Dodaj integrację → Infopiguła.**
Nie trzeba niczego wpisywać – integracja sprawdza tylko, czy wydanie da się
pobrać.

## Przykłady

Karta Markdown z wiadomościami i linkami:

```yaml
type: markdown
title: Wiadomości
content: >
  {% for sensor, header in [('sensor.infopigula_poland', '🇵🇱 Polska'),
                            ('sensor.infopigula_world', '🌍 Świat')] %}
  ### {{ header }}
  {% for n in state_attr(sensor, 'news') or [] %}
  **{{ n.title }}** {{ n.text }} [więcej]({{ n.url }})

  {% endfor %}
  {% endfor %}
```

Odczytanie wiadomości z Polski na głośniku:

```yaml
action: tts.speak
target:
  entity_id: tts.piper
data:
  media_player_entity_id: media_player.salon
  message: "{{ state_attr('sensor.infopigula_poland', 'summary') }}"
```

## Jak to działa

Integracja co 3 godziny wysyła jedno zapytanie `GET`
`https://infopigula.pl/api/v1/user-dashboard/release` – ten sam publiczny
endpoint, z którego korzysta strona. Wydanie ukazuje się raz dziennie, więc
częstsze odpytywanie nic by nie dało. Pierwsze pogrubione zdanie wiadomości to
jej tytuł, reszta to treść.

## Rozwój

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements_test.txt
.venv/bin/pytest
.venv/bin/ruff check . && .venv/bin/ruff format --check .
```

Wdrożenie na własną instancję – skrypt kopiuje integrację do katalogu
konfiguracji Home Assistant (np. zamontowanego udziału Samby):

```sh
HA_CONFIG=/sciezka/do/config scripts/deploy.sh   # domyślnie /Volumes/config
```

## Licencja

MIT – zobacz [LICENSE](LICENSE). Licencja dotyczy kodu integracji, nie treści
wiadomości.
