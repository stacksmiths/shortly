"""
Health check utilities for the Shortly application.

This module provides:
- Dynamic calculation of the application's health status.
- Simulated diagnostics for essential application routes.
- Uptime tracking since the application start.

Key Features:
- Checks the health of critical routes such as `/shorten` and `/health`.
- Provides structured health status including overall status, uptime,
  and individual component statuses.
- Simulates route responses to evaluate service availability.

Usage:
    - Call `get_health_status()` to retrieve the current health status.
    - Use `check_essential_routes()` to check the health of key routes.
    - Use `check_health()` to encapsulate reusable health-check logic.
"""

import logging
from datetime import datetime

# Application start time
start_time = datetime.now()


def check_essential_routes() -> str:
    """
    Check the health of essential application routes.

    Returns:
        str: "up" if routes respond as expected, otherwise "down".
    """
    logger = logging.getLogger("Shortly")
    try:
        essential_routes = ["/shorten", "/health"]
        for route in essential_routes:
            if not simulate_route_response(route):
                logger.debug("Route %s is down", route)
                return "down"
        logger.debug("All essential routes are up")
        return "up"
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.error("Unexpected exception while checking routes: %s", exc)
        return "down"


def simulate_route_response(route: str) -> bool:
    """
    Simulate route response for diagnostics.

    Args:
        route (str): The route to simulate a response for.

    Returns:
        bool: True if the route is healthy, False otherwise.
    """
    logger = logging.getLogger("Shortly")
    if route in ["/shorten", "/health"]:
        logger.debug("Simulated response for route %s: Healthy", route)
        return True
    logger.debug("Simulated response for route %s: Unhealthy", route)
    return False


def check_health() -> dict:
    """
    Calculate the dynamic health status of the application.

    Returns:
        dict: Health status, uptime, and components' statuses.
    """
    logger = logging.getLogger("Shortly")
    route_status = check_essential_routes()

    overall_status = "healthy" if route_status == "up" else "unhealthy"
    uptime = str(datetime.now() - start_time)

    logger.debug("Health status calculated: %s, Uptime: %s", overall_status,
                 uptime)

    return {
        "status": overall_status,
        "uptime": uptime,
        "components": {
            "routes": route_status,
        },
    }


def get_health_status() -> str:
    """
    Calculate and return the overall health status as a string.

    Returns:
        str: "healthy" if the application is healthy, otherwise "unhealthy".
    """
    logger = logging.getLogger("Shortly")
    route_status = check_essential_routes()

    overall_status = "healthy" if route_status == "up" else "unhealthy"
    logger.info("Health status calculated: %s", overall_status)

    return overall_status
