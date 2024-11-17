"""Plotly-based visualization for DataDiVR projects."""

import numpy as np
import plotly.graph_objects as go

from datadivr.exceptions import LayoutNotFoundError
from datadivr.project.model import Project
from datadivr.utils.logging import get_logger

logger = get_logger(__name__)


def visualize_project(project: Project, layout_name: str = "default", zoom_scale: float = 1000.0) -> None:
    """Create an interactive 3D visualization of the project using Plotly with WebGL.

    Args:
        project: The Project instance to visualize
        layout_name: Name of the layout to use (default: "default")
        zoom_scale: Scale factor for extreme zoom capabilities (default: 1000.0)

    Raises:
        LayoutNotFoundError: If the specified layout doesn't exist
    """
    # Verify layout exists
    if layout_name not in project.layouts_data:
        raise LayoutNotFoundError(layout_name=layout_name, available_layouts=list(project.layouts_data.keys()))

    # Get the layout data
    positions = project.get_layout_positions(layout_name) * zoom_scale
    colors = project.get_layout_colors(layout_name)
    node_ids = project.layouts_data[layout_name].node_ids

    # Convert RGBA colors to hex strings for plotly
    node_colors = [f"rgb({c[0]},{c[1]},{c[2]})" for c in colors]

    # Calculate incoming and outgoing links for each node
    incoming_links = np.zeros(len(node_ids), dtype=int)
    outgoing_links = np.zeros(len(node_ids), dtype=int)

    if project.links_data is not None:
        incoming_links = np.bincount(project.links_data.end_ids, minlength=len(node_ids))
        outgoing_links = np.bincount(project.links_data.start_ids, minlength=len(node_ids))

    # Create hover text
    hover_text = [
        f"Node ID: {node_id}<br>"
        f"X: {pos[0] / zoom_scale:.2f}<br>"
        f"Y: {pos[1] / zoom_scale:.2f}<br>"
        f"Z: {pos[2] / zoom_scale:.2f}<br>"
        f"Incoming Links: {incoming_links[i]}<br>"
        f"Outgoing Links: {outgoing_links[i]}"
        for i, (node_id, pos) in enumerate(zip(node_ids, positions))
    ]

    # Create figure
    fig = go.Figure()

    # Create node trace
    node_trace = go.Scatter3d(
        x=positions[:, 0],
        y=positions[:, 1],
        z=positions[:, 2],
        mode="markers",
        marker={
            "size": 8.0,
            "color": node_colors,
            "line": {"width": 0},
            "opacity": 0.5,
            "sizemode": "diameter",
        },
        text=hover_text,
        hoverinfo="text",
        hoverlabel={"bgcolor": "rgba(0,0,0,0.8)", "font": {"size": 12}, "align": "left"},
        name="Nodes",
        customdata=node_ids,
        visible=True,
    )

    fig.add_trace(node_trace)

    # Add links if they exist
    if project.links_data is not None:
        x_lines = np.empty(len(project.links_data.start_ids) * 3)
        y_lines = np.empty(len(project.links_data.start_ids) * 3)
        z_lines = np.empty(len(project.links_data.start_ids) * 3)

        start_positions = positions[project.links_data.start_ids]
        end_positions = positions[project.links_data.end_ids]

        x_lines[::3] = start_positions[:, 0]
        x_lines[1::3] = end_positions[:, 0]
        x_lines[2::3] = None

        y_lines[::3] = start_positions[:, 1]
        y_lines[1::3] = end_positions[:, 1]
        y_lines[2::3] = None

        z_lines[::3] = start_positions[:, 2]
        z_lines[1::3] = end_positions[:, 2]
        z_lines[2::3] = None

        link_colors = [f"rgba({c[0]},{c[1]},{c[2]},{c[3] / 455})" for c in project.links_data.colors]

        fig.add_trace(
            go.Scatter3d(
                x=x_lines,
                y=y_lines,
                z=z_lines,
                mode="lines",
                line={
                    "color": link_colors,
                    "width": 1,
                },
                name="Links",
                hoverinfo="none",
            )
        )

    # Update layout settings
    fig.update_layout(
        scene={
            "aspectmode": "data",
            "camera": {
                "up": {"x": 0, "y": 0, "z": 1},
                "center": {"x": 0, "y": 0, "z": 0},
                "eye": {"x": 1.5, "y": 1.5, "z": 1.5},
            },
            "xaxis": {
                "showspikes": False,
                "range": None,
                "autorange": True,
            },
            "yaxis": {
                "showspikes": False,
                "range": None,
                "autorange": True,
            },
            "zaxis": {
                "showspikes": False,
                "range": None,
                "autorange": True,
            },
            "dragmode": "orbit",
        },
        showlegend=False,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        template="plotly_dark",
        uirevision=True,
    )

    # Configure for better interaction
    config = {
        "scrollZoom": True,
        "displayModeBar": True,
        "responsive": False,
        "modeBarButtonsToRemove": ["resetCameraDefault", "resetCameraLastSave", "hoverClosest3d"],
        "modeBarButtonsToAdd": ["resetCamera"],
        "doubleClick": "reset+autosize",
    }

    # Show the figure
    fig.show(config=config)
