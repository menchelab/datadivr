import os

import numpy as np
import pytest

from datadivr.calc.sample_data import generate_cube_data
from datadivr.project.model import Project


@pytest.fixture
def sample_project():
    """Create a sample project with cube data."""
    project = Project(name="Test Project", attributes={"description": "Test project with cube data"})

    # Generate cube data
    node_ids, cube_coords, node_colors, linklist, link_colors, names = generate_cube_data()

    # Add nodes with attributes
    project.add_nodes_bulk(
        ids=node_ids,
        attributes={
            "name": names,
            "avg_position": cube_coords.mean(axis=1),  # Calculate average of x,y,z coordinates
        },
    )

    # Add links
    project.add_links_bulk(linklist[:, 0], linklist[:, 1], link_colors)

    # Add layout
    project.add_layout_bulk("default", node_ids, cube_coords, node_colors)

    return project


def test_project_creation():
    """Test basic project creation."""
    project = Project(name="Test Project", attributes={"description": "Test description"})
    assert project.name == "Test Project"
    assert project.attributes["description"] == "Test description"


def test_data_addition(sample_project):
    """Test that data was properly added to the project."""
    assert sample_project.nodes_data is not None
    assert sample_project.links_data is not None
    assert "default" in sample_project.layouts_data


def test_save_load_json(sample_project, tmp_path):
    """Test saving and loading project in JSON format."""
    # Save
    json_path = tmp_path / "test_project.json"
    sample_project.save_to_json_file(json_path)
    assert os.path.exists(json_path)

    # Load
    loaded_project = Project.load_from_json_file(json_path)

    # Verify
    assert loaded_project.name == sample_project.name
    assert loaded_project.attributes == sample_project.attributes
    assert len(loaded_project.nodes_data.ids) == len(sample_project.nodes_data.ids)
    assert len(loaded_project.links_data.start_ids) == len(sample_project.links_data.start_ids)
    assert loaded_project.layouts_data.keys() == sample_project.layouts_data.keys()


def test_save_load_binary(sample_project, tmp_path):
    """Test saving and loading project in binary format."""
    # Save
    binary_path = tmp_path / "test_project.npz"
    sample_project.save_to_binary_file(binary_path)
    assert os.path.exists(binary_path)

    # Load
    loaded_project = Project.load_from_binary_file(binary_path)

    # Verify
    assert loaded_project.name == sample_project.name
    assert loaded_project.attributes == sample_project.attributes
    assert len(loaded_project.nodes_data.ids) == len(sample_project.nodes_data.ids)
    assert len(loaded_project.links_data.start_ids) == len(sample_project.links_data.start_ids)
    assert loaded_project.layouts_data.keys() == sample_project.layouts_data.keys()


def test_file_sizes(sample_project, tmp_path):
    """Test that binary format is more compact than JSON."""
    json_path = tmp_path / "test_project.json"
    binary_path = tmp_path / "test_project.npz"

    sample_project.save_to_json_file(json_path)
    sample_project.save_to_binary_file(binary_path)

    json_size = os.path.getsize(json_path)
    binary_size = os.path.getsize(binary_path)

    assert binary_size < json_size  # Binary should be more compact


def test_multiple_save_load_formats(sample_project, tmp_path):
    """Test data consistency when saving/loading across different formats."""
    # First save to binary
    binary_path = tmp_path / "test_project.npz"
    sample_project.save_to_binary_file(binary_path)

    # Load from binary
    binary_loaded = Project.load_from_binary_file(binary_path)

    # Save to JSON
    json_path = tmp_path / "test_project.json"
    binary_loaded.save_to_json_file(json_path)

    # Load from JSON
    final_project = Project.load_from_json_file(json_path)

    # Verify all data remained consistent through the conversions
    assert final_project.name == sample_project.name
    assert final_project.attributes == sample_project.attributes

    # Check nodes data
    assert np.array_equal(final_project.nodes_data.ids, sample_project.nodes_data.ids)
    assert (
        final_project.nodes_data.get_attribute("name").tolist()
        == sample_project.nodes_data.get_attribute("name").tolist()
    )
    assert np.array_equal(
        final_project.nodes_data.get_attribute("avg_position"), sample_project.nodes_data.get_attribute("avg_position")
    )

    # Check links data
    assert np.array_equal(final_project.links_data.start_ids, sample_project.links_data.start_ids)
    assert np.array_equal(final_project.links_data.end_ids, sample_project.links_data.end_ids)
    assert np.array_equal(final_project.links_data.colors, sample_project.links_data.colors)

    # Check layouts data
    assert final_project.layouts_data.keys() == sample_project.layouts_data.keys()
    for layout_name in sample_project.layouts_data:
        original_layout = sample_project.layouts_data[layout_name]
        final_layout = final_project.layouts_data[layout_name]

        assert np.array_equal(final_layout.node_ids, original_layout.node_ids)
        assert np.array_equal(final_layout.positions, original_layout.positions)
        assert np.array_equal(final_layout.colors, original_layout.colors)
