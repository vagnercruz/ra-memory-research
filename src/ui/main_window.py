class MainWindow(QMainWindow):

    def __init__(self):

        ...

        MenuBarBuilder.build(self)

        self.setStatusBar(StatusBar())

        self.setCentralWidget(Workspace())

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            ProjectDock()
        )

        self.addDockWidget(
            Qt.RightDockWidgetArea,
            InspectorDock()
        )