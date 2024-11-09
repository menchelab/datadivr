from typing import Any, ClassVar, Optional

from pydantic import BaseModel, Field


class WebSocketMessage(BaseModel):
    """Base model for WebSocket messages."""

    event_name: str
    payload: Optional[Any] = None
    to: str = Field(default="others")
    from_id: str = Field(default="server", alias="from")
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
