from datadivr.calc import create_sample_data
from datadivr.project.model import Project
from datadivr.viz import visualize_project


def main() -> None:
    project = Project(name="Large Example Project", attributes={"description": "A sample project with 1M nodes"})

    # Add data to project
    data = create_sample_data(100, 500, 2)

    project.add_nodes_bulk(*data[:3])
    project.add_links_bulk(*data[5:])

    # Add layouts
    layout_names = ["default", "alternate1"]
    for name, positions, colors in zip(layout_names, data[3], data[4]):
        project.add_layout_bulk(name, data[0], positions, colors)

    # Test both saving methods
    project.save_to_json_file("tmp/example_project.json")
    project.save_to_binary_file("tmp/example_project.npz")

    # show visualization
    visualize_project(project, "alternate1")


if __name__ == "__main__":
    main()
