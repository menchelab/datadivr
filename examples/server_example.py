import asyncio

from datadivr.handlers.sum_handler import sum_handler
from datadivr.server import WebSocketServer


async def main():
    server = WebSocketServer("localhost", 8765)
    server.register_handler("sum_event", sum_handler)  # Register sum handler
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
