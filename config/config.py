import yaml
import os
import shutil


### ERROR HANDLING
class ConfigError(Exception):
    def __init__(self, param, error_type, expected=None, actual=None):
        self.param = param
        self.error_type = error_type
        self.expected = expected
        self.actual = actual
        
        # Custom error message based on error type
        if error_type == "missing":
            self.message = f"Configuration value for '{param}' is missing."
        elif error_type == "invalid_type":
            self.message = f"Configuration value for '{param}' should be {expected}, but got {actual}."
        elif error_type == "invalid_length":
            self.message = f"List '{param}' length should be {expected}, but got {actual}."
        else:
            self.message = f"Error with '{param}': {error_type}"

        super().__init__(self.message)

    def __str__(self):
        return self.message
    

### CONFIG
class Config:
    def __init__(self, filename):
        self.config = self.load_data(filename)
        self.conf = self._create_last_name_mapping(self.config)
        self.set_config_defaults_if_needed()
        self.check_config()

    def load_data(self, filename):
        with open(os.path.join(os.path.dirname(__file__), filename), 'r') as file:
            return yaml.safe_load(file)

    def _create_last_name_mapping(self, d, parent_key=''):
        items = {}
        if "dict" in parent_key:
            items[parent_key] = d
        else:
            for k, v in d.items():
                if (isinstance(v, dict)):
                    items.update(self._create_last_name_mapping(v, k))
                else:
                    last_name = k
                    items[last_name] = v
        return items
    
    
    def set_config_defaults_if_needed(self):
        self.conf["agents"] = list(range(self.conf["n_agents"]))
        characters = self.conf["characters_dict"]
        for i, character in enumerate(characters):
            if "all" in character.keys():
                if len(character.keys()) > self.conf["n_agents"]:
                    del character["all"]
            else:
                self.conf["characters_dict"][i]["all"] = "ordinary"

    
    def check_config(self):
        int_types = ["n_agents", "n_rounds", "n_stat", "seed", "seed_offset", "n_parallel_core_jobs"]
        for i in int_types:
            if i not in self.conf.keys():
                raise ConfigError(i, "missing")
            if not isinstance(self.conf[i], int):
                raise ConfigError(i, "invalid_type", int, type(self.conf[i]))
            
        list_types = ["honesties", "mindI", "Ks"]
        if self.conf["honesties"] and len(self.conf["honesties"]) != self.conf["n_agents"]:
            raise ConfigError("honesties", "need to have the length of n_agents")
        for l in list_types:
            if self.conf.get(l) and not isinstance(self.conf[l], list):
                raise ConfigError(l, "invalid_type", list, type(self.conf[l]))
        if self.conf.get("mindI"):
            mindI = self.conf["mindI"]
            if not len(mindI) == self.conf["n_agents"]:
                raise ConfigError("mindI", "Needs to have the lenghth of n_agents")
            for agent in mindI:
                if not len(agent) == self.conf["n_agents"]:
                    raise ConfigError("Entries in mindI", "need to have the lenghth of n_agents")
                for entry in agent:
                    if not len(entry) == 2:
                        raise ConfigError("Entries of entries in mindI", "Each element needs to have length 2")
        
        if not len("Ks") <= 10:
            raise ConfigError(l, "Needs to have a length below 10")

            
        characters = self.conf["characters_dict"]
        for character in characters:
            if "all" not in character.keys():
                if len(character.keys()) != self.conf["n_agents"]:
                    raise ConfigError("Number of characters has to match number of agents")
        
        ### ADD MORE CONFIG CHECKS HERE
    

    def get(self, key):
        return self.conf.get(key)

### HELPERS
def init_conf():
    config = Config('config.yml')
    return config.get

config = Config('config.yml')
def conf(key, reload=False):
    c = Config('config.yml') if reload else config
    return c.get(key)


### FOR TESTING PURPOSES
def replace_conf(test_config_path, original_config_path = 'config/config.yml'):
    if not os.path.exists(test_config_path):
        raise FileNotFoundError(f"Test config file not found: {test_config_path}")
    
    original_backup_path = original_config_path + '.bak'
    if not os.path.exists(original_backup_path):
        shutil.copy(original_config_path, original_backup_path)

    shutil.copy(test_config_path, original_config_path)

def restore_conf(original_config_path = 'config/config.yml'):
    original_backup_path = original_config_path + '.bak'
    
    if os.path.exists(original_backup_path):
        shutil.copy(original_backup_path, original_config_path)
        os.remove(original_backup_path)
    else:
        raise FileNotFoundError(f"Backup config file not found: {original_backup_path}")

