import time
import os
import psutil

import numpy as np

from datadivr.project.model import Project
from datadivr.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)

def get_memory_usage() -> str:
    """Get current memory usage in a human-readable format"""
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    return f"{memory_mb:.1f} MB"

def create_sample_data(n_nodes: int = 500_000, n_links: int = 1_000_000) -> tuple:
    """Create sample data with timing and memory information"""
    t_start = time.time()
    initial_memory = get_memory_usage()
    logger.debug(f"Initial memory usage: {initial_memory}")


    # Create node data
    node_ids = np.arange(n_nodes, dtype=np.int32)
    node_names = [f"Node_{i}" for i in node_ids]
    # Create sparse attributes (only 10% of nodes have attributes)
    attributes = {
        i: {"type": "special"} 
        for i in np.random.choice(node_ids, size=n_nodes//10, replace=False)
    }

    t_nodes = time.time()
    logger.debug(f"Created {n_nodes} nodes in {t_nodes - t_start:.2f}s (RAM: {get_memory_usage()})")

    # Create 5 different layout datasets
    layouts = []
    layout_colors = []
    for _ in range(5):
        positions = np.random.rand(n_nodes, 3).astype(np.float32) * 100  # Scale for visibility
        colors = np.random.randint(0, 255, (n_nodes, 4), dtype=np.uint8)
        colors[:, 3] = 255  # Set alpha to fully opaque
        layouts.append(positions)
        layout_colors.append(colors)

    t_layout = time.time()
    logger.debug(f"Created 5 layout datasets in {t_layout - t_nodes:.2f}s (RAM: {get_memory_usage()})")

    # Create link data
    start_ids = np.random.randint(0, n_nodes, n_links, dtype=np.int32)
    end_ids = np.random.randint(0, n_nodes, n_links, dtype=np.int32)
    link_colors = np.full((n_links, 4), [255, 0, 0, 255], dtype=np.uint8)  # Red links

    t_links = time.time()
    logger.debug(f"Created {n_links} links in {t_links - t_layout:.2f}s (RAM: {get_memory_usage()})")

    return (node_ids, node_names, attributes, layouts, layout_colors, 
            start_ids, end_ids, link_colors)

def main() -> None:
    setup_logging(level="DEBUG")
    total_start = time.time()
    logger.debug(f"Starting with RAM usage: {get_memory_usage()}")

    # Create sample data
    data = create_sample_data()
    
    # Create project
    project = Project(
        name="Large Example Project",
        attributes={"description": "A sample project with 1M nodes"}
    )

    # Add data to project
    t_project_start = time.time()
    project.add_nodes_bulk(*data[:3])
    project.add_links_bulk(*data[5:])
    
    # Add layouts
    layout_names = ["default", "alternate1", "alternate2", "alternate3", "alternate4"]
    for name, positions, colors in zip(layout_names, data[3], data[4]):
        project.add_layout_bulk(name, data[0], positions, colors)

    # Test both saving methods
    # 1. JSON format
    t_json_start = time.time()
    project.save_to_json_file("example_project.json")
    t_json_end = time.time()
    json_size = os.path.getsize("example_project.json")

    # 2. Binary format
    t_binary_start = time.time()
    project.save_to_binary_file("example_project.npz")
    t_binary_end = time.time()
    binary_size = os.path.getsize("example_project.npz")

    # Compare results
    logger.info(
        f"Saving performance comparison:"
        f"\n  JSON format:"
        f"\n    - Time: {t_json_end - t_json_start:.2f}s"
        f"\n    - Size: {json_size / 1024 / 1024:.1f} MB"
        f"\n  Binary format:"
        f"\n    - Time: {t_binary_end - t_binary_start:.2f}s"
        f"\n    - Size: {binary_size / 1024 / 1024:.1f} MB"
        f"\n  Improvement:"
        f"\n    - Time: {(t_json_end - t_json_start) / (t_binary_end - t_binary_start):.1f}x"
        f"\n    - Size: {json_size / binary_size:.1f}x"
    )

if __name__ == "__main__":
    main()
