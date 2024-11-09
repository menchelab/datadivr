# Command Line Interface

DataDivr provides a command-line interface for running WebSocket servers and clients.

## Running the CLI

You can run the CLI in two ways:

### Using uv (Recommended)

```bash
# Run directly with uvx
uvx datadivr start-server
uvx datadivr start-client
```

### Using Standard Installation

```bash
datadivr start-server
datadivr start-client
```

## Commands

### Start Server

Start a WebSocket server:

```bash
datadivr start-server [OPTIONS]
# or
uvx datadivr start-server [OPTIONS]
```

Options:

- `--port INTEGER`: Port to run the server on (default: 8765)
- `--host TEXT`: Host address to bind to (default: 127.0.0.1)

### Start Client

Start an interactive WebSocket client:

```bash
datadivr start-client [OPTIONS]
# or
uvx datadivr start-client [OPTIONS]
```

Options:

- `--port INTEGER`: Port to connect to (default: 8765)
- `--host TEXT`: Host address to connect to (default: 127.0.0.1)

## Interactive Client Usage

When using the client, you can send JSON messages in the following formats:

```json
# Calculate sum of numbers
{"event_name": "sum_event", "payload": {"numbers": [391, 29]}}

# Send message to all clients
{"event_name": "msg", "to": "all", "message": "hello"}

# Send message to other clients
{"event_name": "msg", "to": "others", "message": "hello"}

# Calculate sum on client side
{"event_name": "sum_event_client", "payload": {"numbers": [57, 12]}}
```

To exit the client, type `quit` or press Ctrl+C.

## Development and Testing

When developing or testing the CLI:

1. Install development dependencies:

   ```bash
   uv pip install -e ".[dev]"
   ```

2. Run tests specific to the CLI:

   ```bash
   uv run pytest tests/test_cli.py
   ```

3. Check type hints:

   ```bash
   uv run mypy datadivr/cli.py
   ```

The CLI is automatically tested in our CI pipeline across Python versions 3.9-3.13.
