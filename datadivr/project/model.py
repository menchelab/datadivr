import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
import numpy.typing as npt
import orjson
from pydantic import BaseModel, Field

from datadivr.utils.logging import get_logger

# Custom type for RGBA colors - list of 4 numbers: [r, g, b, a]
# a is the alpha value, TODO: use float? 0-255 or
RGBAColor = tuple[int, int, int, int]
"""Type alias for RGBA colors represented as a tuple of 4 integers (r,g,b,a)."""

logger = get_logger(__name__)


@dataclass
class NodeData:
    """Efficient storage for large node datasets"""

    ids: npt.NDArray[np.int32]  # Array of node IDs
    names: list[str]  # Parallel array of names, not using numpy dtype=object because actually worse
    attributes: dict[int, dict[str, str]]  # Sparse dictionary of attributes keyed by node ID


@dataclass
class LayoutData:
    """Efficient storage for layout positions"""

    node_ids: npt.NDArray[np.int32]  # Array of node IDs (N,)
    positions: npt.NDArray[np.float32]  # Array of positions (N, 3)
    colors: npt.NDArray[np.uint8]  # Array of RGBA colors (N, 4)


@dataclass
class LinkData:
    """Efficient storage for links"""

    start_ids: npt.NDArray[np.int32]  # Array of source IDs (M,)
    end_ids: npt.NDArray[np.int32]  # Array of target IDs (M,)
    colors: npt.NDArray[np.uint8]  # Array of RGBA colors (M, 4)


class SelectionNodes(BaseModel):
    node_ids: list[int]
    create_clusternode: bool


class Selection(BaseModel):
    name: str
    label_color: RGBAColor
    nodes: SelectionNodes


class LayoutNotFoundError(ValueError):
    """Raised when a requested layout is not found in the project."""

    pass


class Project(BaseModel):
    """Root model representing a DataDiVR project.

    This model contains all data necessary to represent and visualize
    a network of nodes, their connections, and various layouts using
    efficient data structures for large datasets.

    Attributes:
        name: Project display name
        attributes: Optional key-value pairs for project metadata
        nodes_data: Efficient storage for node data (ids, names, and attributes)
        links_data: Efficient storage for link data (start_ids, end_ids, and colors)
        layouts_data: Dictionary of layout configurations with efficient array storage
        selections: Optional list of node Selection groups

    Example:
        ```python
        project = Project(
            name="My Project",
            attributes={},
            nodes_data=NodeData(ids=np.array([1]), names=["Node 1"], attributes={}),
            links_data=None,
            layouts_data={},
            selections=[]
        )
        ```
    """

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {"name": "Example Project", "nodes": [{"id": 1, "name": "First Node"}], "links": [], "layouts": []}
            ]
        },
    }

    name: str
    attributes: dict[str, str] = Field(default_factory=dict, description="Custom metadata key-value pairs")

    # Change to public names
    nodes_data: Optional[NodeData] = None
    links_data: Optional[LinkData] = None
    layouts_data: dict[str, LayoutData] = Field(default_factory=dict)
    selections: Optional[list[Selection]] = []

    def add_nodes_bulk(
        self, ids: npt.NDArray[np.int32], names: list[str], attributes: Optional[dict[int, dict[str, str]]] = None
    ) -> None:
        """Efficiently add multiple nodes at once"""
        self.nodes_data = NodeData(ids=ids, names=names, attributes=attributes or {})

    def add_layout_bulk(
        self,
        name: str,
        node_ids: npt.NDArray[np.int32],
        positions: npt.NDArray[np.float32],
        colors: npt.NDArray[np.uint8],
    ) -> None:
        """Efficiently add layout data"""
        self.layouts_data[name] = LayoutData(node_ids=node_ids, positions=positions, colors=colors)

    def add_links_bulk(
        self, start_ids: npt.NDArray[np.int32], end_ids: npt.NDArray[np.int32], colors: npt.NDArray[np.uint8]
    ) -> None:
        """Efficiently add multiple links at once"""
        self.links_data = LinkData(start_ids=start_ids, end_ids=end_ids, colors=colors)

    def model_dump(
        self,
        *,
        mode: str = "python",
        include: Any = None,
        exclude: Any = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: Union[bool, str] = True,
        serialize_as_any: bool = False,
        context: Any = None,
    ) -> dict[str, Any]:
        """Custom serialization optimized for speed and memory efficiency"""
        # Convert numpy int32 keys to string keys for JSON compatibility
        attributes = {str(k): v for k, v in self.nodes_data.attributes.items()} if self.nodes_data else {}

        return {
            "name": self.name,
            "attributes": self.attributes,
            "nodes": {
                "ids": self.nodes_data.ids.astype(int).tolist() if self.nodes_data else [],
                "names": self.nodes_data.names if self.nodes_data else [],
                "attributes": attributes,
            },
            "links": {
                "start_ids": self.links_data.start_ids.astype(int).tolist() if self.links_data else [],
                "end_ids": self.links_data.end_ids.astype(int).tolist() if self.links_data else [],
                "colors": self.links_data.colors.tolist() if self.links_data else [],
            },
            "layouts": {
                str(name): {  # Convert layout name to string if it isn't already
                    "node_ids": layout.node_ids.astype(int).tolist(),
                    "positions": layout.positions.tolist(),
                    "colors": layout.colors.tolist(),
                }
                for name, layout in self.layouts_data.items()
            },
            "selections": [s.model_dump() for s in self.selections] if self.selections else [],
        }

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: Union[bool, None] = None,
        from_attributes: Union[bool, None] = None,
        context: Union[Any, None] = None,
    ) -> "Project":
        """Custom deserialization from efficient storage"""
        data = obj  # obj will contain our dictionary data
        project = cls(name=data["name"], attributes=data.get("attributes", {}))

        # Load nodes
        if "nodes" in data:
            project.nodes_data = NodeData(
                ids=np.array(data["nodes"]["ids"], dtype=np.int32),
                names=data["nodes"]["names"],
                attributes={int(k): v for k, v in data["nodes"]["attributes"].items()},
            )

        # Load links
        if "links" in data:
            project.links_data = LinkData(
                start_ids=np.array(data["links"]["start_ids"], dtype=np.int32),
                end_ids=np.array(data["links"]["end_ids"], dtype=np.int32),
                colors=np.array(data["links"]["colors"], dtype=np.uint8),
            )

        # Load layouts
        if "layouts" in data:
            for name, layout_data in data["layouts"].items():
                project.layouts_data[name] = LayoutData(
                    node_ids=np.array(layout_data["node_ids"], dtype=np.int32),
                    positions=np.array(layout_data["positions"], dtype=np.float32),
                    colors=np.array(layout_data["colors"], dtype=np.uint8),
                )

        # Load selections
        if "selections" in data:
            project.selections = [Selection.model_validate(s) for s in data["selections"]]

        return project

    @classmethod
    def load_from_json_file(cls, file_path: Union[Path, str]) -> "Project":
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

    def save_to_json_file(self, file_path: Union[Path, str]) -> None:
        """Save the project to a JSON file with optimized performance."""
        file_path = Path(file_path)
        logger.debug("Saving project", file_path=str(file_path))

        try:
            # Convert to JSON-compatible dict first
            data = self.model_dump()

            # Use a faster JSON encoder
            import orjson  # Much faster than standard json

            # Write in binary mode with orjson
            with file_path.open("wb") as f:
                f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2 | orjson.OPT_SERIALIZE_NUMPY))

            logger.info("Project saved successfully", project_name=self.name)
        except Exception as e:
            logger.exception("Failed to save project", error=str(e))
            raise

    def save_to_binary_file(self, file_path: Union[Path, str]) -> None:
        """Save the project using numpy binary format for large arrays."""
        file_path = Path(file_path)
        logger.debug("Saving project in binary format", file_path=str(file_path))

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                arrays_dir = temp_path / "arrays"
                arrays_dir.mkdir()

                # Save large arrays as numpy files
                if self.nodes_data:
                    np.save(arrays_dir / "node_ids.npy", self.nodes_data.ids)
                    # Save node names as numpy array
                    np.save(arrays_dir / "node_names.npy", np.array(self.nodes_data.names, dtype=object))
                    # Only attributes go to JSON now

                if self.links_data:
                    np.save(arrays_dir / "link_start_ids.npy", self.links_data.start_ids)
                    np.save(arrays_dir / "link_end_ids.npy", self.links_data.end_ids)
                    np.save(arrays_dir / "link_colors.npy", self.links_data.colors)

                # Save layouts
                for name, layout in self.layouts_data.items():
                    layout_dir = arrays_dir / f"layout_{name}"
                    layout_dir.mkdir()
                    np.save(layout_dir / "node_ids.npy", layout.node_ids)
                    np.save(layout_dir / "positions.npy", layout.positions)
                    np.save(layout_dir / "colors.npy", layout.colors)

                # Create metadata JSON (now without node names)
                metadata = {
                    "name": self.name,
                    "attributes": self.attributes,
                    "nodes": {
                        "attributes": {str(k): v for k, v in self.nodes_data.attributes.items()}
                        if self.nodes_data
                        else {}
                    },
                    "layouts": list(self.layouts_data.keys()),
                    "selections": [s.model_dump() for s in self.selections] if self.selections else [],
                }

                # Save metadata
                with open(temp_path / "metadata.json", "wb") as f:
                    f.write(orjson.dumps(metadata, option=orjson.OPT_INDENT_2))

                # Create zip archive
                with ZipFile(file_path, "w", compression=ZIP_DEFLATED) as zf:
                    # Add all files from temp directory
                    for file_path in temp_path.rglob("*"):
                        if file_path.is_file():
                            zf.write(file_path, file_path.relative_to(temp_path))

            logger.info("Project saved successfully in binary format", project_name=self.name)
        except Exception as e:
            logger.exception("Failed to save project in binary format", error=str(e))
            raise

    @classmethod
    def load_from_binary_file(cls, file_path: Union[Path, str]) -> "Project":
        """Load a project from a binary format file."""
        file_path = Path(file_path)
        logger.debug("Loading project from binary format", file_path=str(file_path))

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Extract zip archive
                with ZipFile(file_path, "r") as zf:
                    zf.extractall(temp_path)

                # Load metadata
                with open(temp_path / "metadata.json", "rb") as f:
                    metadata = orjson.loads(f.read())

                # Create project instance
                project = cls(name=metadata["name"], attributes=metadata.get("attributes", {}))

                # Load nodes
                if "nodes" in metadata:
                    node_ids = np.load(temp_path / "arrays/node_ids.npy")
                    # Add allow_pickle=True for object arrays (strings)
                    node_names = np.load(temp_path / "arrays/node_names.npy", allow_pickle=True).tolist()
                    project.nodes_data = NodeData(
                        ids=node_ids,
                        names=node_names,
                        attributes={int(k): v for k, v in metadata["nodes"]["attributes"].items()},
                    )

                # Load links if present
                if (temp_path / "arrays/link_start_ids.npy").exists():
                    project.links_data = LinkData(
                        start_ids=np.load(temp_path / "arrays/link_start_ids.npy"),
                        end_ids=np.load(temp_path / "arrays/link_end_ids.npy"),
                        colors=np.load(temp_path / "arrays/link_colors.npy"),
                    )

                # Load layouts
                for layout_name in metadata["layouts"]:
                    layout_dir = temp_path / f"arrays/layout_{layout_name}"
                    project.layouts_data[layout_name] = LayoutData(
                        node_ids=np.load(layout_dir / "node_ids.npy"),
                        positions=np.load(layout_dir / "positions.npy"),
                        colors=np.load(layout_dir / "colors.npy"),
                    )

                # Load selections
                if "selections" in metadata:
                    project.selections = [Selection.model_validate(s) for s in metadata["selections"]]

                return project

        except Exception as e:
            logger.exception("Failed to load project from binary format", error=str(e))
            raise

    def get_layout_positions(self, layout_name: str = "default") -> npt.NDArray[np.float32]:
        """Get node positions for a specific layout"""
        if layout_name not in self.layouts_data:
            raise LayoutNotFoundError(layout_name)
        return self.layouts_data[layout_name].positions

    def get_layout_colors(self, layout_name: str = "default") -> npt.NDArray[np.uint8]:
        """Get node colors for a specific layout"""
        if layout_name not in self.layouts_data:
            raise LayoutNotFoundError(layout_name)
        return self.layouts_data[layout_name].colors
