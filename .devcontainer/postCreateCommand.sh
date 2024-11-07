#! /usr/bin/env bash

git config --global --add safe.directory /workspaces/datadivr

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Install Dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install --install-hooks
