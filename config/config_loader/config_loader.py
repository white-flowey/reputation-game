import yaml
    
from .config_checker import ConfigChecker

class ConfigLoader:
    def __init__(self, filename):
        self.config = self.load_data(filename)
        self.conf = self.create_last_name_mapping(self.config)
        self.set_config_defaults()
        
        checker = ConfigChecker(self.conf)
        checker.check_config()

    def load_data(self, filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)

    def create_last_name_mapping(self, d, parent_key=''):
        items = {}
        if "dict" in parent_key:
            items[parent_key] = d
        else:
            for k, v in d.items():
                if (isinstance(v, dict)):
                    items.update(self.create_last_name_mapping(v, k))
                else:
                    items[k] = v
        return items

    def set_config_defaults(self):
        self.conf["agents"] = list(range(self.conf["n_agents"]))
        self.conf["times"] = self.conf["n_rounds"] * 3 + 1
        for character in self.conf["characters_dict"]:
            if "all" in character and len(character) > self.conf["n_agents"]:
                del character["all"]
            character.setdefault("all", "ordinary")

    def get(self, key):
        return self.conf.get(key)

def init_conf():
    config = ConfigLoader('config/config.yml')
    return config.get

config = ConfigLoader('config/config.yml')
def conf(key):
    return config.get(key)