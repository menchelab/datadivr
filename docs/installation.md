# Installation

## Using uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install datadivr
uv pip install datadivr
```

## Running Without Installation

You can run datadivr directly without installing using `uvx`:

```bash
# Run datadivr CLI directly
uvx datadivr --help

# Start server
uvx datadivr start-server --port 8765

# Start client
uvx datadivr start-client --port 8765
```

## Development Setup

1. Clone the repository:

```bash
git clone https://github.com/menchelab/datadivr.git
cd datadivr
```

2. Install dependencies:

```bash
uv sync
```

3. Install pre-commit hooks:

```bash
uv run pre-commit install
```

## Development Commands

The project includes a Makefile with common development tasks:

```bash
# Install dependencies and pre-commit hooks
make install

# Run all code quality checks
make check

# Run tests with coverage
make test

# Build package
make build

# Build and serve documentation
make docs

# Show all available commands
make help
```

## Running Tests

### Single Python Version

```bash
# Run tests with coverage
make test
```

### Multiple Python Versions

To test against multiple Python versions (3.9-3.13), use tox with uv:

```bash
# Install required Python versions first
# Then run tox using uv
uv run tox

# To run for specific Python version(s)
uv run tox -e py39,py310
```

Supported environments:

- py39 (Python 3.9)
- py310 (Python 3.10)
- py311 (Python 3.11)
- py312 (Python 3.12)
- py313 (Python 3.13)

## Verifying Installation

```bash
# If installed
uv run datadivr --help

# Or without installing
uvx datadivr --help
```
