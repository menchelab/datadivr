import numpy as np
import pytest
from plotly.graph_objs import Figure

from datadivr.exceptions import LayoutNotFoundError
from datadivr.project.model import Project
from datadivr.viz.plotly import visualize_project


@pytest.fixture
def sample_project():
    """Create a sample project with test data"""
    project = Project(name="Test Viz Project")

    # Add nodes
    node_ids = np.array([1, 2, 3], dtype=np.int32)
    node_names = ["Node 1", "Node 2", "Node 3"]
    project.add_nodes_bulk(node_ids, node_names)

    # Add a layout with 3D positions and colors
    positions = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]], dtype=np.float32)

    colors = np.array([[255, 0, 0, 255], [0, 255, 0, 255], [0, 0, 255, 255]], dtype=np.uint8)

    project.add_layout_bulk("default", node_ids, positions, colors)

    # Add some links
    start_ids = np.array([0, 1], dtype=np.int32)
    end_ids = np.array([1, 2], dtype=np.int32)
    link_colors = np.array([[255, 0, 0, 128], [0, 255, 0, 128]], dtype=np.uint8)

    project.add_links_bulk(start_ids, end_ids, link_colors)

    return project


def test_visualize_project_invalid_layout(sample_project):
    """Test that visualize_project raises LayoutNotFoundError for invalid layout"""
    with pytest.raises(LayoutNotFoundError):
        visualize_project(sample_project, layout_name="nonexistent")


def test_visualize_project_basic(sample_project, monkeypatch):
    """Test basic visualization creation without actually showing the plot"""

    # Mock the show method to prevent actual display
    shown_figure = None

    def mock_show(self, config=None):
        nonlocal shown_figure
        shown_figure = self

    monkeypatch.setattr(Figure, "show", mock_show)

    # Call visualization function
    visualize_project(sample_project)

    # Verify figure was created
    assert shown_figure is not None

    # Check that we have the expected number of traces
    assert len(shown_figure.data) == 2  # One for nodes, one for links

    # Check node trace
    node_trace = shown_figure.data[0]
    assert node_trace.type == "scatter3d"
    assert node_trace.mode == "markers"
    assert len(node_trace.x) == 3  # Number of nodes
    assert len(node_trace.y) == 3
    assert len(node_trace.z) == 3

    # Check link trace
    link_trace = shown_figure.data[1]
    assert link_trace.type == "scatter3d"
    assert link_trace.mode == "lines"
    assert len(link_trace.x) == 6  # 2 links * 3 points each (start, end, None)
    assert len(link_trace.y) == 6
    assert len(link_trace.z) == 6


def test_visualize_project_no_links(sample_project, monkeypatch):
    """Test visualization with a project that has no links"""
    # Remove links from project
    sample_project.links_data = None

    # Mock the show method
    shown_figure = None

    def mock_show(self, config=None):
        nonlocal shown_figure
        shown_figure = self

    monkeypatch.setattr(Figure, "show", mock_show)

    # Call visualization function
    visualize_project(sample_project)

    # Verify figure was created with only node trace
    assert shown_figure is not None
    assert len(shown_figure.data) == 1  # Only nodes, no links


def test_visualize_project_zoom_scale(sample_project, monkeypatch):
    """Test that zoom_scale parameter correctly scales the positions"""
    # Mock the show method
    shown_figure = None

    def mock_show(self, config=None):
        nonlocal shown_figure
        shown_figure = self

    monkeypatch.setattr(Figure, "show", mock_show)

    # Test with custom zoom scale
    zoom_scale = 2000.0
    visualize_project(sample_project, zoom_scale=zoom_scale)

    # Verify positions are scaled
    node_trace = shown_figure.data[0]
    expected_positions = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]]) * zoom_scale

    np.testing.assert_array_almost_equal(node_trace.x, expected_positions[:, 0])
    np.testing.assert_array_almost_equal(node_trace.y, expected_positions[:, 1])
    np.testing.assert_array_almost_equal(node_trace.z, expected_positions[:, 2])
