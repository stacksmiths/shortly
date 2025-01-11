"""
Unit tests for the Shortly application's logging configuration.

These tests cover:
- Logging initialization with and without debug mode.
- Middleware logging of request bodies.
- Logging unhandled exceptions in the exception handler.
"""

from unittest.mock import ANY, AsyncMock, patch, MagicMock
import pytest
from fastapi import Request
from fastapi.responses import JSONResponse
from src.shortly.logging import (
    configure_logging,
    log_requests_middleware,
    log_exception_handler,
)


def test_configure_logging_info_message():
    """
    Test logging configuration info message when debug is False.
    """
    with patch("logging.getLogger") as mock_get_logger:
        logger_instance = mock_get_logger.return_value
        configure_logging(debug=False)
        logger_instance.info.assert_called_once_with("Logging initialized")


def test_configure_logging_debug_message():
    """
    Test logging configuration debug message when debug is True.

    This test ensures:
    - Debug-level logging is enabled when debug=True.
    - A debug message "Debug logging enabled" is logged.
    """
    with (
        patch("logging.basicConfig") as mock_basic_config,
        patch("logging.getLogger") as mock_get_logger,
    ):
        # Mock the logger instance returned by getLogger
        logger_instance = MagicMock()
        mock_get_logger.return_value = logger_instance

        # Call the function with debug=True
        configure_logging(debug=True)

        # Verify basicConfig was called with DEBUG level
        mock_basic_config.assert_called_once_with(
            level=10,  # 10 corresponds to logging.DEBUG
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[ANY],  # Ignore handler details in the test
        )

        # Verify the debug message is logged
        logger_instance.debug.assert_called_once_with("Debug logging enabled")


@pytest.mark.asyncio
async def test_log_requests_middleware_logs_request_body():
    """
    Test that the middleware logs the request body if it exists.

    This test ensures:
    - The middleware logs the incoming request method, URL, and body.
    - The middleware processes the response correctly.
    """
    # Mock the Request object
    mock_request = MagicMock(spec=Request)
    mock_request.method = "POST"
    mock_request.url = "http://testserver/api"
    mock_request.body = AsyncMock(return_value=b'{"key": "value"}')

    # Mock call_next to simulate the next middleware or route handler
    mock_response = MagicMock(status_code=200)
    mock_call_next = AsyncMock(return_value=mock_response)

    # Patch the logger
    with patch("logging.getLogger") as mock_get_logger:
        logger_instance = mock_get_logger.return_value

        # Call the middleware function directly
        response = await log_requests_middleware(mock_request, mock_call_next)

        # Verify the request body log
        logger_instance.debug.assert_any_call(
            "Request body: %s", '{"key": "value"}'
        )

        # Verify the response is passed back
        assert response == mock_response


@pytest.mark.asyncio
async def test_log_exception_handler_logs_exception():
    """
    Test that the exception handler logs the exception
    and returns a 500 response.
    """
    test_exception = Exception("Test exception")
    mock_request = MagicMock(spec=Request)

    with patch("logging.getLogger") as mock_get_logger:
        logger_instance = mock_get_logger.return_value

        # Call the exception handler
        response = await log_exception_handler(mock_request, test_exception)

        # Verify the exception log
        logger_instance.error.assert_called_once_with(
            "Unhandled exception: %s", test_exception, exc_info=True
        )

        # Verify the response
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert (
            response.body.decode("utf-8")
            == '{"detail":"Internal Server Error"}'
        )


@pytest.mark.asyncio
async def test_log_request_middleware_body_read_exception():
    """
    Test the middleware logs a warning if reading the request body
    raises an exception.

    This test ensures:
    - An exception during reading the request body is logged as a warning.
    - The middleware proceeds to process the response.
    """
    # Mock request object with body raising an exception
    mock_request = MagicMock(spec=Request)
    mock_request.method = "POST"
    mock_request.url = "http://testserver/api"
    mock_request.body = AsyncMock(side_effect=Exception("Body read error"))

    # Mock call_next to simulate a response
    mock_response = MagicMock(status_code=200)
    mock_call_next = AsyncMock(return_value=mock_response)

    with patch("logging.getLogger") as mock_get_logger:
        logger_instance = mock_get_logger.return_value

        # Call the middleware function directly
        response = await log_requests_middleware(mock_request, mock_call_next)

        # Verify the logger warning was called
        logger_instance.warning.assert_called_once()
        logged_message, logged_exception = logger_instance.warning.call_args[0]
        assert logged_message == "Could not read request body: %s"
        assert isinstance(logged_exception, Exception)
        assert str(logged_exception) == "Body read error"

        # Ensure the middleware proceeds to return the response
        assert response == mock_response
