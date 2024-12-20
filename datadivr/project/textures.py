import os
from typing import Optional

import numpy as np
from PIL import Image

from datadivr.utils.logging import get_logger

logger = get_logger(__name__)


def create_textures_from_project(
    project_name: str, layouts_data: dict, links_data: Optional[dict], output_dir: str = "static/projects/"
) -> None:
    """Create RGB textures from a Project instance and save them to a specified directory."""
    project_output_dir = os.path.join(output_dir, project_name, "textures")
    os.makedirs(project_output_dir, exist_ok=True)
    logger.debug(f"Created directory {project_output_dir} for project textures.")

    # Iterate over each layout in the project
    for layout_name, layout_data in layouts_data.items():
        make_layout_tex(
            project_name,
            layout_name,
            layout_data.node_ids,
            layout_data.positions,
            layout_data.colors,
            project_output_dir,
        )

    # Create link textures
    if links_data:
        make_link_tex(
            project_name,
            links_data["start_ids"],
            links_data["end_ids"],
            links_data["colors"],
            project_output_dir,
        )


def make_layout_tex(
    project_name: str,
    layout_name: str,
    node_ids: np.ndarray,
    node_positions: np.ndarray,
    node_colors: np.ndarray,
    output_dir: str,
) -> None:
    width = 128
    height = (len(node_positions) + width - 1) // width
    size = width * height

    padded_high = np.zeros((size, 3), dtype=np.uint8)
    padded_low = np.zeros((size, 3), dtype=np.uint8)
    padded_color = np.zeros((size, 4), dtype=np.uint8)

    pos = (node_positions * 65280).astype(int)
    padded_high[: len(node_positions)] = pos // 255
    padded_low[: len(node_positions)] = pos % 255
    padded_color[: len(node_positions)] = node_colors

    img_high = Image.fromarray(padded_high.reshape((height, width, 3)), "RGB")
    img_low = Image.fromarray(padded_low.reshape((height, width, 3)), "RGB")
    img_color = Image.fromarray(padded_color.reshape((height, width, 4)), "RGBA")

    img_high_path = f"{output_dir}/layout_{layout_name}_XYZ.bmp"
    img_low_path = f"{output_dir}/layout_{layout_name}_XYZl.bmp"
    img_color_path = f"{output_dir}/layout_{layout_name}_RGB.png"

    for path in [img_high_path, img_low_path, img_color_path]:
        if os.path.exists(path):
            logger.warning(f"Overwriting existing file: {path}")

    img_high.save(img_high_path)
    img_low.save(img_low_path)
    img_color.save(img_color_path)

    logger.debug(f"Saved layout textures for {layout_name} in {output_dir}.")


def make_link_tex(
    project_name: str, start_ids: np.ndarray, end_ids: np.ndarray, link_colors: np.ndarray, output_dir: str
) -> None:
    num_links = len(start_ids)
    width = 1024
    height = (num_links * 2 + width - 1) // width
    size = width * height

    padded_link_data = np.zeros((size, 3), dtype=np.uint8)
    padded_color_data = np.zeros((size, 4), dtype=np.uint8)

    start_bytes = np.stack([start_ids % 256, (start_ids // 256) % 256, start_ids // (256 * 256)], axis=1)

    end_bytes = np.stack([end_ids % 256, (end_ids // 256) % 256, end_ids // (256 * 256)], axis=1)

    all_bytes = np.empty((num_links * 2, 3), dtype=np.uint8)
    all_bytes[::2] = start_bytes
    all_bytes[1::2] = end_bytes

    padded_link_data[: len(all_bytes)] = all_bytes
    padded_color_data[: len(link_colors)] = link_colors

    img_links = Image.fromarray(padded_link_data.reshape((height, width, 3)), "RGB")
    img_colors = Image.fromarray(padded_color_data.reshape((height, width, 4)), "RGBA")

    img_links_path = f"{output_dir}/links_XYZ.bmp"
    img_colors_path = f"{output_dir}/links_RGB.png"

    for path in [img_links_path, img_colors_path]:
        if os.path.exists(path):
            logger.warning(f"Overwriting existing file: {path}")

    img_links.save(img_links_path)
    img_colors.save(img_colors_path)

    logger.debug(f"Saved link textures in {output_dir}.")
