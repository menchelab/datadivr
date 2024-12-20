from datadivr.calc.sample_data import generate_cube_data
from datadivr.cli import start_server
from datadivr.project.model import Project
from datadivr.viz import visualize_project


def main() -> None:
    project = Project(name="Cube Example Project", attributes={"description": "A sample project showing a cube"})

    ids, coords, node_colors, links, link_colors, names = generate_cube_data()  # get cube example data

    # Add nodes with multiple attributes
    project.add_nodes_bulk(
        ids=ids,
        attributes={
            "name": names,
            # lets add another custom example attribute
            "avg_position": coords.mean(axis=1),  # Calculate average of x,y,z coordinates
        },
    )

    project.add_links_bulk(links[:, 0], links[:, 1], link_colors)
    project.add_layout_bulk("default", ids, coords, node_colors)
    project.create_textures()  # Create textures (bmp files)
    project.create_json_files()  # nodes and links
    project.create_project_summary()  # pfile
    visualize_project(project, "default")  # (optional) Show visualization preview
    start_server(port=8765, host="127.0.0.1")


if __name__ == "__main__":
    main()
