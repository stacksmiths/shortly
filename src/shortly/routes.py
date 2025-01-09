"""
Routes for the Shortly URL Shortener application.

This module defines and registers API routes for the Shortly application.
It includes endpoints for:
- Health checks
- Shortening URLs
- Retrieving original URLs
- URL analytics (click counts)
- Generating QR codes for shortened URLs

Key Features:
- Detailed logging for all requests and responses.
- Validation for short IDs with error handling.
- Structured JSON responses for analytics and errors.

Usage:
    - Import `register_routes` and call it with a FastAPI instance.
    - Routes include `/shorten`, `/{short_id}`, and `/{short_id}/qr`.
"""

import logging
from io import BytesIO
import qrcode
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from .models import URLRequest, URLResponse
from .shorten import shorten_url, get_original_url, get_click_count
from .database import url_store
from .health import check_health, get_health_status


def register_routes(app: FastAPI):
    """
    Register all API routes for the URL shortener service.
    Includes endpoints for shortening URLs, retrieving original URLs,
    analytics, generating QR codes, and more.
    """
    logger = logging.getLogger("Shortly")

    def validate_short_id(short_id: str):
        """
        Validate if a given short_id exists in the database.

        Args:
            short_id (str): The short ID to validate.

        Raises:
            HTTPException: If the short ID does not exist.
        """
        if short_id not in url_store:
            logger.warning("Short ID %s not found", short_id)
            raise HTTPException(status_code=404, detail="Short ID not found")

    @app.get("/")
    def root_endpoint():
        """
        Root endpoint for the Shortly URL Shortener service.

        Returns:
            dict: A JSON response with service information.
        """
        logger.info("Root endpoint accessed")
        return {
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

    @app.get("/health")
    def health_check():
        """
        Detailed health status endpoint.
        """
        logger.info("Health status endpoint accessed")
        return check_health()

    @app.get("/health/status")
    def health_status():
        """
        Simplified health check endpoint.
        """
        logger.info("Health check endpoint accessed")
        return get_health_status()

    @app.post("/shorten", response_model=URLResponse)
    def shorten_url_handler(payload: URLRequest):
        """
        Shorten a URL and return the short ID.
        """
        logger.info("Shorten URL request received for: %s", payload.url)
        short_id = shorten_url(payload.url)
        logger.debug(
            "Generated short ID: %s for URL: %s", short_id, payload.url
        )
        return URLResponse(short_url=f"/{short_id}")

    @app.get("/{short_id}", response_model=str)
    def redirect_url_handler(short_id: str):
        """
        Retrieve the original URL for the given short ID.
        """
        logger.info("Redirect request for short ID: %s", short_id)
        validate_short_id(short_id)
        original_url = get_original_url(short_id)
        logger.debug("Original URL retrieved: %s", original_url)
        return original_url

    @app.get(
        "/{short_id}/analytics",
        response_model=dict,
        response_class=JSONResponse,
    )
    def analytics_handler(short_id: str):
        """
        Get analytics (click count) for a short URL.
        """
        logger.info("Analytics request for short ID: %s", short_id)
        validate_short_id(short_id)
        click_count = get_click_count(short_id)
        logger.debug(
            "Analytics for short ID %s: click count = %d",
            short_id,
            click_count,
        )
        return {"short_id": short_id, "click_count": click_count}

    @app.get("/{short_id}/qr", response_class=StreamingResponse)
    def generate_qr_code_handler(short_id: str):
        """
        Generate a QR code for the shortened URL.
        """
        logger.info("QR code request for short ID: %s", short_id)
        validate_short_id(short_id)
        original_url = get_original_url(short_id)
        logger.debug("Generating QR code for URL: %s", original_url)
        qr = qrcode.make(original_url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        buf.seek(0)
        logger.info("QR code generated for short ID: %s", short_id)
        return StreamingResponse(buf, media_type="image/png")
