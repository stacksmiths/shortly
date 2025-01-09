"""
In-memory database utilities for the Shortly application.

This module provides:
- Data structures for managing URLs, expiration times, and click counts.
- Centralized storage for application components without relying on
  external databases.

Key Features:
- `url_store`: Maps short IDs to their original URLs.
- `expiration_store`: Tracks expiration times for shortened URLs.
- `click_count_store`: Records the number of times each short ID
  has been accessed.

Usage:
    - Use `url_store` to map short IDs to original URLs.
    - Use `expiration_store` to manage TTL (time-to-live) for URLs.
    - Use `click_count_store` to track URL analytics.
"""

# Store mappings between short IDs and original URLs
url_store = {}

# Store expiration times for shortened URLs
expiration_store = {}

# Track the number of times each short ID has been accessed
click_count_store = {}
