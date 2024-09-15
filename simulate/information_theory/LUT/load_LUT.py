import os
import json
import numpy as np
from scipy.interpolate import RegularGridInterpolator

def init_LUT():
    filename_mu = "LUT_mu.json"
    filename_la = "LUT_la.json"
    length = 1000

    
    def load_data(filename):
        file_path = os.path.join(os.path.dirname(__file__), filename)
        with open(file_path, "r") as f:
            return json.load(f)["data"]

    mu_values = np.log10(np.array(load_data(filename_mu)) + 1)
    la_values = np.log10(np.array(load_data(filename_la)) + 1)
    x = y = np.linspace(0, length - 1, length)

    class LookUpTable:
        def __init__(self, x, y, mu_data, la_data):
            self.mu = RegularGridInterpolator((x, y), mu_data, method="linear")
            self.la = RegularGridInterpolator((x, y), la_data, method="linear")
            if len(x) != len(y):
                raise ValueError("LUT is not quadratic. This is not implemented yet!")
            self.len = len(x)

    # Create and return the LookUpTable object
    return LookUpTable(x, y, mu_values, la_values)

LUT = init_LUT()