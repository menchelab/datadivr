# Installation

## Requirements

- Python 3.9 or higher

## Using pip

Install DataDivr using pip:

```bash
pip install datadivr
```

## Using uv (Recommended)

DataDivr can be installed and run using the modern Python package installer `uv`:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install datadivr
uv pip install datadivr

# Run datadivr CLI directly
uvx datadivr --help
```

## Development Installation

For development, clone the repository and install in editable mode:

```bash
git clone https://github.com/menchelab/datadivr.git
cd datadivr

# Using uv (recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

This will install all development dependencies including testing and documentation tools.

## Development Tools

DataDivr uses several tools to maintain code quality:

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality. Install them with:

```bash
pre-commit install
```

The hooks include:

- Code formatting with Ruff
- YAML/TOML validation
- Trailing whitespace removal
- Merge conflict checks
- Prettier for markdown/yaml formatting

### Continuous Integration

Our GitHub Actions workflows handle:

1. Quality Checks (`main.yml`):

   - Pre-commit hook validation
   - Unit tests across Python 3.9-3.13
   - Type checking with mypy
   - Code coverage reporting to Codecov
   - Documentation build verification

2. Release Process (`on-release-main.yml`):

   - Version updating
   - PyPI package publishing
   - Documentation deployment to GitHub Pages

3. Configuration Validation:
   - Codecov configuration validation

### Running Tests

```bash
# Run tests with coverage
uv run pytest tests --cov

# Type checking
uv run mypy

# Run all checks
make check
```

### Building Documentation

```bash
# Build docs
uv run mkdocs build

# Serve docs locally
uv run mkdocs serve
```

## Verifying Installation

After installation, verify it works by running:

```bash
# Using uv
uvx datadivr --help

# Or using standard installation
datadivr --help
```
