import os
import time
from pathlib import Path

import psutil
import orjson  # Add orjson for faster loading
import numpy as np

from datadivr.project.model import Project
from datadivr.utils.logging import get_logger, setup_logging


def get_memory_usage() -> str:
    """Get current memory usage in a human-readable format"""
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    return f"{memory_mb:.1f} MB"

def get_human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def print_json_stats(data: dict) -> str:
    """Generate statistics about JSON data structure"""
    stats = []
    
    # Node statistics
    if "nodes" in data:
        nodes = data["nodes"]
        stats.extend([
            f"Nodes:",
            f"  - IDs: {len(nodes['ids']):,}",
            f"  - Names: {len(nodes['names']):,}",
            f"  - Attributes: {len(nodes['attributes']):,}"
        ])

    # Link statistics
    if "links" in data:
        links = data["links"]
        stats.extend([
            f"Links:",
            f"  - Start IDs: {len(links['start_ids']):,}",
            f"  - End IDs: {len(links['end_ids']):,}",
            f"  - Colors: {len(links['colors']):,}"
        ])

    # Layout statistics
    if "layouts" in data:
        layouts = data["layouts"]
        stats.append(f"Layouts ({len(layouts)}): ")
        for name, layout in layouts.items():
            stats.extend([
                f"  {name}:",
                f"    - Node IDs: {len(layout['node_ids']):,}",
                f"    - Positions: {len(layout['positions']):,}",
                f"    - Colors: {len(layout['colors']):,}"
            ])

    # Selection statistics if present
    if "selections" in data and data["selections"]:
        selections = data["selections"]
        stats.extend([
            f"Selections:",
            f"  - Count: {len(selections):,}"
        ])

    return "\n".join(stats)

def main() -> None:
    setup_logging(level="DEBUG")
    logger = get_logger(__name__)
    total_start = time.time()
    initial_memory = get_memory_usage()
    logger.debug(f"Starting with RAM usage: {initial_memory}")

    # Test both loading methods
    # 1. JSON format
    input_json = "example_project.json"
    json_size = os.path.getsize(input_json)
    logger.debug(f"Loading JSON project file ({get_human_readable_size(json_size)})")

    t_json_start = time.time()
    with open(input_json, "rb") as f:
        json_data = orjson.loads(f.read())
    t_json_parsed = time.time()
    
    logger.debug("JSON Structure Statistics:\n" + print_json_stats(json_data))
    json_project = Project.model_validate(json_data)
    t_json_end = time.time()

    # 2. Binary format
    input_binary = "example_project.npz"
    binary_size = os.path.getsize(input_binary)
    logger.debug(f"Loading binary project file ({get_human_readable_size(binary_size)})")

    t_binary_start = time.time()
    binary_project = Project.load_from_binary_file(input_binary)
    t_binary_end = time.time()

    # Calculate memory increases
    final_memory = float(get_memory_usage().split()[0])
    initial_memory_float = float(initial_memory.split()[0])
    memory_increase = final_memory - initial_memory_float

    # Compare results
    logger.info(
        f"Loading performance comparison:"
        f"\n  JSON format:"
        f"\n    - Parse time: {t_json_parsed - t_json_start:.2f}s"
        f"\n    - Model load time: {t_json_end - t_json_parsed:.2f}s"
        f"\n    - Total time: {t_json_end - t_json_start:.2f}s"
        f"\n    - File size: {get_human_readable_size(json_size)}"
        f"\n  Binary format:"
        f"\n    - Total time: {t_binary_end - t_binary_start:.2f}s"
        f"\n    - File size: {get_human_readable_size(binary_size)}"
        f"\n  Improvement:"
        f"\n    - Time: {(t_json_end - t_json_start) / (t_binary_end - t_binary_start):.1f}x"
        f"\n    - Size: {json_size / binary_size:.1f}x"
    )

    # Validate data integrity between formats
    if logger.level <= 10:  # DEBUG level
        logger.debug("Validating data integrity between formats...")
        
        # Compare node counts
        json_nodes = len(json_project.nodes_data.ids) if json_project.nodes_data else 0
        binary_nodes = len(binary_project.nodes_data.ids) if binary_project.nodes_data else 0
        logger.debug(f"Node count match: {json_nodes == binary_nodes} ({json_nodes:,} vs {binary_nodes:,})")

        # Compare link counts
        json_links = len(json_project.links_data.start_ids) if json_project.links_data else 0
        binary_links = len(binary_project.links_data.start_ids) if binary_project.links_data else 0
        logger.debug(f"Link count match: {json_links == binary_links} ({json_links:,} vs {binary_links:,})")

        # Compare layouts
        json_layouts = len(json_project.layouts_data)
        binary_layouts = len(binary_project.layouts_data)
        logger.debug(f"Layout count match: {json_layouts == binary_layouts} ({json_layouts} vs {binary_layouts})")

        # Check layout data consistency
        for name in json_project.layouts_data:
            if name in binary_project.layouts_data:
                json_layout = json_project.layouts_data[name]
                binary_layout = binary_project.layouts_data[name]
                logger.debug(
                    f"Layout '{name}' comparison:"
                    f"\n    - Node count match: {len(json_layout.node_ids) == len(binary_layout.node_ids)}"
                    f"\n    - Position shape match: {json_layout.positions.shape == binary_layout.positions.shape}"
                    f"\n    - Color shape match: {json_layout.colors.shape == binary_layout.colors.shape}"
                )

    total_time = time.time() - total_start
    logger.info(
        f"Total execution time: {total_time:.2f}s"
        f"\nFinal RAM: {get_memory_usage()}"
        f"\nPeak memory increase: {memory_increase:.1f} MB"
    )

if __name__ == "__main__":
    main()
