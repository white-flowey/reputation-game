from .config_error import ConfigError

class ConfigChecker:
    """A class to check the configuration settings for the simulation."""

    def __init__(self, conf):
        """Initialize the ConfigChecker with the given configuration.

        Args:
            conf (dict): The configuration settings to be checked.
        """
        self.conf = conf

    def check_config(self):
        """Run all configuration checks."""
        self.check_integer_parameters()
        self.check_list_lengths()
        self.check_initial_mind_structure()
        self.check_character_consistency()

    def check_integer_parameters(self):
        """Check that all required integer parameters are present and valid.

        Raises:
            ConfigError: If any integer parameter is missing or not of type `int`.
        """
        int_types = ["n_agents", "n_rounds", "n_stat", "seed", "seed_offset"]
        for i in int_types:
            if i not in self.conf:
                raise ConfigError(i, "missing")
            if not isinstance(self.conf[i], int):
                raise ConfigError(i, "invalid_type", int, type(self.conf[i]))

    def check_list_lengths(self):
        """Check the lengths of lists in the configuration.

        Raises:
            ConfigError: If the length of 'honesties' does not match 'n_agents',
                         or if any list is of an invalid type or length.
        """
        if self.conf.get("honesties_dict") and len(self.conf["honesties_dict"]) != self.conf["n_agents"]:
            raise ConfigError("honesties_dict", "invalid_length", self.conf["n_agents"], len(self.conf["honesties_dict"]))

        list_types = ["mindI", "Ks"]
        for l in list_types:
            if self.conf.get(l) and not isinstance(self.conf[l], list):
                raise ConfigError(l, "invalid_type", list, type(self.conf[l]))

        if len(self.conf.get("Ks", [])) > 10:
            raise ConfigError("Ks", "invalid_length", "<= 10", len(self.conf["Ks"]))

    def check_initial_mind_structure(self):
        """Check the structure of the initial mind configuration.

        Raises:
            ConfigError: If the length of 'mindI' does not match 'n_agents',
                         or if entries in 'mindI' do not have the correct structure.
        """
        mindI = self.conf.get("mindI")
        if mindI:
            if len(mindI) != self.conf["n_agents"]:
                raise ConfigError("mindI", "invalid_length", self.conf["n_agents"], len(mindI))
            for entry in mindI:
                if len(entry) != 2:
                    raise ConfigError("Entries of entries in mindI", "invalid_length", 2, len(entry))

    def check_character_consistency(self):
        """Check that character configurations are consistent with the number of agents.

        Raises:
            ConfigError: If the length of any character list does not match 'n_agents'.
        """
        characters = self.conf["characters_dict"]
        for character in characters:
            if "all" not in character and len(character) != self.conf["n_agents"]:
                raise ConfigError("Number of characters", "invalid_length", self.conf["n_agents"], len(character))
