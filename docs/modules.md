# Core Components

## WebSocket Message

The `WebSocketMessage` class is the core data structure:

```python
from datadivr import WebSocketMessage

message = WebSocketMessage(
    event_name="sum_event",
    payload={"numbers": [1, 2, 3]},
    to="all",
    message="Calculate sum"
)
```

## Handlers

Register custom handlers using the `@websocket_handler` decorator:

```python
from datadivr import HandlerType, websocket_handler

@websocket_handler("custom_event", HandlerType.SERVER)
async def handle_custom(message: WebSocketMessage) -> Optional[WebSocketMessage]:
    # Handle the message
    return response_message
```

## Client Usage

```python
from datadivr import WebSocketClient

client = WebSocketClient("ws://localhost:8765/ws")
await client.connect()
await client.send_message(
    payload={"numbers": [1, 2, 3]},
    event_name="sum_event"
)
```

## Server Usage

```python
from datadivr import app
import uvicorn

uvicorn.run(app, host="127.0.0.1", port=8765)
```
