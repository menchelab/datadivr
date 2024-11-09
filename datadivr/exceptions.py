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


class UnsupportedWebSocketTypeError(DataDivrError):
    """Raised when an unsupported WebSocket type is used."""

    def __init__(self, message: str = "Unsupported WebSocket type") -> None:
        super().__init__(message)
