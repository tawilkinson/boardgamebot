"""LIVE tests: scrape the real "play online" sites for their game lists.

Run with:  pytest -m live
A failure means that site's game list came back empty -- the reported "websites
lack games" symptom -- usually because the page structure/selector drifted.
"""
import pytest

from utils.online_game_search import get_all_games

pytestmark = pytest.mark.live

SITES = [
    (1, "Board Game Arena"),
    (2, "Boîte à Jeux"),
    (3, "Yucata.de"),
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
