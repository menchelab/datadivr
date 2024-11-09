# Command Line Interface

## Basic Commands

### Start Server

```bash
uv run datadivr start-server [--port PORT] [--host HOST]
```

Options:

- `--port`: Port number (default: 8765)
- `--host`: Host address (default: 127.0.0.1)

### Start Client

```bash
uv run datadivr start-client [--port PORT] [--host HOST]
```

## Client Input Format

The client accepts JSON messages in this format:

```json
{
  "event_name": "sum_event",
  "payload": { "numbers": [1, 2, 3] },
  "to": "all"
}
```

Common event types:

- `sum_event`: Calculate sum of numbers
- `msg`: Send text message
