"""
URL shortening utilities for the Shortly application.

This module provides functions for managing URL shortening, retrieving
original URLs, and tracking usage analytics.

Key Features:
- `shorten_url`: Generates a short ID for a given URL with an optional TTL.
- `get_original_url`: Retrieves the original URL for a short ID if valid.
- `get_click_count`: Tracks and retrieves access counts for shortened URLs.

Usage:
    - Use `shorten_url` to create a short ID for a URL.
    - Use `get_original_url` to retrieve the original URL from a short ID.
    - Use `get_click_count` to retrieve analytics for a specific short ID.
"""

import logging
from datetime import datetime, timedelta
from .utils import generate_short_id
from .database import url_store, expiration_store, click_count_store


def shorten_url(url: str, ttl: int = 3600) -> str:
    """
    Shorten the URL and store it in the in-memory database with an expiration.

    Args:
        url (str): The original URL to shorten.
        ttl (int): Time-to-live in seconds. Defaults to 3600 (1 hour).

    Returns:
        str: The generated short ID for the URL.
    """
    logger = logging.getLogger("Shortly")

    # Check if the URL is already shortened
    for short_id, stored_url in url_store.items():
        if stored_url == url:
            logger.debug("URL already shortened: %s -> %s", url, short_id)
            return short_id

    # Generate a new short ID
    short_id = generate_short_id()
    expiration_time = datetime.now() + timedelta(seconds=ttl)
    url_store[short_id] = str(url)
    expiration_store[short_id] = expiration_time
    click_count_store[short_id] = 0

    logger.debug("Shortened URL: %s -> %s (expires at %s)", url, short_id,
                 expiration_time)
    return short_id


def get_original_url(short_id: str) -> str:
    """
    Retrieve the original URL for a given short ID, if it hasn't expired.

    Args:
        short_id (str): The unique short ID.

    Returns:
        str: The original URL if the short ID exists and hasn't expired,
             otherwise None.
    """
    logger = logging.getLogger("Shortly")

    # Validate existence of the short ID
    if short_id not in url_store or short_id not in expiration_store:
        logger.debug("Short ID not found or expired: %s", short_id)
        return None

    # Check for expiration
    if datetime.now() > expiration_store[short_id]:
        logger.debug("Short ID expired: %s", short_id)
        del url_store[short_id]
        del expiration_store[short_id]
        del click_count_store[short_id]
        return None

    # Increment click count
    if short_id in click_count_store:
        click_count_store[short_id] += 1

    logger.debug("Retrieved original URL: %s -> %s", short_id,
                 url_store[short_id])
    return url_store[short_id]


def get_click_count(short_id: str) -> int:
    """
    Get the click count for a given short ID.

    Args:
        short_id (str): The unique short ID.

    Returns:
        int: The number of times the URL has been accessed.
    """
    logger = logging.getLogger("Shortly")
    click_count = click_count_store.get(short_id, 0)
    logger.debug("Click count for %s: %d", short_id, click_count)
    return click_count
