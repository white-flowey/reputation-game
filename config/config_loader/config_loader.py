import yaml
from .config_checker import ConfigChecker

class ConfigLoader:
    """Class to load and validate configuration from a YAML file.

    Attributes:
        config: The raw configuration data loaded from the YAML file.
        conf: The processed configuration with defaults and mappings applied.
    """

    def __init__(self, filename: str) -> None:
        """Initialize the ConfigLoader by loading configuration data and checking validity.

        Args:
            filename: The path to the YAML configuration file.
        """
        self.config = self.load_data(filename)
        self.conf = self.create_last_name_mapping(self.config)
        self.set_config_defaults()
        
        checker = ConfigChecker(self.conf)
        checker.check_config()

    def load_data(self, filename: str) -> dict:
        """Load configuration data from a YAML file.

        Args:
            filename: The path to the YAML configuration file.

        Returns:
            A dictionary containing the loaded configuration data.
        """
        with open(filename, 'r') as file:
            return yaml.safe_load(file)

    def create_last_name_mapping(self, d: dict, parent_key: str = '') -> dict:
        """Create a mapping for nested dictionary keys. Keep dicts as dicts if their key contains "dict".

        Args:
            d: The original dictionary to map.
            parent_key: The parent key to prepend to child keys.

        Returns:
            A flattened dictionary with combined keys.
        """
        items = {}
        if "dict" in parent_key:
            items[parent_key] = d
        else:
            for k, v in d.items():
                if isinstance(v, dict):
                    items.update(self.create_last_name_mapping(v, k))
                else:
                    items[k] = v
        return items

    def set_config_defaults(self) -> None:
        """Set default values for the configuration attributes."""
        self.conf["agents"] = list(range(self.conf["n_agents"]))
        self.conf["times"] = self.conf["n_rounds"] * 3 + 1
        for character in self.conf["characters_dict"]:
            if "all" in character and len(character) > self.conf["n_agents"]:
                del character["all"]
            character.setdefault("all", "ordinary")

    def get(self, key: str) -> any:
        """Get the configuration value for a given key."""
        return self.conf.get(key)

def init_conf() -> any:
    """Initialize configuration loader and return a function to access configuration values.

    Returns:
        A function that takes a key and returns the corresponding configuration value.
    """
    config = ConfigLoader('config/config.yml')
    return config.get

config = ConfigLoader('config/config.yml')

def conf(key: str) -> any:
    """Retrieve the configuration value for the specified key. Used as a shorthand throughout the simulation.

    Args:
        key: The configuration key to look up.

    Returns:
        The value associated with the key, or None if the key doesn't exist.
    """
    return config.get(key)
