from config import conf

class PlotConfigurator:
    def __init__(self):
        """Initialize PlotConfigurator with predefined plot configurations."""
        n_agents = conf("n_agents")
        colors = ["red", "blue", "black", "green", "orange"]
        linestyles = ["--", "-.", ":", (0, (1, 0.5)), (0, (10, 2))]

        self.preconfigured = {
            "Select plot": "",
            "All on All": self.plot_conf(
                "time", 
                [f"A{i} on A{j}" for i in conf("agents") for j in conf("agents")] + [f"Honesty A{i}" for i in conf("agents")],
                [linestyles[i % len(linestyles)] for i in conf("agents") for _ in conf("agents")] + ["-"] * n_agents,
                [colors[i % len(colors)] for i in conf("agents")] * (n_agents + 1)
            ),
        }
        print(self.preconfigured)

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
