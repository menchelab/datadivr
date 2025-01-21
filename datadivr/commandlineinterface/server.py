"""Server-side CLI functionality."""

import asyncio
from typing import Optional

import uvicorn
from fastapi import FastAPI

from datadivr.transport.server import app as websocket_app
from datadivr.transport.web_server import add_static_routes
from datadivr.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


def start_server_app(
    host: str,
    port: int,
    static_dir: Optional[str],
    log_level: str,
    pretty: bool,
) -> None:
    """Start WebSocket and static file server."""
    setup_logging(level=log_level, pretty=pretty)

    # get fastapi instance
    app = FastAPI()

    # websocket router
    app.router.lifespan_context = websocket_app.router.lifespan_context
    app.include_router(websocket_app.router)

    # webserver static file server
    add_static_routes(app, static_dir=static_dir or "./static")

    logger.info("server_starting", host=host, port=port)

    # too much data with debug loglvl
    # removed loglevel='log_level'
    config = uvicorn.Config(app, host=host, port=port)
    config.log_config = None
    asyncio.run(uvicorn.Server(config).serve())
