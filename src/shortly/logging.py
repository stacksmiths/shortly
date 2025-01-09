"""
Logging utilities for the Shortly URL Shortener application.

This module provides:
- Logging configuration with optional debug mode.
- Middleware for logging incoming HTTP requests and outgoing responses.
- Exception handling to capture and log unhandled exceptions.

Key Features:
- Centralized logging configuration for the application.
- Detailed request and response logging for debugging and monitoring.
- Graceful error handling with structured JSON error responses.

Usage:
    - Call `configure_logging(debug=True)` to enable debug logging.
    - Add `LogRequestsMiddleware` as middleware to the FastAPI app.
    - Register `log_exception_handler` as a global exception handler.
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse


def configure_logging(debug: bool) -> logging.Logger:
    """
    Configure logging with optional debug mode.

    Args:
        debug (bool): Enables debug-level logging if True; otherwise,
        uses INFO level.

    Returns:
        logging.Logger: Configured logger instance for the application.
    """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    logger = logging.getLogger("Shortly")
    if debug:
        logger.debug("Debug logging enabled")
    else:
        logger.info("Logging initialized")
    return logger


async def log_requests_middleware(request: Request, call_next):
    """
    Middleware to log incoming requests and outgoing responses.

    Logs request details such as method, URL, and request body (if available),
    along with the response status code.

    Args:
        request (Request): The incoming HTTP request.
        call_next (callable): The next middleware or route handler.

    Returns:
        Response: The HTTP response after processing the request.
    """
    logger = logging.getLogger("Shortly")

    # Log the incoming request method and URL
    logger.info("Incoming request: %s %s", request.method, request.url)

    # Try to capture the request body
    try:
        body = await request.body()
        if body:
            logger.debug("Request body: %s", body.decode("utf-8"))
    except Exception as e:  # noqa: E722 or pylint: disable=broad-except
        logger.warning("Could not read request body: %s", e)

    # Process the request and get the response
    response = await call_next(request)

    # Log the response status code
    logger.info("Response status: %d", response.status_code)

    return response


async def log_exception_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    """
    Log unhandled exceptions and return an internal server error response.

    Args:
        request (Request): The incoming HTTP request.
        exc (Exception): The unhandled exception.

    Returns:
        JSONResponse: A structured JSON response with a 500 status code.
    """
    logger = logging.getLogger("Shortly")
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
