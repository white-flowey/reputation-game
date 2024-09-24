class ConfigError(Exception):
    def __init__(self, param, error_type, expected=None, actual=None):
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
        return self.message