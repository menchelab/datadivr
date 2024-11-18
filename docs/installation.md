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
git clone https://github.com/menchelab/datadivr.git
cd datadivr
```

## Development

For information about setting up a development environment, running tests, and contributing to the project, please see our [Contributing Guide](/contributing/).

## Verifying Installation

```bash
# If installed
uv run datadivr --help

# Or without installing
uvx datadivr --help
```
