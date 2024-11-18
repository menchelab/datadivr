# WebSocket Server

The datadivr server provides a FastAPI-based WebSocket server that handles client connections, message routing, and event handling.

## Basic Usage

```python
import uvicorn
from datadivr import app, HandlerType, websocket_handler, WebSocketMessage
from datadivr.transport.messages import create_error_message

# Define handlers
@websocket_handler("sum_event", HandlerType.SERVER)
async def sum_handler(message: WebSocketMessage) -> WebSocketMessage:
    """Calculate sum of numbers in the payload."""
    try:
        numbers = message.payload.get("numbers")
        if not isinstance(numbers, list):
            return create_error_message(
                "Payload must contain a list of numbers",
                message.from_id
            )

        result = sum(float(n) for n in numbers)
        return WebSocketMessage(
            event_name="sum_handler_result",
            payload=result,
            to=message.from_id,
        )
    except Exception as e:
        return create_error_message(f"Error: {e}", message.from_id)

# Start the server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765)
```

## Built-in Handlers

The server comes with built-in handlers for common operations:

### Sum Handler

```python
@websocket_handler("sum_event", HandlerType.SERVER)
async def sum_handler(message: WebSocketMessage) -> WebSocketMessage:
    """Calculate sum of numbers in the payload."""
    try:
        numbers = message.payload.get("numbers")
        result = sum(float(n) for n in numbers)
        return WebSocketMessage(
            event_name="sum_handler_result",
            payload=result,
            to=message.from_id,
        )
    except Exception as e:
        return create_error_message(f"Error: {e}", message.from_id)
```

## Server Implementation

The server uses FastAPI and maintains a registry of connected clients:

```python
# Module-level state
clients: dict[WebSocket, str] = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Handle incoming WebSocket connections."""
    await handle_connection(websocket)

async def handle_connection(websocket: WebSocket) -> None:
    """Manage client connection lifecycle."""
    await websocket.accept()
    client_id = str(uuid.uuid4())
    clients[websocket] = client_id

    try:
        while True:
            data = await websocket.receive_json()
            message = WebSocketMessage.model_validate(data)
            message.from_id = client_id
            response = await handle_msg(message)
            if response is not None:
                await broadcast(response, websocket)
    except WebSocketDisconnect:
        del clients[websocket]
```

## Message Broadcasting

The server supports three broadcasting modes:

1. **All Clients**:

```python
message = WebSocketMessage(
    event_name="announcement",
    message="Server maintenance in 5 minutes",
    to="all"
)
```

2. **Other Clients**:

```python
message = WebSocketMessage(
    event_name="user_joined",
    message="New user connected",
    to="others"
)
```

3. **Specific Client**:

```python
message = WebSocketMessage(
    event_name="private_message",
    message="Your request was processed",
    to="client_123"
)
```

## Error Handling

The server handles various error conditions:

- Invalid message formats
- Client disconnections
- Message broadcasting failures

All errors are logged using structured logging via `structlog`:

```python
try:
    message = WebSocketMessage.model_validate(data)
except ValueError as e:
    logger.exception("invalid_message_format",
                    error=str(e),
                    client_id=client_id)
    raise InvalidMessageFormat()
```

## Reference

::: datadivr.transport.server
options:
show_root_heading: true
show_source: true
