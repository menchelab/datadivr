class DataDivrError(Exception):
    """Base exception for all datadivr errors."""

    pass


class WebSocketError(DataDivrError):
    """Base exception for WebSocket errors."""

    pass


class NotConnectedError(WebSocketError):
    """Exception raised when attempting to use a WebSocket that is not connected."""

    pass


class ConnectionLimitExceeded(WebSocketError):
    """Raised when max connections is exceeded."""

    pass


class InvalidMessageFormat(Exception):
    def __init__(self, message: str = "Invalid format") -> None:
        super().__init__(message)


class AuthenticationError(DataDivrError):
    """Raised when authentication fails."""

    pass


class UnsupportedWebSocketTypeError(Exception):
    """Exception raised when an unsupported WebSocket type is used."""

    def __init__(self) -> None:
        super().__init__("Unsupported WebSocket type")


class InputLoopInterrupted(Exception):
    """Custom exception for input loop interruption."""

    def __init__(self) -> None:
        super().__init__("Input loop interrupted")


class LayoutNotFoundError(ValueError):
    """Raised when a requested layout is not found in the project."""

    def __init__(self, layout_name: str, available_layouts: list[str]):
        self.layout_name = layout_name
        self.available_layouts = available_layouts
        super().__init__(f"Layout '{layout_name}' not found. " f"Available layouts: {available_layouts}")
