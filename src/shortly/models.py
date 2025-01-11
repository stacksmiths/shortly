"""
Data models for the Shortly URL Shortener application.

This module defines Pydantic models used for request validation and
structured responses in the Shortly API.

Key Features:
- `URLRequest`: Validates incoming URL shortening requests.
- `URLResponse`: Defines the structure of the shortened URL response.
"""

from pydantic import BaseModel, HttpUrl


class URLRequest(BaseModel):
    """
    Model for URL shortening requests.

    Attributes:
        url (HttpUrl): The original URL to be shortened. Must be a valid
        HTTP/HTTPS URL.
    """
    url: HttpUrl


class URLResponse(BaseModel):
    """
    Model for URL shortening responses.

    Attributes:
        short_url (str): The shortened URL returned by the API.
    """
    short_url: str
