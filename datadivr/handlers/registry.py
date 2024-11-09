from collections.abc import Awaitable
from enum import Enum, auto
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from datadivr.transport.models import WebSocketMessage

T = TypeVar("T", bound=Callable[..., Awaitable[Optional[WebSocketMessage]]])


class HandlerType(Enum):
    """Type of handler to register."""

    SERVER = auto()
    CLIENT = auto()
    BOTH = auto()


# Separate registries for server and client handlers
_server_handlers: dict[str, Callable[[WebSocketMessage], Awaitable[Optional[WebSocketMessage]]]] = {}
_client_handlers: dict[str, Callable[[WebSocketMessage], Awaitable[Optional[WebSocketMessage]]]] = {}


def get_handlers(
    handler_type: HandlerType = HandlerType.SERVER,
) -> dict[str, Callable[[WebSocketMessage], Awaitable[Optional[WebSocketMessage]]]]:
    """
    Get registered handlers for the specified type.

    Args:
        handler_type: Type of handlers to retrieve (SERVER or CLIENT)
    """
    if handler_type == HandlerType.SERVER:
        return _server_handlers
    return _client_handlers


def websocket_handler(
    event_name: str, handler_type: HandlerType = HandlerType.SERVER
) -> Callable[
    [Callable[..., Awaitable[Optional[WebSocketMessage]]]], Callable[..., Awaitable[Optional[WebSocketMessage]]]
]:
    """
    Decorator to register a websocket handler function.

    Args:
        event_name: The event name to register the handler for.
        handler_type: Where this handler should be registered (SERVER, CLIENT, or BOTH)

    Example:
        @websocket_handler("sum_event", HandlerType.BOTH)
        async def sum_handler(message: WebSocketMessage) -> Optional[WebSocketMessage]:
            ...
    """

    def decorator(
        func: Callable[..., Awaitable[Optional[WebSocketMessage]]],
    ) -> Callable[..., Awaitable[Optional[WebSocketMessage]]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Optional[WebSocketMessage]:
            return await func(*args, **kwargs)

        if handler_type in (HandlerType.SERVER, HandlerType.BOTH):
            _server_handlers[event_name] = wrapper
        if handler_type in (HandlerType.CLIENT, HandlerType.BOTH):
            _client_handlers[event_name] = wrapper

        return wrapper

    return decorator
