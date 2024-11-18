# WebSocket Client

The datadivr client provides a simple interface for connecting to a WebSocket server and handling real-time communication.

## Basic Usage

```python
import asyncio
from datadivr import WebSocketClient, HandlerType, websocket_handler, WebSocketMessage
from typing import Optional

# Define handlers
@websocket_handler("sum_handler_result", HandlerType.CLIENT)
async def handle_sum_result(message: WebSocketMessage) -> None:
    """Handle the result of a sum calculation."""
    print(f"Sum result from {message.from_id}: {message.payload}")

@websocket_handler("msg", HandlerType.CLIENT)
async def msg_handler(message: WebSocketMessage) -> None:
    """Handle text messages."""
    print(f">> {message.from_id}: '{message.message}'")

# Create and run client
async def run_client() -> None:
    # Create and connect client
    client = WebSocketClient("ws://localhost:8765/ws")
    await client.connect()

    # Send a calculation request
    await client.send_message(
        payload={"numbers": [391, 29]},
        event_name="sum_event"
    )

    # Create tasks for message handling
    tasks = [
        asyncio.create_task(client.receive_messages()),
    ]

    try:
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            task.cancel()
        await client.disconnect()

# Run the client
asyncio.run(run_client())
```

## Built-in Handlers

The client comes with several built-in handlers:

### Sum Handler

```python
@websocket_handler("sum_event_client", HandlerType.CLIENT)
async def sum_handler(message: WebSocketMessage) -> None:
    """Handle sum calculation results."""
    print(f"Sum result from {message.from_id}: {message.payload}")
```

### Message Handler

```python
@websocket_handler("msg", HandlerType.CLIENT)
async def msg_handler(message: WebSocketMessage) -> None:
    """Handle text messages."""
    print(f">> {message.from_id}({message.event_name}): '{message.message}'")
```

## Interactive Usage

Here's how the CLI client uses these handlers:

```python
async def run_client() -> None:
    # Create and connect client
    client = WebSocketClient(f"ws://{host}:{port}/ws")
    await client.connect()

    # Create tasks for message handling and user input
    tasks = [
        asyncio.create_task(client.receive_messages()),
        asyncio.create_task(input_loop(client)),
    ]

    try:
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            task.cancel()
        await client.disconnect()

# Example JSON messages to send:
# Sum calculation:
{"event_name": "sum_event", "payload": {"numbers": [391, 29]}}
# Broadcast message:
{"event_name": "msg", "to": "all", "message": "hello"}
```

## Message Types

1. **Sum Calculation**:

   ```python
   await client.send_message(
       payload={"numbers": [1, 2, 3]},
       event_name="sum_event"
   )
   ```

2. **Text Messages**:

   ```python
   await client.send_message(
       message="Hello everyone!",
       event_name="msg",
       to="all"
   )
   ```

3. **Custom Events**:

   ```python
   await client.send_message(
       payload={"data": "custom_data"},
       event_name="custom_event",
       to="specific_client_id"
   )
   ```

## Error Handling

The client handles several error conditions:

- `NotConnectedError`: Raised when trying to send messages before connecting
- `ConnectionClosed`: Handled during message reception
- Invalid message formats: Logged and handled gracefully

## Connection Lifecycle

1. **Connection**:

   ```python
   client = WebSocketClient("ws://localhost:8765/ws")
   await client.connect()  # Automatically registers handlers
   ```

2. **Message Loop**:

   ```python
   # Start receiving messages (blocks until connection closes)
   await client.receive_messages()
   ```

3. **Disconnection**:

   ```python
   await client.disconnect()  # Clean up connection
   ```

## Reference

::: datadivr.transport.client.WebSocketClient
options:
show_root_heading: true
show_source: true
