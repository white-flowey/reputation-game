import sys
import ast
from pathlib import Path
import graphviz
import argparse

class CallGraphMaker:
    """Generates a call graph for a given Python package."""

    def __init__(self, project_folder: str):
        """Initializes the CallGraphMaker.

        Args:
            project_folder (str): The path to the Python package folder.
        """
        self.folder = Path(project_folder).resolve()
        self.filename = f"call_graphs/{self.folder.name}"
        self.project_files = self.collect_python_files()
        self.class_method_map: dict[str, str] = {}
        self.class_names: set[str] = set()
        self.method_to_class_map: dict[str, str] = {}
        self.excluded_functions: set[str] = {
            'print', 'setting', 'sqrt', 'keys', 'items', 'get', 'abs', 'sum',
            'setattr', 'str', 'np.array', 'median', 'pop', 'uniform', 'choice',
            'int', 'exists', 'array', 'round', 'lstrip', 'conf', 'Info', 
            'float', 'len', 'linspace', 'range'
        }

    def collect_python_files(self) -> list[Path]:
        """Collects all Python files in the specified folder.

        Returns:
            list: A list of Python file paths.
        """
        return [file for file in self.folder.rglob('*.py') if file.exists()]

    def collect_function_calls(self) -> dict[tuple[Path, str], list[str]]:
        """Collects function calls from the Python files.

        Returns:
            dict: A mapping of (file, caller_function) to called functions.
        """
        function_calls: dict[tuple[Path, str], list[str]] = {}
        for py_file in self.project_files:
            with open(py_file, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
                current_class: str | None = None
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        current_class = node.name
                        self.class_names.add(current_class)
                        for class_node in node.body:
                            if isinstance(class_node, ast.FunctionDef):
                                method_name = f"{current_class}.{class_node.name}"
                                self.class_method_map[method_name] = class_node.name
                                self.method_to_class_map[class_node.name] = current_class
                    if isinstance(node, ast.FunctionDef):
                        caller_function = f"{current_class}.{node.name}" if current_class else node.name
                        called_functions = self.extract_called_functions(node)
                        function_calls[(py_file, caller_function)] = list(called_functions)
        return self.update_called_functions(function_calls)

    def extract_called_functions(self, node: ast.FunctionDef) -> set[str]:
        """Extracts functions called within a given node.

        Args:
            node (ast.FunctionDef): The AST node to analyze.

        Returns:
            set: A set of called function names.
        """
        called_functions: set[str] = set()
        for body_node in ast.walk(node):
            if isinstance(body_node, ast.Call):
                if isinstance(body_node.func, ast.Name) and body_node.func.id not in self.excluded_functions:
                    called_functions.add(body_node.func.id)
                elif isinstance(body_node.func, ast.Attribute) and body_node.func.attr not in self.excluded_functions:
                    called_functions.add(body_node.func.attr)
        return called_functions

    def update_called_functions(self, function_calls: dict[tuple[Path, str], list[str]]) -> dict[tuple[Path, str], list[str]]:
        """Updates called functions with their fully qualified names.

        Args:
            function_calls (dict): The initial mapping of function calls.

        Returns:
            dict: Updated mapping of function calls with fully qualified names.
        """
        for (file, caller_function), called_functions in function_calls.items():
            function_calls[(file, caller_function)] = [
                self.class_method_map.get(called_function, called_function) for called_function in called_functions
            ]
        return function_calls

    def generate_call_graph(self) -> None:
        """Generates and saves the call graph as a PNG file."""
        dot = graphviz.Digraph()
        dot.attr(ranksep='1.5', nodesep='0.75')
        for class_name in self.class_names:
            dot.node(class_name, class_name)
        for (file, caller_function), called_functions in self.collect_function_calls().items():
            dot.node(caller_function, caller_function)
            if '.' in caller_function:
                class_name = caller_function.split('.')[0]
                if class_name in self.class_names:
                    dot.edge(class_name, caller_function)
            for called_function in called_functions:
                if called_function.split('.')[-1] not in self.excluded_functions:
                    if called_function in self.method_to_class_map:
                        qualified_name = f"{self.method_to_class_map[called_function]}.{called_function}"
                        dot.node(qualified_name, qualified_name)
                        dot.edge(caller_function, qualified_name)
                    if called_function in self.class_names:
                        dot.edge(caller_function, called_function)
        dot.render(self.filename, format='png', cleanup=True)
        print(f"Call graph saved as {self.filename}.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a call graph for a given Python package.")
    parser.add_argument("project_folder", type=str, help="Path to the Python package folder.")
    args = parser.parse_args()
    folder = Path(__file__).parent.parent / args.project_folder

    if not folder.exists() or not folder.is_dir():
        print(f"Error: The specified folder '{folder}' does not exist.")
        sys.exit(1)

    cg_maker = CallGraphMaker(folder)
    cg_maker.generate_call_graph()
