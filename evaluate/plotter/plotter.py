import os
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QComboBox, QPushButton, QColorDialog, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from config import conf


class Plotter(QWidget):
    def __init__(self, remove_callback=None, removable=True):
        super().__init__()
        self.fields = []
        self.remove_callback = remove_callback
        self.removable = removable
        self.index = 0
        self.control_visible = True
        self.setup()
        self.load_data(self.list_json_files()[1])
    
    def setup(self):
        self.main_layout = QVBoxLayout(self)
        self.control_layout = QGridLayout()
        self.init_controls()

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toggle_button = QPushButton("Hide Controls")
        self.toggle_button.clicked.connect(self.toggle_controls)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addLayout(self.control_layout)
        self.main_layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.main_layout.addWidget(self.toolbar)

        if self.removable:
            self.create_button("Remove", self.remove, 0, 2)

        self.setLayout(self.main_layout)

    def toggle_controls(self):
        if self.control_visible:
            for i in reversed(range(self.control_layout.count())):
                widget = self.control_layout.itemAt(i).widget()
                if widget:
                    widget.hide()
            self.control_visible = False
            self.toggle_button.setText("Show Controls")
        else:
            for i in reversed(range(self.control_layout.count())):
                widget = self.control_layout.itemAt(i).widget()
                if widget:
                    widget.show()
            self.control_visible = True
            self.toggle_button.setText("Hide Controls")

        self.adjust_plot_size()

    def adjust_plot_size(self):
        """Update the layout to adjust the plot size when controls are hidden/shown."""
        self.canvas.updateGeometry()
        self.main_layout.update()

    def init_controls(self):
        self.create_label("Data source", 0, 0)
        self.file_select = self.create_select(self.list_json_files(), 0, 1, func=self.load_data)
        self.create_label("Preconfigured", 0, 2)
        self.preconf = self.create_select(self.preconfigure_plots().keys(), 0, 3, self.apply_preconfigured)
        self.create_label("X-Axis", 1, 0)
        self.x_axis_select = self.create_select(self.fields, 1, 1)
        self.create_button("Add Y-Axis", self.add_y_axis, 2, 0)
        self.create_button("Plot", self.plot_data, 2, 1)
        self.y_axes = []
    
    def load_data(self, filename):
        if filename != "Select file":
            file_path = os.path.join(conf("folder"), "processor", filename)
            with open(file_path, "r") as json_file:
                self.data = json.load(json_file)

        self.x_axis_select.deleteLater()
        self.fields = sorted(self.data.keys())
        self.x_axis_select = self.create_select(self.fields, 1, 1)

    def list_json_files(self):
        json_files = [f for f in os.listdir("evaluate/results/processor") if f.endswith('.json')]
        return ["Select file"] + json_files

    def apply_preconfigured(self, plot_name):
        if plot_name == "Select plot": return
        [self.remove_y_axis(y["id"]) for y in self.y_axes]
        plot = self.preconfigure_plots()[plot_name]
        self.x_axis_select.setCurrentText(plot["x_axis"])
        for y in plot["y_axes"]:
            self.add_y_axis(y["field"], y["line_style"], y["color"])

    def x_axis(self):
        self.label("X-Axis", 1, 0)
        self.x_axis_select = self.select(self.fields, 1, 1)
    
    def y_axis(self):
        self.y_axes = []
        self.button("Add Y-Axis Dataset", self.add_y_axis, 2, 0)
        self.button("Plot", self.plot_data, 2, 1)
        
    def add_y_axis(self, y_field=None, line_style=None, color=None):
        index = self.index
        row = len(self.y_axes) + 3
        axis = {
            "id": index,
            "data": self.create_select(self.fields, row, 0),
            "line_style": self.create_select(["-", "--", "-.", ":"], row, 1),
            "color_button": self.create_button("Color", lambda: self.select_color(index), row, 2),
            "remove": self.create_button("Remove", lambda: self.remove_y_axis(index), row, 3),
            "color": color or "blue"
        }
        if y_field and line_style and color:
            axis["data"].setCurrentText(y_field)
            axis["line_style"].setCurrentText(line_style)
            axis["color_button"].setStyleSheet(f"background-color: {color}")
        self.y_axes.append(axis)
        self.index += 1

    def remove_y_axis(self, id):
        row, y = [(row, y) for row, y in enumerate(self.y_axes) if y["id"] == id][0]
        [y[key].deleteLater() for key in y.keys() if key not in ["id", "color"]]
        self.y_axes = [y for y in self.y_axes if y["id"] != id]
        
        for r, y in enumerate(self.y_axes[row:]):
            [self.control_layout.removeWidget(y[key]) for key in y.keys() if key not in ["id", "color"]]
            [self.control_layout.addWidget(y[key], row + r + 3, col - 1) for col, key in enumerate(y.keys()) if key not in ["id", "color"]]
        self.plot_data()

    def plot_data(self):
        self.figure.clear()
        x_field = self.x_axis_select.currentText()
        ax = self.canvas.figure.add_subplot(111)
        for y_axis in self.y_axes:
            y_field = y_axis["data"].currentText()
            ax.plot(self.data[x_field], self.data[y_field], linestyle=y_axis["line_style"].currentText(), color=y_axis["color"], label=y_field, linewidth=0.5)
        ax.set_xlabel(x_field)
        ax.set_ylabel("Values")
        ax.legend()
        self.canvas.draw()

    def select_color(self, id):
        color = QColorDialog.getColor()
        if color.isValid():
            y_axis = [y for y in self.y_axes if y["id"] == id][0]
            y_axis["color"] = color.name()
            y_axis["color_button"].setStyleSheet(f"background-color: {color.name()}")
        self.plot_data()

    def preconfigure_plots(self):
        return {
            "Select plot": "",
            "All on All": self.plot_conf("time", ["Honesty A0", "A0 on A0", "A0 on A1", "A0 on A2", "Honesty A1", "A1 on A0", "A1 on A1", "A1 on A2", "Honesty A2", "A2 on A0", "A2 on A1", "A2 on A2"], 
                                         ["-."] * 4 + [":"] * 4 + ["--"] * 4, ["gray", "red", "blue", "black"] * 3),
            "A0 on All": self.plot_conf("time", ["A0 on A0", "A0 on A1", "A0 on A2"], ["-"] * 3, ["red", "blue", "black"]),
            "All on A0": self.plot_conf("time", ["A0 on A0", "A1 on A0", "A2 on A0"], ["-"] * 3, ["red", "blue", "black"]),
        }

    def plot_conf(self, x, y, style, color):
        return {
            "x_axis": x, "y_axes": [{"field": f, "line_style": s, "color": c} for f, s, c in zip(y, style, color)]
        }

    def remove(self):
        if self.remove_callback:
            self.remove_callback(self)

    ### COMPONENTS
    def create_select(self, items, row, col, func=None):
        combo = QComboBox()
        combo.addItems(items)
        if func: combo.currentTextChanged.connect(func)
        combo.currentTextChanged.connect(self.plot_data)
        self.control_layout.addWidget(combo, row, col)
        return combo
    
    def create_button(self, label, func, row, col):
        btn = QPushButton(label)
        btn.clicked.connect(func)
        self.control_layout.addWidget(btn, row, col)
        return btn
    
    def create_label(self, text, row, col):
        lbl = QLabel(text)
        self.control_layout.addWidget(lbl, row, col)
