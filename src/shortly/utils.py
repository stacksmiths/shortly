"""
Utility functions for the Shortly application.

This module provides utility functions for generating random short IDs used
in the URL shortening service.

Key Features:
- `generate_short_id`: Creates a random alphanumeric short ID.

Usage:
    - Use `generate_short_id` to generate unique short IDs for URLs.
"""

import random
import string
import logging


def generate_short_id(length: int = 6) -> str:
    """
    Generate a random short ID using alphanumeric characters.

    Args:
        length (int): The length of the short ID. Defaults to 6.

    Returns:
        str: The generated short ID.
    """
    logger = logging.getLogger("Shortly")
    characters = string.ascii_letters + string.digits
    short_id = "".join(random.choices(characters, k=length))
    logger.debug("Generated short ID: %s", short_id)
    return short_id
