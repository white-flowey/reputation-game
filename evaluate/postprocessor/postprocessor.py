import json
from .time_series_maker import TimeSeriesMaker
from .calculate_statistics import calculate_statistics
from .prepare_plotting import create_select_for_plotter

class Postprocessor:
    """Loads data from simulation output JSON, converts to time series data, 
    applies statistics, and prepares for plotting."""
    def __init__(self, filename: str = None, data: list = None) -> None:
        """Initialize the Postprocessor with data loaded from a JSON file.

        Args:
            filename (str): The path to the JSON file containing the results.
        """
        if data:
            self.data = data
        elif filename:
            self.data = self.load_results(filename)
        else:
            raise NotImplementedError
        times = len(self.data[0])
        ts_maker = TimeSeriesMaker()

        self.data = [ts_maker.make_time_series_data(result, times) for result in self.data]
        self.data = calculate_statistics(self.data, times)
        self.select = create_select_for_plotter(self.data, times)

    def load_results(self, filename: str) -> list[dict]:
        """Load results from a JSON file."""
        with open(filename, "r") as json_file:
            return json.load(json_file)
