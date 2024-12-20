from datadivr.calc.sample_data import generate_cube_project
from datadivr.cli import start_server
from datadivr.viz import visualize_project


def main() -> None:
    project = generate_cube_project()
    project.create_all_assets()  # textures, node/links json, projectfile

    visualize_project(project, "default")  # (optional) Show visualization preview
    start_server(port=8765, host="127.0.0.1")


if __name__ == "__main__":
    main()
