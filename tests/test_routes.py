"""
Unit tests for the Shortly application's API routes.

These tests cover:
- Health check and status endpoints.
- Validation of short IDs and error handling.
- URL shortening and retrieval.
- URL analytics (click counts).
- QR code generation for shortened URLs.

Each test ensures:
- Proper HTTP status codes are returned.
- The JSON responses match the expected formats.
- Functions like `shorten_url`, `get_original_url`, and `get_click_count`
are called correctly.
- Mocking is used to isolate route logic from underlying implementations.
"""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from pydantic import HttpUrl
from src.shortly.routes import register_routes

# Initialize the FastAPI app and register routes
app = FastAPI()
register_routes(app)
client = TestClient(app)


def test_health_check():
    """
    Test the /health endpoint to verify the application's basic health.

    This test ensures:
    - The endpoint responds with a 200 status code.
    - The JSON response contains a "status" field with the value "healthy".
    - The response includes "uptime" and "components" fields.
    - The "components" field contains "routes" with the value "up".
    """
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime" in data
    assert "components" in data
    assert data["components"]["routes"] == "up"


def test_validate_short_id_not_found():
    """
    Test validation for short IDs that do not exist in the database.

    This test ensures:
    - A 404 status code is returned when accessing a short ID
    not in `url_store`.
    - The response contains an appropriate error message.
    """
    invalid_short_id = "nonexistent"
    response = client.get(f"/{invalid_short_id}")
    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "Short ID not found"


def test_health_status():
    """
    Test the /health/status endpoint to verify the application's
    overall health.

    This test ensures:
    - The endpoint responds with a 200 status code.
    - The JSON response is a string, either "healthy" or "unhealthy".
    """
    response = client.get("/health/status")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, str)
    assert data in ["healthy", "unhealthy"]


def test_root_endpoint():
    """
    Test the root (/) endpoint.

    This test ensures:
    - The endpoint responds with a 200 status code.
    - It returns the expected JSON structure with a welcome
    message and endpoints.
    """
    response = client.get("/")

    assert response.status_code == 200

    expected_response = {
        "message": "Welcome to Shortly URL Shortener!",
        "endpoints": {
            "health": "/health",
            "health_status": "/health/status",
            "shorten_url": "/shorten",
            "retrieve_url": "/{short_id}",
            "analytics": "/{short_id}/analytics",
            "generate_qr": "/{short_id}/qr",
        },
    }
    assert response.json() == expected_response


def test_shorten_url():
    """
    Test the /shorten endpoint to shorten a URL.

    This test ensures:
    - The endpoint accepts a valid URLRequest payload.
    - It returns a valid short URL in the response.
    - The shorten_url function is called with the correct arguments.
    """
    payload = {"url": "https://example.com"}

    with patch("src.shortly.routes.shorten_url") as mock_shorten_url:
        mock_shorten_url.return_value = "abc123"

        # Send a POST request to /shorten
        response = client.post("/shorten", json=payload)

        # Verify response
        assert response.status_code == 200
        assert response.json() == {"short_url": "/abc123"}

        # Verify shorten_url function call with HttpUrl
        mock_shorten_url.assert_called_once_with(
            HttpUrl("https://example.com")
        )


def test_redirect_url_handler():
    """
    Test the /{short_id} endpoint for retrieving the original URL.

    This test ensures:
    - The endpoint validates the short ID.
    - It retrieves the original URL if the short ID is valid.
    - The get_original_url function is called with the correct arguments.
    """
    short_id = "abc123"
    original_url = "https://example.com"

    with (
        patch("src.shortly.routes.get_original_url") as mock_get_original_url,
        patch("src.shortly.routes.url_store", {short_id: original_url}),
    ):
        # Mock the return value of get_original_url
        mock_get_original_url.return_value = original_url

        # Send a GET request to /{short_id}
        response = client.get(f"/{short_id}")

        # Verify response
        assert response.status_code == 200
        assert response.json() == original_url

        # Verify get_original_url call
        mock_get_original_url.assert_called_once_with(short_id)


def test_analytics_handler():
    """
    Test the /{short_id}/analytics endpoint for retrieving URL analytics.

    This test ensures:
    - The endpoint validates the short ID.
    - It retrieves click count analytics for the short URL.
    - The get_click_count function is called correctly.
    """
    short_id = "abc123"
    click_count = 42

    with (
        patch("src.shortly.routes.get_click_count") as mock_get_click_count,
        patch(
            "src.shortly.routes.url_store", {short_id: "https://example.com"}
        ),
    ):
        # Mock the return value of get_click_count
        mock_get_click_count.return_value = click_count

        # Send a GET request to /{short_id}/analytics
        response = client.get(f"/{short_id}/analytics")

        # Verify response
        assert response.status_code == 200
        assert response.json() == {
            "short_id": short_id,
            "click_count": click_count,
        }

        # Verify get_click_count call
        mock_get_click_count.assert_called_once_with(short_id)


def test_generate_qr_code_handler():
    """
    Test the /{short_id}/qr endpoint for generating a QR code.

    This test ensures:
    - The endpoint validates the short ID.
    - It generates a QR code for the original URL.
    - The get_original_url function is called correctly.
    """
    short_id = "abc123"
    original_url = "https://example.com"

    with (
        patch("src.shortly.routes.get_original_url") as mock_get_original_url,
        patch("src.shortly.routes.url_store", {short_id: original_url}),
        patch("qrcode.make") as mock_qrcode_make,
    ):
        # Mock the return value of get_original_url
        mock_get_original_url.return_value = original_url

        # Mock qrcode.make to simulate QR code generation
        mock_qr_image = MagicMock()
        mock_qrcode_make.return_value = mock_qr_image

        # Send a GET request to /{short_id}/qr
        response = client.get(f"/{short_id}/qr")

        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

        # Verify get_original_url call
        mock_get_original_url.assert_called_once_with(short_id)

        # Verify qrcode.make is called with the original URL
        mock_qrcode_make.assert_called_once_with(original_url)
