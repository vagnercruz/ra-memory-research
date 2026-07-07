"""Project explorer dock."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem

from ramr.models.project import Project

# Sections shown under an open project; they mirror the standard
# project subdirectories plus future research views.
PROJECT_SECTIONS = ("Snapshots", "Watch List", "Code Notes", "Exports")

NO_PROJECT_TEXT = "No project open"


class ProjectDock(QDockWidget):
    """Shows the open project and its research sections."""

    def __init__(self) -> None:
        super().__init__("Project Explorer")

        self.setObjectName("project_dock")
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self.setWidget(self._tree)

        self.clear_project()

    def show_project(self, project: Project) -> None:
        """Display ``project`` as the tree root with its research sections."""
        self._tree.clear()

        root = QTreeWidgetItem([f"{project.name} ({project.system})"])
        root.setToolTip(0, str(project.root_directory))
        for section in PROJECT_SECTIONS:
            root.addChild(QTreeWidgetItem([section]))

        self._tree.addTopLevelItem(root)
        root.setExpanded(True)

    def clear_project(self) -> None:
        """Show the empty state."""
        self._tree.clear()

        placeholder = QTreeWidgetItem([NO_PROJECT_TEXT])
        placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
        self._tree.addTopLevelItem(placeholder)
