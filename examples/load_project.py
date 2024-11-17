from pathlib import Path

from datadivr.project.model import Project
from datadivr.utils.logging import get_logger, setup_logging


def main() -> None:
    setup_logging(level="DEBUG")
    logger = get_logger(__name__)

    # Load the project using the new method name
    project = Project.load_from_json_file("example_project.json")

    logger.info(
        "Project loaded",
        project_name=project.name,
        node_count=len(project.nodes),
        link_count=len(project.links),
    )

    # Example of accessing project data
    for node in project.nodes:
        logger.debug("Node found", node_id=node.id, node_name=node.name)

if __name__ == "__main__":
    main()
