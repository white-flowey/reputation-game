import os
import streamlit as st
import matplotlib.pyplot as plt
from simulate import Game
from evaluate import Postprocessor
from evaluate.plotter_tool import PlotConfigurator
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True  

st.set_page_config(initial_sidebar_state="expanded")
if 'results' not in st.session_state:
    st.session_state.results = None

class ConfigUpdater():
    def __init__(self):
        self.config_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'config', 'config.yml')
        self.config = self.load_config()
        
    def load_config(self):
        with open(self.config_file) as file:
            return yaml.load(file)

    def update_config(self, config_update):
        """Update the configuration with new values without overwriting the entire config."""
        for key, value in config_update.items():
            # Update only if the key exists in the current config
            if key in self.config:
                self.config[key].update(value)  # Update the specific field
            else:
                self.config[key] = value  # Add the new field if it doesn't exist

        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file)

    
class ConfigSidebar():
    def __init__(self):
        self.config_updater = ConfigUpdater()
        self.n_agents = st.sidebar.number_input("Number of Agents", value=3, min_value=2, max_value=5)
        self.honesties = st.sidebar.text_area("Honesties", value='0: 0.17; 1: 0.8; 2: 0.95')
        self.characters = st.sidebar.text_area("Characters", value='0: "ordinary"; 1: "deceptive"')
        self.blush_freq_lie = st.sidebar.number_input("Blush Frequency Lie", value=0.1, min_value=0.0, max_value=1.0)
        self.continuous_friendship = st.sidebar.checkbox("Continuous Friendship", value=True)

        if st.sidebar.button("Run Simulation"):
            self.run_simulation()

    def run_simulation(self):
        self.honesties = self.parse_input(self.honesties, 'honesties')
        self.characters = self.parse_input(self.characters, 'characters')
        self.config_updater.update_config(
            {"game": {"n_agents": self.n_agents, "honesties_dict": self.honesties, "characters_dict": [self.characters]},
            "constants": {"BLUSH_FREQ_LIE": self.blush_freq_lie},
            "switches": {"CONTINUOUS_FRIENDSHIP": self.continuous_friendship}}
        )
        results = Game(write_to_file=False).run(override=True)
        data = Postprocessor(data=results).select
        st.session_state.results = data
        st.success("Configuration updated and game executed!")

    def parse_input(self, input_str, input_type='honesties'):
        output_dict = {}
        for pair in input_str.split(';'):
            try:
                key, value = pair.split(':')
                output_dict[int(key.strip()) if input_type == 'honesties' else key.strip()] = \
                    float(value.strip()) if input_type == 'honesties' else value.strip().strip('"')
            except ValueError:
                st.error(f"Invalid format in {input_type} input: '{pair}'. Expected 'key: value'.")
                return None
        return output_dict


class App():
    def __init__(self):
        st.title("Reputation Game - Demo")
        st.sidebar.header("Configuration Panel")
        self.sidebar = ConfigSidebar()
        self.plotter = Plotter()

class Plotter():
    def __init__(self):
        self.figure, self.ax = plt.subplots(figsize=(10, 5))
        self.plots = PlotConfigurator().preconfigured
        self.selected_plot = st.selectbox("Select Preconfigured Plot", options=list(self.plots.keys()))
        if st.session_state.results is not None and self.plots != "Select plot":
            self.plot_data()
        else:
            st.write("No results to plot. Please configure and run the simulation on the left.")

    def plot_data(self):
        """Plot the selected data with specified axes and styles."""
        self.plot = self.plots[self.selected_plot]
        print(self.plots)
        print(self.plot)
        self.ax.clear()
        x_field = self.plot["x_axis"]
        for y_axis in self.plot["y_axes"]:
            y_field = y_axis["field"]
            self.ax.plot(st.session_state.results[x_field], st.session_state.results[y_field], 
                    linestyle=y_axis["line_style"], 
                    color=y_axis["color"], 
                    label=y_field, 
                    linewidth=0.5)
        self.ax.set_xlabel(x_field)
        self.ax.set_ylabel("Values")
        self.ax.legend()
        st.pyplot(self.figure)
    
app = App()