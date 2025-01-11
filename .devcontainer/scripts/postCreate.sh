#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status

# Display system information
echo "System Information:"
uname -a

# Install Poetry
echo "Installing Poetry..."
if ! command -v poetry &>/dev/null; then
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "Poetry is already installed."
fi

# Verify Poetry installation
if ! command -v poetry &>/dev/null; then
    echo "Error: Poetry installation failed."
    exit 1
fi

# Change to the project directory where pyproject.toml is located
PROJECT_DIR="/workspaces/test"  # Adjust this to your actual project path
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory $PROJECT_DIR does not exist."
    exit 1
fi
cd "$PROJECT_DIR"

# Configure Poetry to create virtual environments inside the project
poetry config virtualenvs.in-project true

# Check if existing virtual environment is managed by Poetry
VENV_DIR="$PROJECT_DIR/.venv"
if [ -d "$VENV_DIR" ]; then
    echo "Validating existing virtual environment..."
    POETRY_ENV_PATH=$(poetry env info --path 2>/dev/null || echo "")
    if [ "$POETRY_ENV_PATH" != "$VENV_DIR" ]; then
        echo "Existing virtual environment is not managed by Poetry. Removing it..."
        rm -rf "$VENV_DIR"
    else
        echo "Existing virtual environment is valid and managed by Poetry. Skipping removal."
    fi
fi

# Install dependencies via Poetry
echo "Installing dependencies with Poetry..."
LOG_FILE="/tmp/poetry_install.log"
poetry install --with dev &> "$LOG_FILE" &
POETRY_PID=$!

# Wait for the virtual environment to be created, with a timeout
echo "Waiting for virtual environment to be created at $VENV_DIR..."
TIMEOUT=300  # Timeout after 5 minutes
INTERVAL=1   # Check every second
PROGRESS_INTERVAL=10  # Display progress every 10 seconds
ELAPSED=0
NEXT_PROGRESS=$PROGRESS_INTERVAL

VENV_BIN_PATH="$VENV_DIR/bin"
while [ ! -d "$VENV_BIN_PATH" ]; do
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))

    # Display progress logs every PROGRESS_INTERVAL seconds
    if [ "$ELAPSED" -ge "$NEXT_PROGRESS" ]; then
        echo "Still waiting... Elapsed time: ${ELAPSED}s"
        echo "Latest logs:"
        tail -n 5 "$LOG_FILE" || echo "No logs available yet."
        NEXT_PROGRESS=$((NEXT_PROGRESS + PROGRESS_INTERVAL))
    fi

    # Check if timeout is reached
    if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
        echo "Error: Timeout reached. Virtual environment not created within $((TIMEOUT / 60)) minutes."
        echo "See $LOG_FILE for details."
        kill $POETRY_PID 2>/dev/null || true
        exit 1
    fi
done

# Ensure the Poetry process completes successfully
wait $POETRY_PID || {
    echo "Error: Poetry install failed. Check logs in $LOG_FILE."
    exit 1
}

echo "Virtual environment detected."

# Add Poetry virtual environment activation to .bashrc
if ! grep -Fxq "poetry env info --path" ~/.bashrc; then
    echo "Ensuring Poetry virtual environment activation in .bashrc..."
    {
        echo ""
        echo "# Automatically activate Poetry virtual environment for this project"
        echo "if [ -f \"pyproject.toml\" ]; then"
        echo "    VENV_PATH=\$(poetry env info --path 2>/dev/null)"
        echo "    if [ -d \"\$VENV_PATH\" ]; then"
        echo "        source \"\$VENV_PATH/bin/activate\""
        echo "    fi"
        echo "fi"
    } >>~/.bashrc
fi

# Load the updated .bashrc configuration for the current session
source ~/.bashrc

# Ensure the current shell session uses the Poetry environment
if [ -f "$VENV_BIN_PATH/activate" ]; then
    echo "Activating Poetry virtual environment..."
    source "$VENV_BIN_PATH/activate"
else
    echo "Error: Poetry virtual environment activation script not found at $VENV_BIN_PATH/activate."
    echo "The setup cannot continue without a valid Poetry environment."
    exit 1
fi

# Display completion message
echo "Development container setup complete!"
