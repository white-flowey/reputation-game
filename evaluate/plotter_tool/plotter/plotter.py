import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QSizePolicy
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from .control_panel import ControlPanel
from .plot_configurator import PlotConfigurator
from helper import create_button


class Plotter(QWidget):
    def __init__(self, remove_callback: callable):
        """Initialize the Plotter widget with controls and plotting canvas.

        Args:
            remove_callback (callable): Function to call (passed from PlotterGrid) when removing the plotter.
        """
        super().__init__()
        self.remove_callback = remove_callback
        self.plots = PlotConfigurator().preconfigured
        self.controls = ControlPanel(self)
        self.setup_main()
        self.setup_plot()
        self.add_remove_button()

    def setup_main(self):
        """Set up the main layout with controls and toggle button."""
        self.main_layout = QVBoxLayout(self)
        self.toggle_button = create_button("Toggle Controls", self.controls.toggle, self.main_layout)
        self.main_layout.addLayout(self.controls)
        self.setLayout(self.main_layout)
        
    def setup_plot(self):
        """Set up the plot figure, canvas, and toolbar."""
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.canvas)

    def add_remove_button(self):
        """Add a button to remove the plotter."""
        remove_button = create_button("Remove Plotter", self.remove_callback, self.main_layout)
        self.main_layout.addWidget(remove_button)

    def adjust_plot_size(self):
        """Update the layout to adjust the plot size when controls are hidden or shown."""
        self.canvas.updateGeometry()
        self.main_layout.update()

    def plot_data(self):
        """Plot the selected data with specified axes and styles."""
        if getattr(self, "data", None):
            self.figure.clear()
            x_field = self.controls.x_axis_select.currentText()
            ax = self.canvas.figure.add_subplot(111)
            for y_axis in self.controls.y_axes:
                y_field = y_axis["data"].currentText()
                ax.plot(self.data[x_field], self.data[y_field], 
                        linestyle=y_axis["line_style"].currentText(), 
                        color=y_axis["color"], 
                        label=y_field, 
                        linewidth=0.5)
            ax.set_xlabel(x_field)
            ax.set_ylabel("Values")
            ax.legend()
            self.canvas.draw()
