import os
import time

from datadivr.calc import get_memory_usage
from datadivr.project.model import Project
from datadivr.utils.logging import get_logger, setup_logging


def get_human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human readable string"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def main() -> None:
    setup_logging(level="DEBUG")
    logger = get_logger(__name__)
    total_start = time.time()
    initial_memory = get_memory_usage()
    logger.debug(f"Starting with RAM usage: {initial_memory}")

    # Test both loading methods
    # 1. JSON format
    input_json = "tmp/example_project.json"
    json_size = os.path.getsize(input_json)
    logger.debug(f"Loading JSON project file ({get_human_readable_size(json_size)})")

    t_json_start = time.time()
    _ = Project.load_from_json_file(input_json)
    t_json_end = time.time()

    # 2. Binary format
    input_binary = "tmp/example_project.npz"
    binary_size = os.path.getsize(input_binary)
    logger.debug(f"Loading binary project file ({get_human_readable_size(binary_size)})")

    t_binary_start = time.time()
    _ = Project.load_from_binary_file(input_binary)
    t_binary_end = time.time()

    # Calculate memory increases
    final_memory = float(get_memory_usage().split()[0])
    initial_memory_float = float(initial_memory.split()[0])
    memory_increase = final_memory - initial_memory_float

    # Compare results
    logger.info(
        f"Loading performance comparison:"
        f"\n  JSON format:"
        f"\n    - Total time: {t_json_end - t_json_start:.2f}s"
        f"\n    - File size: {get_human_readable_size(json_size)}"
        f"\n  Binary format:"
        f"\n    - Total time: {t_binary_end - t_binary_start:.2f}s"
        f"\n    - File size: {get_human_readable_size(binary_size)}"
        f"\n  Improvement:"
        f"\n    - Time: {(t_json_end - t_json_start) / (t_binary_end - t_binary_start):.1f}x"
        f"\n    - Size: {json_size / binary_size:.1f}x"
    )

    total_time = time.time() - total_start
    logger.info(
        f"Total execution time: {total_time:.2f}s"
        f"\nFinal RAM: {get_memory_usage()}"
        f"\nPeak memory increase: {memory_increase:.1f} MB"
    )


if __name__ == "__main__":
    main()
