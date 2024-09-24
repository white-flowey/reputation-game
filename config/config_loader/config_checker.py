from .config_error import ConfigError

class ConfigChecker:
    def __init__(self, conf):
        self.conf = conf

    def check_config(self):
        self.check_integer_parameters()
        self.check_list_lengths()
        self.check_initial_mind_structure()
        self.check_character_consistency()

    def check_integer_parameters(self):
        int_types = ["n_agents", "n_rounds", "n_stat", "seed", "seed_offset"]
        for i in int_types:
            if i not in self.conf:
                raise ConfigError(i, "missing")
            if not isinstance(self.conf[i], int):
                raise ConfigError(i, "invalid_type", int, type(self.conf[i]))

    def check_list_lengths(self):
        if self.conf.get("honesties") and len(self.conf["honesties"]) != self.conf["n_agents"]:
            raise ConfigError("honesties", "invalid_length", self.conf["n_agents"], len(self.conf["honesties"]))

        list_types = ["mindI", "Ks"]
        for l in list_types:
            if self.conf.get(l) and not isinstance(self.conf[l], list):
                raise ConfigError(l, "invalid_type", list, type(self.conf[l]))

        if len(self.conf.get("Ks", [])) > 10:
            raise ConfigError("Ks", "invalid_length", "<= 10", len(self.conf["Ks"]))

    def check_initial_mind_structure(self):
        mindI = self.conf.get("mindI")
        if mindI:
            if len(mindI) != self.conf["n_agents"]:
                raise ConfigError("mindI", "invalid_length", self.conf["n_agents"], len(mindI))
            for agent in mindI:
                if len(agent) != self.conf["n_agents"]:
                    raise ConfigError("Entries in mindI", "invalid_length", self.conf["n_agents"], len(agent))
                for entry in agent:
                    if len(entry) != 2:
                        raise ConfigError("Entries of entries in mindI", "invalid_length", 2, len(entry))

    def check_character_consistency(self):
        characters = self.conf["characters_dict"]
        for character in characters:
            if "all" not in character and len(character) != self.conf["n_agents"]:
                raise ConfigError("Number of characters", "invalid_length", self.conf["n_agents"], len(character))
