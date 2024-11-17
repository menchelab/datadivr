from pathlib import Path

from datadivr.project.model import (
    Layout,
    LayoutNodePosition,
    Link,
    Node,
    Project,
    Selection,
    SelectionNodes,
)
from datadivr.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)

def main() -> None:
    setup_logging()

    # Create a sample project
    project = Project(
        name="Example Project",
        attributes={"description": "A sample project"},
        nodes=[
            Node(id=1, name="Node 1", attributes={"type": "source"}),
            Node(id=2, name="Node 2", attributes={"type": "target"}),
        ],
        links=[
            Link(start=1, end=2, linkcolor=(255, 0, 0, 255)),
        ],
        layouts=[
            Layout(
                name="Default Layout",
                node_positions=[
                    LayoutNodePosition(
                        node_id=1,
                        x=2.0,
                        y=3.0,
                        z=5.0,
                        nodecolor=(0, 255, 0, 255),
                    ),
                    LayoutNodePosition(
                        node_id=2,
                        x=1.0,
                        y=1.0,
                        z=0.0,
                        nodecolor=(0, 0, 255, 255),
                    ),
                ],
            )
        ],
        selections=[
            Selection(
                name="Selection 1",
                label_color=(255, 255, 0, 255),
                nodes=SelectionNodes(
                    node_ids=[1, 2],
                    create_clusternode=False,
                ),
            )
        ],
    )

    # Save the project using the new method name
    project.save_to_json_file("example_project.json")
    logger.info("Created and saved example project")

if __name__ == "__main__":
    main()
