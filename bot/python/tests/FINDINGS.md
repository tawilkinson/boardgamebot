# Findings

Issues surfaced while building the test suite. Items 1–4 have been **fixed**
(2026-06-24), each with a regression test that fails on the old behaviour and
passes on the new. Item 5 is an environmental caveat, not a code bug.

## 1. Invalid dice notation crashed instead of erroring gracefully — FIXED

`utils/die.py` — `Die.__init__` only wrapped `self.roll()` in the
`try/except AttributeError` that produces the `"! Incorrect syntax !"`
message, but `self.parse_dice()` ran *before* it. Any input the regex didn't
match (e.g. `bg roll notdice`) raised an uncaught `AttributeError`, so `/roll`
crashed.

**Fix:** guard `__init__` — if `self.match is None`, set the syntax-error
message and return before parsing.
**Test:** `tests/unit/test_die.py::test_invalid_notation_is_handled_gracefully`
(parametrised over several bad inputs).

## 2. `@cached` wrapped an async coroutine — FIXED

`utils/online_game_search.py` — `search_web_board_game_data` was `async` and
`@cached(TTLCache(...))`. cachetools cached the **coroutine object** (and keyed
on the `message`/`ctx` args too), so a cache hit returned an already-awaited
coroutine and raised `RuntimeError: cannot reuse already awaited coroutine`.

**Fix:** split into a public result-caching wrapper (caches the awaited result,
keyed on the game name only) and a private `_fetch_board_game_data`.
**Test:** `tests/parsing/test_online_game_search.py::test_search_results_are_cached_and_reusable`.

## 3. Stray debug `print` — FIXED

`utils/bgg.py` — `print(board_game_search)` dumped raw parsed XML to stdout on
every ambiguous (multi-match) BGG search. Removed.
**Test:** the multi-match test asserts `capsys` captured no stdout.

## 4. Unknown site raised instead of returning `{}` — FIXED

`utils/online_game_search.py` — `get_all_games` checked
`if site_name is None: return {}`, but `set_site_data` called `Site(site)`,
which raised `ValueError` for any unknown site before that guard could run.

**Fix:** `set_site_data` now catches the `ValueError` and returns
`(None, None)`, making the existing `get_all_games` guard reachable.
**Tests:** `test_set_site_data_unknown_site_returns_none`,
`test_get_all_games_unknown_site_returns_empty`.

## 6. Live site breakage (from the GitHub Actions live run)

Diagnosed against the real services (2026-06-25):

- **BGG search — FIXED (needs a token).** The XML API now returns `401
  Unauthorized` to anonymous requests; it requires `Authorization: Bearer
  <token>` (register at https://boardgamegeek.com/applications). `utils/bgg.py`
  now sends that header from the `BGG_TOKEN` env var, and the BGG URLs were
  switched to HTTPS. Set `BGG_TOKEN` in `.env` locally and as a CI secret. The
  BGG live test skips when the token is unset.
- **Boîte à Jeux — REMOVED.** `boiteajeux.net` no longer hosts the board-game
  service (the domain now serves an unrelated online-casino page). The feature,
  its scraper/embed/command, `Site.boite` (value 2), and the Boîte tests/fixture
  were removed.
- **Yucata.de — FIXED (needs credentials).** The full catalogue moved behind a
  login; the old `a.jGameInfo` selector no longer matches. `get_yucata_games()`
  now logs in with a `requests.Session` (POST `AuthenticateViaAjax` with
  `YUCATA_USER` / `YUCATA_PASS`, success = response `{"d": true}`) and scrapes
  the `/en/GameInfo/<Name>` links from the authenticated games page. Missing
  credentials or a failed login degrade to an empty list with a logged warning.
  The login request contract was verified live (`{"d": false}` for bad creds);
  the games-page parse is **unverified** without a real account — confirm with
  `pytest -m live` once `YUCATA_USER` / `YUCATA_PASS` are set. The Yucata live
  test skips when they're absent.
- BGA (1) and TTS (4) live tests pass.

## 5. Live results depend on the network environment — caveat (not a bug)

The `live/` suite needs real outbound HTTPS. In a sandboxed environment all
requests can fail with `SSL Error` (verified: even `https://example.com`
fails), so a red live run there is **not** a verdict on the real sites. Run
`pytest -m live` from an unrestricted network (or the scheduled CI job) to get
the true BGG/site health signal.

---

## Not addressed (out of scope)

- `utils/bgg.py:112` uses the deprecated BeautifulSoup `findAll` (→ `find_all`).
  Harmless deprecation warning; left as-is.
