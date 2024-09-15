from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QGridLayout, QSizePolicy
from PyQt5.QtCore import Qt
import sys
from .plotter import Plotter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulation Data Plotter")
        self.setup_main()
        self.setup_plotters()
        self.central_widget.setLayout(self.main_layout)
        
    def setup_main(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.add_instance_button = QPushButton("Add Instance")
        self.add_instance_button.clicked.connect(lambda: self.add_plotter(True))
        self.main_layout.addWidget(self.add_instance_button)

    def setup_plotters(self):
        self.plotter_container = QWidget()
        self.plotter_layout = QGridLayout(self.plotter_container)
        self.plotter_layout.setSpacing(10)
        self.plotter_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addWidget(self.plotter_container)

        self.plotters = []
        self.add_plotter(removable=False)

    def add_plotter(self, removable=True):
        plotter = Plotter(remove_callback=self.remove_plotter, removable=removable)
        
        # Set the size policy for the Plotter widget to expanding
        plotter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add the plotter to the grid layout
        column = len(self.plotters)  # Add it to the next column
        self.plotter_layout.addWidget(plotter, 0, column)
        
        # Ensure equal space allocation for all plotters
        self.plotter_layout.setColumnStretch(column, 1)
        for i in range(len(self.plotters)):
            self.plotter_layout.setColumnStretch(i, 1)
        
        self.plotters.append(plotter)

    def remove_plotter(self, plotter):
        if plotter in self.plotters:
            # Get the position of the plotter in the grid
            index = self.plotters.index(plotter)
            
            # Remove the plotter widget
            self.plotters.remove(plotter)
            plotter.deleteLater()

            # Remove the widget from the grid layout
            for col in range(self.plotter_layout.columnCount()):
                item = self.plotter_layout.itemAtPosition(0, col)
                if item and item.widget() == plotter:
                    self.plotter_layout.removeWidget(plotter)

            # Re-adjust the grid layout to remove empty columns and reset stretch factors
            for col in range(self.plotter_layout.columnCount()):
                self.plotter_layout.setColumnStretch(col, 0)  # Reset stretch

            for i, remaining_plotter in enumerate(self.plotters):
                self.plotter_layout.addWidget(remaining_plotter, 0, i)  # Reinsert remaining plotters
                self.plotter_layout.setColumnStretch(i, 1)  # Set equal stretch for all remaining plotters



def plot():
    app = QApplication(sys.argv)
    
    main_window = MainWindow()
    main_window.showFullScreen()

    sys.exit(app.exec_())
