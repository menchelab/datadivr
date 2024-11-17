import numpy as np
import pytest

from datadivr.project.model import LayoutNotFoundError, Project


@pytest.fixture
def sample_project():
    """Create a sample project with some test data"""
    project = Project(name="Test Project")

    # Add nodes
    node_ids = np.array([1, 2, 3], dtype=np.int32)
    node_names = ["Node 1", "Node 2", "Node 3"]
    node_attributes = {1: {"type": "A"}, 2: {"type": "B"}}
    project.add_nodes_bulk(node_ids, node_names, node_attributes)

    # Add links
    start_ids = np.array([1, 2], dtype=np.int32)
    end_ids = np.array([2, 3], dtype=np.int32)
    link_colors = np.array([[255, 0, 0, 255], [0, 255, 0, 255]], dtype=np.uint8)
    project.add_links_bulk(start_ids, end_ids, link_colors)

    # Add a layout
    layout_positions = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]], dtype=np.float32)
    layout_colors = np.array([[255, 0, 0, 255], [0, 255, 0, 255], [0, 0, 255, 255]], dtype=np.uint8)
    project.add_layout_bulk("default", node_ids, layout_positions, layout_colors)

    return project


def test_project_initialization():
    project = Project(name="Test")
    assert project.name == "Test"
    assert project.attributes == {}
    assert project.nodes_data is None
    assert project.links_data is None
    assert project.layouts_data == {}
    assert project.selections == []


def test_add_nodes_bulk(sample_project):
    assert len(sample_project.nodes_data.ids) == 3
    assert sample_project.nodes_data.names == ["Node 1", "Node 2", "Node 3"]
    assert sample_project.nodes_data.attributes[1]["type"] == "A"


def test_add_links_bulk(sample_project):
    assert len(sample_project.links_data.start_ids) == 2
    assert len(sample_project.links_data.end_ids) == 2
    np.testing.assert_array_equal(sample_project.links_data.colors[0], [255, 0, 0, 255])


def test_add_layout_bulk(sample_project):
    layout = sample_project.layouts_data["default"]
    assert len(layout.node_ids) == 3
    np.testing.assert_array_equal(layout.positions[0], [0, 0, 0])
    np.testing.assert_array_equal(layout.colors[0], [255, 0, 0, 255])


def test_get_layout_positions(sample_project):
    positions = sample_project.get_layout_positions("default")
    np.testing.assert_array_equal(positions[0], [0, 0, 0])

    with pytest.raises(LayoutNotFoundError):
        sample_project.get_layout_positions("nonexistent")


def test_save_and_load_json(sample_project, tmp_path):
    # Test JSON serialization
    json_path = tmp_path / "test_project.json"
    sample_project.save_to_json_file(json_path)

    loaded_project = Project.load_from_json_file(json_path)
    assert loaded_project.name == sample_project.name
    np.testing.assert_array_equal(loaded_project.nodes_data.ids, sample_project.nodes_data.ids)
    assert loaded_project.nodes_data.names == sample_project.nodes_data.names


def test_save_and_load_binary(sample_project, tmp_path):
    # Test binary serialization
    binary_path = tmp_path / "test_project.bin"
    sample_project.save_to_binary_file(binary_path)

    loaded_project = Project.load_from_binary_file(binary_path)
    assert loaded_project.name == sample_project.name
    np.testing.assert_array_equal(loaded_project.nodes_data.ids, sample_project.nodes_data.ids)
    assert loaded_project.nodes_data.names == sample_project.nodes_data.names
