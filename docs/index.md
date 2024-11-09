# datadivr

[![Release](https://img.shields.io/github/v/release/menchelab/datadivr)](https://img.shields.io/github/v/release/menchelab/datadivr)
[![Build status](https://img.shields.io/github/actions/workflow/status/menchelab/datadivr/main.yml?branch=main)](https://github.com/menchelab/datadivr/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/menchelab/datadivr)](https://img.shields.io/github/commit-activity/m/menchelab/datadivr)
[![License](https://img.shields.io/github/license/menchelab/datadivr)](https://img.shields.io/github/license/menchelab/datadivr)

datadivr backend and toolset.

## Overview

`datadivr` is a WebSocket-based data communication framework that allows for easy registration and handling of WebSocket events.

### Key Features

- **WebSocket Handlers**: Use the `@websocket_handler` decorator to register functions that handle specific WebSocket events.
- **WebSocket Messages**: The `WebSocketMessage` model defines the structure of messages sent over WebSocket, including attributes like `event_name`, `payload`, `to`, `from_id`, and `message`.

## Running the CLI

To run the CLI, use the following command structure:

```bash
python -m datadivr.cli [command] [options]
```

### Commands

- **Start Server**:

  ```bash
  python -m datadivr.cli start_server --port 8765 --host 127.0.0.1
  ```

  This command starts the WebSocket server.

- **Start Client**:
  ```bash
  python -m datadivr.cli start_client --port 8765 --host 127.0.0.1
  ```
  This command starts the WebSocket client, allowing you to send messages to the server.

### Example JSON Format

When using the client, you can send messages in the following JSON format:

```json
{ "event_name": "sum_event", "payload": { "numbers": [391, 29] } }
```
