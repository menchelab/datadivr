import numpy as np

from datadivr.project.model import Project
from datadivr.viz import visualize_project


def generate_cube_data():
    # Create node IDs first
    node_ids = np.arange(8, dtype=np.int32)  # Creates [0, 1, 2, 3, 4, 5, 6, 7]

    # Create 8 corners of a cube in 3D space
    cube_coords = np.array(
        [
            [0.1, 0.1, 0.1],  # 0: front bottom left
            [0.9, 0.1, 0.1],  # 1: front bottom right
            [0.1, 0.9, 0.1],  # 2: front top left
            [0.9, 0.9, 0.1],  # 3: front top right
            [0.1, 0.1, 0.9],  # 4: back bottom left
            [0.9, 0.1, 0.9],  # 5: back bottom right
            [0.1, 0.9, 0.9],  # 6: back top left
            [0.9, 0.9, 0.9],  # 7: back top right
        ],
        dtype=np.float32,
    )

    # Generate colors for nodes
    nodecol = np.column_stack([
        np.full(len(cube_coords), 255),  # Red channel
        (cube_coords[:, 2] * 255).astype(int),  # Green varies with z
        (cube_coords[:, 1] * 255).astype(int),  # Blue varies with y
        np.full(len(cube_coords), 255),  # Alpha channel
    ]).astype(np.uint8)

    # Define the links (edges of the cube)
    linklist = np.array(
        [
            [0, 1],
            [1, 3],
            [3, 2],
            [2, 0],  # Front face
            [4, 5],
            [5, 7],
            [7, 6],
            [6, 4],  # Back face
            [0, 4],
            [1, 5],
            [2, 6],
            [3, 7],  # Connecting edges
        ],
        dtype=np.int32,
    )

    # Generate colors for links
    linkcol = np.column_stack([
        np.random.randint(128, 256, len(linklist)),  # Red
        np.random.randint(128, 256, len(linklist)),  # Green
        np.random.randint(128, 256, len(linklist)),  # Blue
        np.full(len(linklist), 255),  # Alpha
    ]).astype(np.uint8)

    # Node attributes
    names = np.array([
        "front bottom left",
        "front bottom right",
        "front top left",
        "front top right",
        "back bottom left",
        "back bottom right",
        "back top left",
        "back top right",
    ])

    return node_ids, cube_coords, nodecol, linklist, linkcol, names


def main() -> None:
    project = Project(name="Cube Example Project", attributes={"description": "A sample project showing a cube"})

    # Generate cube data
    ids, coords, node_colors, links, link_colors, names = generate_cube_data()

    # Add nodes with multiple attributes
    project.add_nodes_bulk(
        ids=ids,
        attributes={
            "name": names,
            # lets add another example attribute
            "avg_position": coords.mean(axis=1),  # Calculate average of x,y,z coordinates
        },
    )

    # Add links
    project.add_links_bulk(links[:, 0], links[:, 1], link_colors)

    # Add layout
    project.add_layout_bulk("default", ids, coords, node_colors)

    # Save project
    project.save_to_json_file("tmp/cube_project.json")
    project.save_to_binary_file("tmp/cube_project.npz")

    # Show visualization
    visualize_project(project, "default")


if __name__ == "__main__":
    main()
