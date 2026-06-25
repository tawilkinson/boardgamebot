"""LIVE tests: scrape the real "play online" sites for their game lists.

Run with:  pytest -m live
A failure means that site's game list came back empty -- usually because the
page structure/selector drifted.
"""
import os

import pytest

from utils.online_game_search import get_all_games

pytestmark = pytest.mark.live

# Sites scrapeable without credentials.
SITES = [
    (1, "Board Game Arena"),
    (4, "Tabletop Simulator"),
]


@pytest.mark.parametrize("site,name", SITES)
def test_site_returns_games(site, name):
    games = get_all_games(site=site)
    assert "All Games Error" not in games, (
        f"{name} was unreachable: {games.get('All Games Error')}"
    )
    assert len(games) > 0, (
        f"{name} returned no games -- its scraper/selector is likely broken."
    )


@pytest.mark.skipif(
    not (os.getenv("YUCATA_USER") and os.getenv("YUCATA_PASS")),
    reason="YUCATA_USER / YUCATA_PASS not set; Yucata needs a logged-in session",
)
def test_yucata_returns_games():
    games = get_all_games(site=3)
    assert "All Games Error" not in games
    assert len(games) > 0, (
        "Yucata returned no games -- login may have failed or the games-page "
        "structure changed."
    )
