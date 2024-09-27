import os
from PyQt5.QtWidgets import QGridLayout, QColorDialog
from helper import create_button, create_label, create_select, update_plot
from .control_updater import ControlUpdater
from evaluate.postprocessor import Postprocessor

class ControlPanel(QGridLayout):
    def __init__(self, plotter):
        """Initialize the control panel for the plotter.

        Args:
            plotter: The plotter object that manages the data plots.
        """
        super().__init__()
        self.plotter = plotter
        self.fields = []
        self.visible = True
        self.index = 0
        self.updater = ControlUpdater(self, plotter)
        self.setup_data_source()

    def setup_data_source(self):
        """Set up the data source selection panel."""
        create_label("Data source", 0, 0, self)
        self.file_select = create_select(self.list_json_files(), 0, 1, self, func=self.load_data)

    def setup_main_menu(self):
        """Set up the main control panel with axis selection and preconfigured options."""
        create_label("Preconfigured", 0, 2, self)
        self.preconf = create_select(self.plotter.plots.keys(), 0, 3, self, self.apply_preconfigured)
        create_label("X-Axis", 1, 0, self)
        self.x_axis_select = create_select(self.fields, 1, 1, self, func=self.plotter.plot_data)
        create_button("Add Y-Axis", self.updater.add_y_axis, self, 2, 0)
        create_button("Plot", self.plotter.plot_data, self, 2, 1)
        self.y_axes = []

    @update_plot
    def load_data(self, filename: str = None):
        """Load data from the selected file.

        Args:
            filename (str, optional): Name of the selected data file. Defaults to None.
        """
        if not getattr(self.plotter, "data", None):
            self.setup_main_menu()
        if filename != "Select file":
            filename = "/".join(["evaluate/results/simulation", filename])
            self.plotter.data = Postprocessor(filename=filename).select
            self.x_axis_select.deleteLater()
            self.fields = sorted(self.plotter.data.keys())
            self.x_axis_select = create_select(self.fields, 1, 1, self, func=self.plotter.plot_data)
            self.file_select.setCurrentText(filename)

    def list_json_files(self) -> list:
        """List all JSON files in the data directory.

        Returns:
            list: A list of JSON file names.
        """
        json_files = [f for f in os.listdir("evaluate/results/simulation") if f.endswith('.json')]
        return ["Select file"] + json_files

    @update_plot
    def apply_preconfigured(self, plot_name: str):
        """Apply a preconfigured plot setup.

        Args:
            plot_name (str): The name of the preconfigured plot.
        """
        if plot_name == "Select plot":
            return
        [self.updater.remove_y_axis(y["id"]) for y in self.y_axes]
        plot = self.plotter.plots[plot_name]
        self.x_axis_select.setCurrentText(plot["x_axis"])
        for y in plot["y_axes"]:
            self.updater.add_y_axis(y["field"], y["line_style"], y["color"])

    @update_plot
    def select_color(self, id: int):
        """Open a color selection dialog and set the color for the selected Y-axis.

        Args:
            id (int): The ID of the Y-axis to update.
        """
        color = QColorDialog.getColor()
        if color.isValid():
            y_axis = [y for y in self.y_axes if y["id"] == id][0]
            y_axis["color"] = color.name()
            y_axis["color_button"].setStyleSheet(f"background-color: {color.name()}")

    def toggle(self):
        """Toggle the visibility of the control panel widgets."""
        for i in reversed(range(self.count())):
            widget = self.itemAt(i).widget()
            if widget:
                widget.setVisible(not self.visible)
        self.visible = not self.visible
        self.plotter.adjust_plot_size()
