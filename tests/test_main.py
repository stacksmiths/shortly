"""
Unit tests for the Shortly application's main CLI functionality.

These tests cover:
- Default configuration values when no CLI arguments or environment variables
are provided.
- Overriding defaults with custom CLI arguments.
- Overriding both defaults and CLI arguments with environment variables.

Each test ensures:
- Proper parsing and prioritization of configuration inputs (defaults,
CLI arguments, and environment variables).
- `uvicorn.run` is called with the correct arguments for each scenario.
"""

from unittest.mock import patch
import os
from click.testing import CliRunner
from src.shortly.main import main


def test_main_default_configuration():
    """
    Test the main function with default configuration.

    This test ensures:
    - Default host, port, reload, and debug values are used.
    - `uvicorn.run` is called with the correct default arguments.
    """
    with patch("src.shortly.main.uvicorn.run") as mock_uvicorn_run:
        runner = CliRunner()
        result = runner.invoke(main, [])

        # Ensure the command executed successfully
        assert result.exit_code == 0

        # Verify default arguments passed to uvicorn.run
        mock_uvicorn_run.assert_called_once_with(
            "src.shortly.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
        )


def test_main_with_custom_arguments():
    """
    Test the main function with custom CLI arguments.

    This test ensures:
    - CLI arguments override the default configuration values.
    - `uvicorn.run` is called with the correct custom arguments.
    """
    with patch("src.shortly.main.uvicorn.run") as mock_uvicorn_run:
        runner = CliRunner()
        result = runner.invoke(
            main, ["-h", "127.0.0.1", "-p", "9000", "-r", "-d"]
        )

        # Ensure the command executed successfully
        assert result.exit_code == 0

        # Verify custom arguments passed to uvicorn.run
        mock_uvicorn_run.assert_called_once_with(
            "src.shortly.main:app",
            host="127.0.0.1",
            port=9000,
            reload=True,
            log_level="debug",
        )


def test_main_with_environment_variables():
    """
    Test the main function with environment variables.

    This test ensures:
    - Environment variables override both defaults and CLI arguments.
    - `uvicorn.run` is called with the correct environment-configured
    arguments.
    """
    env_vars = {
        "APP_HOST": "192.168.1.1",
        "APP_PORT": "8080",
        "APP_RELOAD": "true",
        "APP_DEBUG": "true",
    }

    with (
        patch.dict(os.environ, env_vars),
        patch("src.shortly.main.uvicorn.run") as mock_uvicorn_run,
    ):
        runner = CliRunner()
        result = runner.invoke(main, [])

        # Ensure the command executed successfully
        assert result.exit_code == 0

        # Verify environment variable arguments passed to uvicorn.run
        mock_uvicorn_run.assert_called_once_with(
            "src.shortly.main:app",
            host="192.168.1.1",
            port=8080,
            reload=True,
            log_level="debug",
        )
