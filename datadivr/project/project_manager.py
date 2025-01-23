from datadivr.project.model import Project


class ProjectManager:
    _instance: Project | None = None

    @classmethod
    def get_current_project(cls) -> Project | None:
        """Get the current project instance."""
        return cls._instance

    @classmethod
    def set_current_project(cls, project: Project) -> None:
        """Set the current project instance."""
        cls._instance = project

    @classmethod
    def clear_current_project(cls) -> None:
        """Clear the current project instance."""
        cls._instance = None
