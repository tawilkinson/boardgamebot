# Test suite

Tests for boardgamebot. Two layers:

- **Deterministic** (`unit/`, `parsing/`, `commands/`) — no network, no real
  Discord. Run via CI on every push/PR.
- **Live** (`live/`) — hits the real BGG API and the play-online sites (BGA,
  Yucata, TTS) to detect changes. Deselected by default; run on demand/weekly
  by CI.

## Setup

From `bot/python/`:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

(Requires Python ≥ 3.11 — the Dockerfile uses 3.13.)

The BGG XML API requires a token. For the BGG live test (and the bot) to reach
BGG, register an app at https://boardgamegeek.com/applications and export it:

```bash
export BGG_TOKEN=<your-token>   # or put it in bot/python/.env
```

The BGG live test skips when `BGG_TOKEN` is unset.

Yucata's catalogue requires login. Set `YUCATA_USER` / `YUCATA_PASS` (a Yucata
account) to enable the Yucata listing and its live test; otherwise the listing
is empty and the live test skips.

## Running

```bash
cd bot/python

pytest                # deterministic suite (live tests excluded via pytest.ini)
pytest -m live        # only the live drift tests (needs unrestricted network)
pytest tests/unit     # one layer
pytest -q             # quiet
```

## Layout

| Path | What it covers |
|------|----------------|
| `unit/` | Pure logic: dice, roller, helpers, Game URLs, wordle helpers, embeds |
| `parsing/` | Real BeautifulSoup parsers vs saved fixtures (BGG, BGA, Yucata, TTS) |
| `commands/` | Every slash-command callback + admin cmds + a cog-load smoke test |
| `live/` | `@pytest.mark.live` — real BGG + site requests (BGG needs `BGG_TOKEN`) |
| `fixtures/` | Saved HTML/XML samples encoding the structure each parser expects |
| `conftest.py` | Path/CWD setup, network-mock + fake-interaction fixtures, cache clearing |

## Output

| `parsing/` result | matching `live/` result | meaning |
|---|---|---|
| FAIL | — | our parser logic is wrong |
| PASS | FAIL | the external site drifted — fix the scraper |
| PASS | PASS | healthy |

