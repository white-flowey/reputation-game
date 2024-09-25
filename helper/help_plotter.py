from typing import Callable
from PyQt5.QtWidgets import QComboBox, QPushButton, QLabel

def create_select(items, row: int, col: int, layout, func=None) -> QComboBox:
    """Creates a QComboBox widget with given items.

    Args:
        items (list): A list of items to add to the combo box.
        row (int): The row in the layout where the combo box will be placed.
        col (int): The column in the layout where the combo box will be placed.
        layout (QLayout): The layout to which the combo box will be added.
        func (Callable, optional): An optional function to connect to the currentTextChanged signal.

    Returns:
        QComboBox: The created combo box widget.
    """
    combo = QComboBox()
    combo.addItems(items)
    if func: combo.currentTextChanged.connect(func)
    layout.addWidget(combo, row, col)
    return combo

def create_button(label: str, func: Callable, layout, row: int = None, col: int = None) -> QPushButton:
    """Creates a QPushButton widget with a given label.

    Args:
        label (str): The text to display on the button.
        func (Callable): The function to call when the button is clicked.
        layout (QLayout): The layout to which the button will be added.
        row (int, optional): The row in the layout where the button will be placed.
        col (int, optional): The column in the layout where the button will be placed.

    Returns:
        QPushButton: The created button widget.
    """
    btn = QPushButton(label)
    btn.clicked.connect(func)
    if row is not None and col is not None:
        layout.addWidget(btn, row, col)
    else:
        layout.addWidget(btn)
    return btn

def create_label(text: str, row: int, col: int, layout) -> None:
    """Creates a QLabel widget with the given text.

    Args:
        text (str): The text to display on the label.
        row (int): The row in the layout where the label will be placed.
        col (int): The column in the layout where the label will be placed.
        layout (QLayout): The layout to which the label will be added.
    """
    lbl = QLabel(text)
    layout.addWidget(lbl, row, col)

def update_plot(func: Callable) -> Callable:
    """Decorator to update the plot after the function execution."""
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)  # Call the original function
        self.plotter.plot_data()  # Update the plot
        return result  # Return the result of the original function
    return wrapper
