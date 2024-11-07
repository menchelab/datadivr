from typing import Any, Optional

from fastapi import WebSocket


class Message:
    def __init__(
        self,
        event_name: str,
        payload: Any = None,
        to: str = "others",
        from_id: str = "server",
        message: Optional[str] = None,
    ):
        self.event_name = event_name
        self.payload = payload
        self.to = to
        self.from_id = from_id
        self.message = message

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_name": self.event_name,
            "payload": self.payload,
            "to": self.to,
            "from": self.from_id,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        return cls(
            event_name=data["event_name"],
            payload=data.get("payload"),
            to=data.get("to", "others"),
            from_id=data.get("from", "server"),
            message=data.get("message"),
        )


async def send_message(websocket: WebSocket, message: Message) -> None:
    """Send a message through the websocket."""
    await websocket.send(message.to_dict())


def create_error_message(error_msg: str, to: str) -> Message:
    """Create a standardized error message."""
    return Message(event_name="error", message=error_msg, to=to)


def create_message(event_name: str, payload: Any, to: str, message: Optional[str] = None) -> Message:
    """Create a standardized  message."""
    return Message(event_name=event_name, payload=payload, to=to, message=message)
