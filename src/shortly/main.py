"""
Main entry point for the Shortly URL Shortener application.

This module initializes and runs the FastAPI application for Shortly. It:
- Registers API routes for URL shortening, retrieval, analytics, and more.
- Configures application-wide middleware and exception handlers.
- Provides command-line interface (CLI) options for configuring the server.

Key Features:
- Dynamic CLI options for host, port, reload, and debug mode.
- Middleware for logging HTTP requests and responses.
- Exception handling to capture and log unhandled errors.

Usage:
    python -m src.shortly.main -h 127.0.0.1 -p 8000 -r --debug
"""

import os
import uvicorn
import click
from fastapi import FastAPI
from .routes import register_routes
from .logging import (
    configure_logging,
    log_requests_middleware,
    log_exception_handler,
)

app = FastAPI(title="Shortly: URL Shortener")
register_routes(app)

app.middleware("http")(log_requests_middleware)
app.add_exception_handler(Exception, log_exception_handler)


@click.command()
@click.option(
    "-h",
    "--host",
    default=None,
    help=("Host to bind. Overridden by APP_HOST environment variable."),
)
@click.option(
    "-p",
    "--port",
    default=None,
    type=int,
    help=("Port to bind. Overridden by APP_PORT environment variable."),
)
@click.option(
    "-r",
    "--reload",
    is_flag=True,
    help=("Enable reload. Overridden by APP_RELOAD environment variable."),
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help=(
        "Enable debug logging. Overridden by APP_DEBUG environment variable."
    ),
)
def main(host, port, reload, debug):
    """
    Run the Shortly API server with configurable options.
    """
    host = os.getenv("APP_HOST", host or "0.0.0.0")
    port = int(os.getenv("APP_PORT", port or 8000))
    reload = os.getenv("APP_RELOAD", str(reload or "false")).lower() == "true"
    debug = os.getenv("APP_DEBUG", str(debug or "false")).lower() == "true"

    logger = configure_logging(debug)

    logger.info(
        "Starting server at %s:%d with reload=%s debug=%s",
        host,
        port,
        reload,
        debug,
    )

    uvicorn.run(
        "src.shortly.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="debug" if debug else "info",
    )


if __name__ == "__main__":
    import sys

    main.main(prog_name="main", standalone_mode=False, args=sys.argv[1:])
