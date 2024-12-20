"""Web server implementation for serving static files in datadivr.

This module provides functionality for serving static files using FastAPI.

Example:    ```python
    import uvicorn
    from datadivr.transport.web_server import create_static_app

    app = create_static_app(static_dir="static")
    uvicorn.run(app, host="127.0.0.1", port=8765)    ```
"""

from pathlib import Path
from typing import Optional, Union

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from datadivr.exceptions import StaticDirectoryNotFoundError
from datadivr.utils.logging import get_logger

logger = get_logger(__name__)


def add_static_routes(
    app: FastAPI,
    static_dir: Optional[Union[str, Path]] = None,
    static_url: str = "/static",
) -> None:
    """Add static file serving routes to an existing FastAPI application.

    Args:
        app: Existing FastAPI application to add routes to
        static_dir: Directory containing static files to serve
        static_url: URL path where static files will be served

    Raises:
        FileNotFoundError: If the static directory doesn't exist
    """
    # If no static directory specified, use default in package
    if static_dir is None:
        static_dir = Path(__file__).parent.parent / "static"
        logger.debug("using_default_static_dir", path=str(static_dir))
    else:
        static_dir = Path(static_dir)
        logger.debug("using_provided_static_dir", path=str(static_dir))

    # Ensure static directory exists
    if not static_dir.exists():
        logger.error("static_directory_not_found", path=str(static_dir))
        raise StaticDirectoryNotFoundError(str(static_dir))
    logger.debug("static_directory_verified", path=str(static_dir))

    # Mount static files to existing app
    app.mount(
        static_url,
        StaticFiles(directory=str(static_dir), html=True),
        name="static",
    )
    logger.debug("static_files_mounted", url=static_url)
