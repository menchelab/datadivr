from typing import Optional

from datadivr.project.model import Project


class ProjectManager:
    _instance: Optional[Project] = None

    @classmethod
    def get_current_project(cls) -> Optional[Project]:
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
