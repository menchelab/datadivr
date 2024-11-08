import asyncio

import uvicorn

from datadivr.handlers.sum_handler import sum_handler
from datadivr.server import app, register_handler


async def main() -> None:
    register_handler("sum_event", sum_handler)

    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server_instance = uvicorn.Server(config)
    await server_instance.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server shutdown gracefully.")
