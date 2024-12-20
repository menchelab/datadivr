import json
import os

from datadivr.utils.logging import get_logger

logger = get_logger(__name__)


def create_nodes_json(nodelist: list, node_names: list, project: str, prefix_path: str = "static/projects/") -> None:
    # Create a list of nodes with the required structure
    nodes = [{"id": int(idx), "n": name, "attrlist": []} for idx, name in zip(nodelist, node_names)]

    # Create the final structure
    data = {"nodes": nodes}

    # Define the file path
    file_path = os.path.join(prefix_path, project, "nodes.json")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the JSON data to the file
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    logger.info(f"Saved nodes to {file_path}")


def create_links_json(linklist: list, project: str, prefix_path: str = "static/projects/") -> None:
    # Create a list of links with the required structure
    links = [{"id": idx, "s": int(link[0]), "e": int(link[1])} for idx, link in enumerate(linklist)]

    # Create the final structure
    data = {"links": links}

    # Define the file path
    file_path = os.path.join(prefix_path, project, "links.json")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the JSON data to the file
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    logger.info(f"Saved links to {file_path}")
