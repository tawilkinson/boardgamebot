"""Unit tests for utils.game: the Game URL builder and Webpage wrapper."""
import requests

from utils.game import Game, Webpage


def test_name_is_capwords():
    assert Game("carcassonne").name == "Carcassonne"
    assert Game("ticket to ride").name == "Ticket To Ride"


def test_search_name_encoding():
    g = Game("ticket to ride")
    assert g.search_name == "ticket%20to%20ride"
    assert g.search_name_alpha_num == "tickettoride"


def test_bgg_search_urls():
    g = Game("carcassonne")
    assert "xmlapi2/search?query=carcassonne&exact=1" in g.bgg_search_url
    assert "exact=1" not in g.bgg_non_exact_search_url
    assert "query=carcassonne" in g.bgg_non_exact_search_url


def test_get_set_bgg_url_sets_and_returns():
    g = Game("carcassonne")
    thing_url = g.get_set_bgg_url(822)
    assert g.bgg == "https://boardgamegeek.com/boardgame/822/"
    assert "xmlapi2/thing?id=822" in thing_url


def test_update_name_refreshes_derived_fields():
    g = Game("carcassonne")
    g.update_name("ticket to ride")
    assert g.name == "Ticket To Ride"
    assert g.search_name == "ticket%20to%20ride"
    assert g.search_name_alpha_num == "tickettoride"


def test_return_game_data_shape():
    g = Game("carcassonne")
    data = g.return_game_data()
    assert set(data.keys()) == {
        "name", "description", "bgg", "image",
        "tabletopia", "tts", "bga", "yucata", "boite", "app",
    }
    assert data["name"] == "Carcassonne"


def test_webpage_parses_html(mock_get):
    mock_get("<html><body><p id='x'>hi</p></body></html>")
    page = Webpage("http://example.com")
    assert page.error is None
    assert page.page_html.find("p", id="x").text == "hi"


def test_webpage_parses_xml(mock_get):
    mock_get("<items total='1'><item id='5'/></items>")
    page = Webpage("http://example.com/xml", xml=True)
    assert page.page_html.items["total"] == "1"


def test_webpage_connection_error(raise_get):
    raise_get(requests.exceptions.ConnectionError())
    page = Webpage("http://example.com")
    assert page.page_html is None
    assert page.error == "Timed Out"


def test_webpage_ssl_error(raise_get):
    raise_get(requests.exceptions.SSLError())
    page = Webpage("http://example.com")
    assert page.page_html is None
    assert page.error == "SSL Error"
