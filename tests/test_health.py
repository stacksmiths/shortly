"""
Unit tests for the Shortly application's health check utilities.

These tests cover:
- Simulated diagnostics of essential application routes.
- Overall health check functionality, including mock scenarios.
"""

from unittest.mock import patch
from src.shortly.health import (
    check_essential_routes,
    check_health,
    get_health_status,
    simulate_route_response,
)
from src.shortly.logging import configure_logging
import logging


def test_check_essential_routes():
    """
    Test the self-diagnostic route check.
    """
    # Case: All routes are healthy
    with patch(
        "src.shortly.health.simulate_route_response", return_value=True
    ):
        status = check_essential_routes()
        assert status == "up", "Expected status 'up' when routes are healthy"

    # Case: One route is unhealthy
    def mock_route_response(route):
        return route != "/health"

    with patch(
        "src.shortly.health.simulate_route_response",
        side_effect=mock_route_response,
    ):
        status = check_essential_routes()
        assert status == "down", "Expected status 'down' for unhealthy route"


def test_check_health():
    """
    Test the detailed health check status of the system.
    """
    # Mock healthy system
    with patch("src.shortly.health.check_essential_routes", return_value="up"):
        health_status = check_health()
        assert health_status["status"] == "healthy"
        assert health_status["components"]["routes"] == "up"

    # Mock unhealthy system
    with patch(
        "src.shortly.health.check_essential_routes", return_value="down"
    ):
        health_status = check_health()
        assert health_status["status"] == "unhealthy"
        assert health_status["components"]["routes"] == "down"


def test_check_essential_routes_exception_handling():
    """
    Test the route check for exception handling with centralized logging.
    """
    # Configure the logging utility
    logger = configure_logging(debug=True)

    # Case: Exception occurs during route simulation
    with patch(
        "src.shortly.health.simulate_route_response",
        side_effect=Exception("Test exception"),
    ):
        with patch.object(logger, "error") as mock_error_log:
            status = check_essential_routes()
            assert status == "down", (
                "Expected status 'down' when exception occurs"
            )
            mock_error_log.assert_called_once()
            logged_message, logged_exception = mock_error_log.call_args[0]
            assert logged_message == (
                "Unexpected exception while checking routes: %s"
            )
            assert isinstance(logged_exception, Exception)
            assert str(logged_exception) == "Test exception"


def test_simulate_route_response_unhealthy():
    """
    Test the route simulation for unhealthy routes with centralized logging.
    """
    # Configure the logging utility
    logger = logging.getLogger("Shortly")

    # Case: Route is unhealthy
    with patch.object(logger, "debug") as mock_debug_log:
        response = simulate_route_response("/invalid-route")
        assert response is False, (
            "Expected False for an unhealthy route"
        )
        mock_debug_log.assert_called_once_with(
            "Simulated response for route %s: Unhealthy",
            "/invalid-route",
        )


def test_get_health_status():
    """
    Test overall health status calculation with centralized logging.
    """


with patch(
    "src.shortly.health.check_essential_routes"
) as mock_check_routes:
    with patch("logging.getLogger") as mock_logger:
        logger_instance = mock_logger.return_value

        # Case: Application is healthy
        mock_check_routes.return_value = "up"
        status = get_health_status()
        assert status == "healthy", (
            "Expected status 'healthy' when routes are healthy"
        )
        logger_instance.info.assert_called_with(
            "Health status calculated: %s", "healthy"
        )

        # Case: Application is unhealthy
        mock_check_routes.return_value = "down"
        status = get_health_status()
        assert status == "unhealthy", (
            "Expected status 'unhealthy' when routes are unhealthy"
        )
        logger_instance.info.assert_called_with(
            "Health status calculated: %s", "unhealthy"
        )
