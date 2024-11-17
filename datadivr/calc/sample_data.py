"""Sample data generation utilities for DataDiVR."""

import time

import numpy as np

from datadivr.utils.logging import get_logger

logger = get_logger(__name__)


def create_sample_data(n_nodes: int = 5_000, n_links: int = 50_000, n_layouts: int = 5) -> tuple:
    """Create sample data with timing information.

    Args:
        n_nodes: Number of nodes to generate
        n_links: Number of links to generate
        n_layouts: Number of layout datasets to generate

    Returns:
        tuple: Contains (node_ids, node_names, attributes, layouts, layout_colors,
               start_ids, end_ids, link_colors)
    """
    t_start = time.time()

    # Create node data
    node_ids = np.arange(n_nodes, dtype=np.int32)
    node_names = [f"Node_{i}" for i in node_ids]
    # Create sparse attributes (only 10% of nodes have attributes)
    attributes = {i: {"type": "special"} for i in np.random.choice(node_ids, size=n_nodes // 10, replace=False)}

    t_nodes = time.time()
    logger.debug(f"Created {n_nodes} nodes in {t_nodes - t_start:.2f}s")

    # Create n_layouts different layout datasets
    layouts = []
    layout_colors = []
    for _ in range(n_layouts):
        positions = np.random.rand(n_nodes, 3).astype(np.float32) * 100  # Scale for visibility
        colors = np.random.randint(0, 255, (n_nodes, 4), dtype=np.uint8)
        colors[:, 3] = 120  # Set alpha to fully opaque
        layouts.append(positions)
        layout_colors.append(colors)

    t_layout = time.time()
    logger.debug(f"Created {n_layouts} layout datasets in {t_layout - t_nodes:.2f}s")

    # Create link data with random colors and 50% transparency
    start_ids = np.random.randint(0, n_nodes, n_links, dtype=np.int32)
    end_ids = np.random.randint(0, n_nodes, n_links, dtype=np.int32)
    # Random RGB colors with 50% transparency (alpha=128)
    link_colors = np.random.randint(0, 255, (n_links, 4), dtype=np.uint8)
    link_colors[:, 3] = 128  # Set alpha to 128 (50% transparency)

    t_links = time.time()
    logger.debug(f"Created {n_links} links in {t_links - t_layout:.2f}s")

    return (node_ids, node_names, attributes, layouts, layout_colors, start_ids, end_ids, link_colors)
