import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from datadivr.utils.logging import get_logger

# Custom type for RGBA colors - list of 4 numbers: [r, g, b, a]
# a is the alpha value, TODO: use float? 0-255 or
RGBAColor = tuple[int, int, int, int]
"""Type alias for RGBA colors represented as a tuple of 4 integers (r,g,b,a)."""

logger = get_logger(__name__)

class Link(BaseModel):
    """Represents a connection between two nodes in the project graph.

    Attributes:
        start: ID of the source node
        end: ID of the target node
        linkcolor: RGBA color tuple for visual representation
    """
    start: int
    end: int
    linkcolor: RGBAColor

class LayoutNodePosition(BaseModel):
    """Defines the 3D position and color of a node in a specific layout.

    Attributes:
        node_id: Reference to the Node.id
        x: X-coordinate in 3D space
        y: Y-coordinate in 3D space
        z: Z-coordinate in 3D space
        nodecolor: RGBA color tuple for visual representation
    """
    node_id: int
    x: float
    y: float
    z: float
    nodecolor: RGBAColor

class Layout(BaseModel):
    name: str
    node_positions: list[LayoutNodePosition]

class SelectionNodes(BaseModel):
    node_ids: list[int]
    create_clusternode: bool

class Selection(BaseModel):
    name: str
    label_color: RGBAColor
    nodes: SelectionNodes

class Node(BaseModel):
    id: int
    name: str
    attributes: dict[str, str] = Field(default_factory=dict)

class Project(BaseModel):
    """Root model representing a DataDiVR project.

    This model contains all data necessary to represent and visualize
    a network of nodes, their connections, and various layouts.

    Attributes:
        name: Project display name
        attributes: Optional key-value pairs for project metadata
        nodes: List of Node objects in the project
        links: List of Link objects defining node connections
        layouts: List of Layout configurations
        selections: Optional list of node Selection groups

    Example:
        ```python
        project = Project(
            name="My Project",
            nodes=[Node(id=1, name="Node 1")],
            links=[],
            layouts=[],
            selections=[]
        )
        ```
    """
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Example Project",
                    "nodes": [{"id": 1, "name": "First Node"}],
                    "links": [],
                    "layouts": []
                }
            ]
        }
    }

    name: str
    attributes: dict[str, str] = Field(
        default_factory=dict,
        description="Custom metadata key-value pairs"
    )
    nodes: list[Node]
    links: list[Link]
    layouts: list[Layout]
    selections: Optional[list[Selection]] = []

    @classmethod
    def load_from_json_file(cls, file_path: Path | str) -> "Project":
        """Load a project from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Project: Loaded and validated Project instance

        Raises:
            ValidationError: If the JSON data doesn't match the expected schema
            OSError: If there are file access issues
        """
        file_path = Path(file_path)
        logger.debug("Loading project", file_path=str(file_path))

        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                project = cls.model_validate(data)
                logger.info("Project loaded successfully", project_name=project.name)
                return project
        except Exception as e:
            logger.exception("Failed to load project", error=str(e))
            raise

    def save_to_json_file(self, file_path: Path | str) -> None:
        """Save the project to a JSON file."""
        file_path = Path(file_path)
        logger.debug("Saving project", file_path=str(file_path))

        try:
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(self.model_dump(), f, indent=2)
            logger.info("Project saved successfully", project_name=self.name)
        except Exception as e:
            logger.exception("Failed to save project", error=str(e))
            raise
