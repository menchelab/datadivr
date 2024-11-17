import os
import time

from datadivr.calc import create_sample_data
from datadivr.project.model import Project
from datadivr.utils.logging import get_logger, setup_logging
from datadivr.viz import visualize_project

logger = get_logger(__name__)


def main() -> None:
    setup_logging(level="DEBUG")
    logger.debug("Starting project creation")

    # Create project
    t0 = time.perf_counter()
    project = Project(name="Large Example Project", attributes={"description": "A sample project with 1M nodes"})
    logger.debug(f"Project creation took {time.perf_counter() - t0:.2f}s")

    # Add data to project with specific sizes
    t0 = time.perf_counter()
    n_nodes = 100  # 1M nodes
    n_links = 5_000  # 5M links
    n_layouts = 1
    data = create_sample_data(n_nodes=n_nodes, n_links=n_links, n_layouts=n_layouts)
    logger.debug(f"Data generation took {time.perf_counter() - t0:.2f}s")

    # Add data to project
    t0 = time.perf_counter()
    project.add_nodes_bulk(*data[:3])
    project.add_links_bulk(*data[5:])
    logger.debug(f"Adding bulk data took {time.perf_counter() - t0:.2f}s")

    # Add layouts
    t0 = time.perf_counter()
    layout_names = ["default"]
    for name, positions, colors in zip(layout_names, data[3], data[4]):
        project.add_layout_bulk(name, data[0], positions, colors)
    logger.debug(f"Adding layouts took {time.perf_counter() - t0:.2f}s")

    # Test both saving methods
    # 1. JSON format
    t0 = time.perf_counter()
    project.save_to_json_file("tmp/example_project.json")
    json_time = time.perf_counter() - t0
    json_size = os.path.getsize("tmp/example_project.json")

    # 2. Binary format
    t0 = time.perf_counter()
    project.save_to_binary_file("tmp/example_project.npz")
    binary_time = time.perf_counter() - t0
    binary_size = os.path.getsize("tmp/example_project.npz")

    # Compare results
    logger.info(
        f"Saving performance comparison:"
        f"\n  JSON format: {json_time:.2f}s, {json_size / 1024 / 1024:.1f} MB"
        f"\n  Binary format: {binary_time:.2f}s, {binary_size / 1024 / 1024:.1f} MB"
        f"\n  Size ratio: {json_size / binary_size:.1f}x"
    )

    # Test loading performance
    t0 = time.perf_counter()
    Project.load_from_json_file("tmp/example_project.json")
    json_load_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    Project.load_from_binary_file("tmp/example_project.npz")
    binary_load_time = time.perf_counter() - t0

    logger.info(
        f"Loading performance comparison:"
        f"\n  JSON format: {json_load_time:.2f}s"
        f"\n  Binary format: {binary_load_time:.2f}s"
        f"\n  Speed ratio: {json_load_time / binary_load_time:.1f}x"
    )

    # show visualization
    logger.info("Creating visualization...")
    visualize_project(project)
    logger.info("Ciao!")


if __name__ == "__main__":
    main()
