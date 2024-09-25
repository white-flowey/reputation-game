class PlotConfigurator:
    def __init__(self):
        """Initialize PlotConfigurator with predefined plot configurations."""
        self.preconfigured = {
            "Select plot": "",
            "All on All": self.plot_conf(
                "time", 
                ["A0 on A0", "A0 on A1", "A0 on A2", "A1 on A0", "A1 on A1", "A1 on A2", 
                 "A2 on A0", "A2 on A1", "A2 on A2", "Honesty A0", "Honesty A1", "Honesty A2"], 
                ["-."] * 3 + [":"] * 3 + ["--"] * 3 + ["-"] * 3, 
                ["red", "blue", "black"] * 4
            ),
            "A0 on All": self.plot_conf(
                "time", 
                ["A0 on A0", "A0 on A1", "A0 on A2"], 
                ["-"] * 3, 
                ["red", "blue", "black"]
            ),
            "All on A0": self.plot_conf(
                "time", 
                ["A0 on A0", "A1 on A0", "A2 on A0"], 
                ["-"] * 3, 
                ["red", "blue", "black"]
            ),
        }

    def plot_conf(self, x: str, y: list, style: list, color: list) -> dict:
        """Create a plot configuration.

        Args:
            x (str): X-axis label.
            y (list): List of Y-axis labels.
            style (list): List of line styles for each Y-axis.
            color (list): List of colors for each Y-axis.

        Returns:
            dict: A dictionary containing the plot configuration.
        """
        return {
            "x_axis": x, 
            "y_axes": [{"field": f, "line_style": s, "color": c} for f, s, c in zip(y, style, color)]
        }
