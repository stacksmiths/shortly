from src.shortly.shorten import shorten_url, get_original_url, get_click_count
from src.shortly.database import url_store, expiration_store
from datetime import datetime, timedelta


def test_shorten_url():
    """
    Test that a URL can be shortened and stored in the database.
    """
    url = "https://example.com"
    short_id = shorten_url(url)
    assert short_id in url_store
    assert url_store[short_id] == url


def test_get_original_url():
    """
    Test that a short ID retrieves the correct original URL.
    """
    url = "https://example.com"
    short_id = shorten_url(url)
    assert get_original_url(short_id) == url

    # Test for a non-existent short ID
    assert get_original_url("invalid_id") is None


def test_get_original_url_type():
    """
    Test that get_original_url returns a string.
    """
    url = "https://example.com"
    short_id = shorten_url(url)
    original_url = get_original_url(short_id)
    assert isinstance(original_url, str)


def test_shorten_url_with_expiration():
    """
    Test that shortened URLs expire correctly based on TTL.
    """
    url = "https://example.com"
    short_id = shorten_url(url, ttl=2)  # 2 seconds TTL
    assert short_id in url_store
    assert short_id in expiration_store

    # Ensure it's accessible before expiration
    assert get_original_url(short_id) == url

    # Simulate expiration
    expiration_store[short_id] = datetime.now() - timedelta(seconds=1)

    # Ensure it's not accessible after expiration
    assert get_original_url(short_id) is None


def test_get_original_url_and_click_count():
    """
    Test retrieving a URL and tracking clicks.
    """
    url = "https://example.com"
    short_id = shorten_url(url)

    # Access the URL twice
    assert get_original_url(short_id) == url
    assert get_original_url(short_id) == url

    # Verify click count
    assert get_click_count(short_id) == 2
