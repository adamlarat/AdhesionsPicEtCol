#!/bin/bash

# Function to check if Poetry is installed
check_poetry() {
    if ! command -v poetry &> /dev/null
    then
        echo "Poetry could not be found. Please install it first."
        echo "You can install Poetry by following the instructions at:"
        echo "https://python-poetry.org/docs/#installation"
        exit 1
    fi
}

# Function to install Poetry
install_poetry() {
    echo "Installing Poetry..."
    if curl -sSL https://install.python-poetry.org | python3 -; then
        echo "Poetry installed successfully."
        # Add Poetry to PATH for the current session
        export PATH="$HOME/.local/bin:$PATH"
    else
        echo "Failed to install Poetry. Please install it manually."
        echo "Visit https://python-poetry.org/docs/#installation for instructions."
        exit 1
    fi
}


# Main execution
if ! check_poetry; then
  install_poetry
fi

echo "Install virtualenv with poetry"
poetry install --no-interaction --no-root

echo "Process completed."
echo "Activate virtualenv with 'poetry shell'"
echo "Run python inside virtualenv with avec 'poetry run python'"
