from typing import Any, ClassVar, Optional

from pydantic import BaseModel, Field


class WebSocketMessage(BaseModel):
    """A model representing a WebSocket message.

    This model defines the structure of messages sent between WebSocket clients and servers.
    It includes fields for event identification, payload data, routing information, and optional
    text messages.

    Attributes:
        event_name: The name of the event this message represents
        payload: Optional data associated with the message
        to: The recipient identifier (defaults to "others")
        from_id: The sender identifier (defaults to "server")
        message: Optional text message content

    Example:
        ```python
        message = WebSocketMessage(
            event_name="data_update",
            payload={"value": 42},
            to="client_123",
            from_id="server",
            message="Updated data value"
        )
        ```
    """

    event_name: str
    payload: Optional[Any] = None
    to: str = Field(default="others")
    from_id: str = Field(default="server")
    message: Optional[str] = None

    ConfigDict: ClassVar[dict] = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "event_name": "sum_event",
                "payload": {"numbers": [1, 2, 3]},
                "to": "all",
                "from": "client1",
                "message": "Calculate sum",
            }
        },
    }
