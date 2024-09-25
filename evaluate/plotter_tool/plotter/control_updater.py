from helper import create_button, create_select, update_plot

class ControlUpdater:
    def __init__(self, controls, plotter):
        """Initialize ControlUpdater to manage the control panel's Y-axes.

        Args:
            controls: The control panel layout object.
            plotter: The plotter object that handles data plotting.
        """
        self.controls = controls
        self.plotter = plotter

    @update_plot
    def remove_y_axis(self, id: int):
        """Remove the Y-axis control from the panel, update the plot, and rearrange remaining y-axes.

        Args:
            id (int): The ID of the Y-axis to remove.
        """
        row, y = [(row, y) for row, y in enumerate(self.controls.y_axes) if y["id"] == id][0]
        [y[key].deleteLater() for key in y.keys() if key not in ["id", "color"]]
        self.controls.y_axes = [y for y in self.controls.y_axes if y["id"] != id]
        
        for r, y in enumerate(self.controls.y_axes[row:]):
            [self.controls.removeWidget(y[key]) for key in y.keys() if key not in ["id", "color"]]
            [self.controls.addWidget(y[key], row + r + 3, col - 1) for col, key in enumerate(y.keys()) if key not in ["id", "color"]]
        
        self.plotter.plot_data()

    @update_plot
    def add_y_axis(self, y_field: str = None, line_style: str = None, color: str = None):
        """Add a new Y-axis control to the panel.

        Args:
            y_field (str, optional): The Y-axis data field. Defaults to None.
            line_style (str, optional): The line style for the plot. Defaults to None.
            color (str, optional): The color for the plot line. Defaults to None.
        """
        index = self.controls.index
        row = len(self.controls.y_axes) + 3
        axis = {
            "id": index,
            "data": create_select(self.controls.fields, row, 0, self.controls),
            "line_style": create_select(["-", "--", "-.", ":"], row, 1, self.controls),
            "color_button": create_button("Color", lambda: self.controls.select_color(index), self.controls, row, 2),
            "remove": create_button("Remove", lambda: self.remove_y_axis(index), self.controls, row, 3),
            "color": color or "blue"
        }
        
        # Set values if provided
        if y_field and line_style and color:
            axis["data"].setCurrentText(y_field)
            axis["line_style"].setCurrentText(line_style)
            axis["color_button"].setStyleSheet(f"background-color: {color}")
        
        self.controls.y_axes.append(axis)
        self.controls.index += 1
