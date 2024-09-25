from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QGridLayout, QSizePolicy
from PyQt5.QtCore import Qt
import sys

from .plotter import Plotter
from helper import create_button


class PlotterGrid(QMainWindow):
    def __init__(self):
        """Initialize the main window for displaying multiple plotter instances."""
        super().__init__()
        self.setWindowTitle("Simulation Data Plotter")
        self.plotters = []
        self.setup_main()
        self.setup_plotters()
        self.central_widget.setLayout(self.main_layout)
        
    def setup_main(self) -> None:
        """Set up the main layout and add instance button."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.add_instance_button = QPushButton("Add Instance")
        self.add_instance_button.clicked.connect(lambda: self.add_plotter())
        self.main_layout.addWidget(self.add_instance_button)

    def setup_plotters(self) -> None:
        """Initialize the plotter container with a grid layout."""
        self.plotter_container = QWidget()
        self.plotter_layout = QGridLayout(self.plotter_container)
        self.plotter_layout.setSpacing(10)
        self.plotter_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addWidget(self.plotter_container)
        self.add_plotter()

    def add_plotter(self) -> None:
        """Add a new plotter instance to the grid layout."""
        plotter = Plotter(remove_callback=lambda: self.remove_plotter(plotter))
        plotter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        column = len(self.plotters)
        self.plotter_layout.setColumnStretch(column, 1)
        self.plotters.append(plotter)
        self.update_plotter_layout()

    def update_plotter_layout(self) -> None:
        """Update the grid layout and resize the plotters based on screen width."""
        n_plotters = len(self.plotters)
        if n_plotters == 0:
            return

        self.plotter_layout.setColumnStretch(n_plotters - 1, 1)
        screen_width = self.screen().availableGeometry().width()
        spacing = self.plotter_layout.horizontalSpacing() * (n_plotters + 1)
        l, t, r, b = self.plotter_layout.getContentsMargins()
        total_width = screen_width - spacing - (l + r)
        plotter_width = total_width // n_plotters

        for i, plotter in enumerate(self.plotters):
            self.plotter_layout.addWidget(plotter, 0, i)
            plotter.setFixedWidth(plotter_width)

    def remove_plotter(self, plotter: Plotter) -> None:
        """Remove a plotter from the grid layout.

        Args:
            plotter (Plotter): The plotter instance to be removed.
        """
        self.plotters.remove(plotter)
        plotter.deleteLater()
        for col in range(self.plotter_layout.columnCount()):
            item = self.plotter_layout.itemAtPosition(0, col)
            if item and item.widget() == plotter:
                self.plotter_layout.removeWidget(plotter)
            self.plotter_layout.setColumnStretch(col, 0)
        self.update_plotter_layout()


def plot() -> None:
    """Start the Qt application and show the main window."""
    app = QApplication(sys.argv)
    
    main_window = PlotterGrid()
    main_window.showFullScreen()

    sys.exit(app.exec_())
