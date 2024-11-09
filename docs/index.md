# datadivr

[![Release](https://img.shields.io/github/v/release/menchelab/datadivr)](https://img.shields.io/github/v/release/menchelab/datadivr)
[![Build status](https://img.shields.io/github/actions/workflow/status/menchelab/datadivr/main.yml?branch=main)](https://github.com/menchelab/datadivr/actions/workflows/main.yml?query=branch%3Amain)
[![License](https://img.shields.io/github/license/menchelab/datadivr)](https://img.shields.io/github/license/menchelab/datadivr)

A WebSocket-based data communication framework for Python.

## Quick Start

1. Install using uv (recommended):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install datadivr
```

2. Start a WebSocket server:

```bash
uv run datadivr start-server --port 8765
```

3. Connect a client:

```bash
uv run datadivr start-client --port 8765
```

## Key Features

- Simple WebSocket server and client implementation
- Event-based message handling
- Built-in handlers for common operations
- Easy-to-use CLI interface

## Example Usage

Send a message to calculate a sum:

```json
{
  "event_name": "sum_event",
  "payload": { "numbers": [1, 2, 3] },
  "to": "all"
}
```

Send a broadcast message:

```json
{
  "event_name": "msg",
  "message": "Hello everyone!",
  "to": "all"
}
```
