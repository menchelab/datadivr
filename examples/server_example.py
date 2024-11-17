# this is now obsolete and will be removed in the next release
# look at cli.py for the new example

import asyncio

import uvicorn

# Import handlers to register them automatically
from datadivr.handlers import sum_handler  # noqa: F401
from datadivr.server import app


async def main() -> None:
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server_instance = uvicorn.Server(config)
    await server_instance.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server shutdown gracefully.")
