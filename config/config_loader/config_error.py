class ConfigError(Exception):
    """Exception raised for errors in the configuration settings.

    Attributes:
        param (str): The name of the configuration parameter that caused the error.
        error_type (str): The type of error (e.g., missing, invalid_type, invalid_length).
        expected (any): The expected value or type (if applicable).
        actual (any): The actual value or type (if applicable).
    """

    def __init__(self, param: str, error_type: str, expected=None, actual=None):
        """Initialize the ConfigError with parameter details.

        Args:
            param (str): The name of the configuration parameter that caused the error.
            error_type (str): The type of error (e.g., 'missing', 'invalid_type', 'invalid_length').
            expected (any, optional): The expected value or type. Defaults to None.
            actual (any, optional): The actual value or type. Defaults to None.
        """
        self.param = param
        self.error_type = error_type
        self.expected = expected
        self.actual = actual
        
        error_messages = {
            "missing": f"Configuration value for '{param}' is missing.",
            "invalid_type": f"Configuration value for '{param}' should be {expected}, but got {actual}.",
            "invalid_length": f"List '{param}' length should be {expected}, but got {actual}."
        }
        self.message = error_messages.get(error_type, f"Error with '{param}': {error_type}")
        super().__init__(self.message)

    def __str__(self):
        """Return the string representation of the error message."""
        return self.message
