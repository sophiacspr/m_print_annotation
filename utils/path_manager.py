import json
import os


class PathManager:
    """
    Resolves and manages project-specific file paths centrally.

    Loads path templates from app_paths.json and expands <project> placeholders
    using the active project name. Paths can be recomputed when switching projects.
    """

    def __init__(self) -> None:
        """
        Initializes the path manager by resolving the current project name
        and building the expanded path mapping.
        """
        self._app_paths_file = os.path.normpath(
            "app_data/app/config/app_paths.json"
        )

        # Initial load without project context to be able to read project-independent
        # files before a project is selected.
        self._paths: dict[str, str] = self._load_project_independent_paths()

    def get_last_project_name(self) -> str:
        """
        Resolves the project name from config or falls back to first existing directory.

        Returns:
            str: The name of the last project.

        Raises:
            FileNotFoundError: If the project root directory is missing.
            RuntimeError: If no projects are available.
        """
        with open(self._app_paths_file, "r", encoding="utf-8") as file:
            app_paths = json.load(file)

        raw_path_to_last_project = app_paths.get("last_project", "").strip()

        if raw_path_to_last_project:
            path_to_last_project = os.path.normpath(raw_path_to_last_project)

            if os.path.isfile(path_to_last_project):
                with open(path_to_last_project, "r", encoding="utf-8") as file:
                    last_project_config = json.load(file)

                project_name = last_project_config.get("last_project", "").strip()

                if project_name:
                    return project_name

        project_root = os.path.normpath("app_data/project_directory")

        try:
            projects = [
                name
                for name in os.listdir(project_root)
                if os.path.isdir(os.path.join(project_root, name))
            ]
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "Project directory 'app_data/project_directory' does not exist."
            ) from exc

        if not projects:
            raise RuntimeError(
                "No projects found in 'app_data/project_directory'."
            )

        return projects[0]

    def update_paths(self, project_name: str) -> None:
        """
        Rebuilds the internal path mapping for the given project name.

        Args:
            project_name (str): The new project to resolve paths for.
        """
        with open(self._app_paths_file, "r", encoding="utf-8") as file:
            raw_paths = json.load(file)

        self._paths = {
            key: os.path.normpath(path.replace("<project>", project_name))
            for key, path in raw_paths.items()
        }

    def resolve_path(self, key_or_path: str) -> str:
        """
        Resolves a configuration key to a full file path, or returns the path as-is
        if it is already a real path.

        Args:
            key_or_path (str): Key from config or already-resolved file path.

        Returns:
            str: Fully resolved and normalized file path.
        """
        if key_or_path in self._paths:
            return os.path.normpath(self._paths[key_or_path])

        return os.path.normpath(key_or_path)

    def _load_project_independent_paths(self) -> dict[str, str]:
        """
        Loads paths from app_paths.json without expanding <project>.

        This is used during initialization before any project is selected.

        Returns:
            dict[str, str]: Normalized raw path templates from app_paths.json
            that do not depend on a project placeholder.
        """
        with open(self._app_paths_file, "r", encoding="utf-8") as file:
            raw_paths = json.load(file)

        project_independent_paths = {
            key: os.path.normpath(path)
            for key, path in raw_paths.items()
            if "<project>" not in path
        }

        return project_independent_paths