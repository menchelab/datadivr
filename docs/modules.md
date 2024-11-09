# Modules in `datadivr`

## Handlers

The `datadivr.handlers` module provides functionality for registering WebSocket handlers. Handlers can be used for both client and server communication.

### `websocket_handler`

The `websocket_handler` decorator allows you to register a function as a handler for a specific WebSocket event.

**Parameters**:

- `event_name`: The name of the event to register the handler for.
- `handler_type`: Specifies where the handler should be registered (SERVER, CLIENT, or BOTH).

**Example**:

```python
@websocket_handler("sum_event", HandlerType.BOTH)
async def sum_handler(message: WebSocketMessage) -> Optional[WebSocketMessage]:
    ...

```

## Models

The `datadivr.models` module defines the `WebSocketMessage` model, which represents the structure of messages sent over WebSocket.

### `WebSocketMessage`

**Attributes**:

- `event_name`: The name of the event.
- `payload`: Optional data associated with the event.
- `to`: The recipient of the message (default is "others").
- `from_id`: The sender's identifier (default is "server").
- `message`: Optional text message.

**Example**:

```python
message = WebSocketMessage(
    event_name="sum_event",
    payload={"numbers": [1, 2, 3]},
    to="all",
    from_id="client1",
    message="Calculate sum"
)
```
