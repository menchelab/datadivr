from collections.abc import Awaitable
from enum import Enum, auto
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar, cast

from datadivr.transport.models import WebSocketMessage

P = ParamSpec("P")
T = TypeVar("T", bound=Callable[..., Awaitable[WebSocketMessage | None]])


class HandlerType(Enum):
    """Type of handler to register."""

    SERVER = auto()
    CLIENT = auto()
    BOTH = auto()


# Separate registries for server and client handlers
_server_handlers: dict[str, Callable[[WebSocketMessage], Awaitable[WebSocketMessage | None]]] = {}
_client_handlers: dict[str, Callable[[WebSocketMessage], Awaitable[WebSocketMessage | None]]] = {}


def get_handlers(
    handler_type: HandlerType = HandlerType.SERVER,
) -> dict[str, Callable[[WebSocketMessage], Awaitable[WebSocketMessage | None]]]:
    """
    Get registered handlers for the specified type.

    Args:
        handler_type: Type of handlers to retrieve (SERVER or CLIENT)
    """
    if handler_type == HandlerType.SERVER:
        return _server_handlers
    return _client_handlers


def websocket_handler(event_name: str, handler_type: HandlerType = HandlerType.SERVER) -> Callable[[T], T]:
    """
    Decorator to register a websocket handler function.

    Args:
        event_name: The event name to register the handler for.
        handler_type: Where this handler should be registered (SERVER, CLIENT, or BOTH)

    Example:
        @websocket_handler("sum_event", HandlerType.BOTH)
        async def sum_handler(message: WebSocketMessage) -> WebSocketMessage:
            ...
    """

    def decorator(func: T) -> T:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> WebSocketMessage | None:
            return await func(*args, **kwargs)

        if handler_type in (HandlerType.SERVER, HandlerType.BOTH):
            _server_handlers[event_name] = wrapper
        if handler_type in (HandlerType.CLIENT, HandlerType.BOTH):
            _client_handlers[event_name] = wrapper

        return cast(T, wrapper)

    return decorator
