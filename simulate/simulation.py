import numpy as np

from config import init_conf
from .information_theory import Ift, Info
from .agent import Agent
from evaluate import Logger

class Simulation():
    def __init__(self, seed, characters_setup):
        self.characters_setup = characters_setup
        self.conf = init_conf()
        self.id = seed
        self.log = Logger(seed)
        self.build_simulation_name()
        self.make_random_dict(seed)
        self.init_agents()


    def make_random_dict(self, seed_var):
        seed_offsets = {
            "honesties": self.conf("seed"),
            "varying_random_honesties": seed_var,
            "fr_affinities": self.conf("seed") + seed_var + 1,
            "shynesses": self.conf("seed") + seed_var + 2,
            "one_to_one": self.conf("seed") + 10 * seed_var - 1,
            "n_recipients": self.conf("seed") + 10 * seed_var,
            "recipients": self.conf("seed") + 10 * seed_var + 1,
            "topic": self.conf("seed") + 10 * seed_var + 2,
            "honests": self.conf("seed") + 10 * seed_var + 3,
            "lies": self.conf("seed") + 10 * seed_var + 4,
            "blush": self.conf("seed") + 10 * seed_var + 5,
            "ego": self.conf("seed") + 10 * seed_var + 6,
            "strategic": self.conf("seed") + 10 * seed_var + 7,
            "flattering": self.conf("seed") + 10 * seed_var + 8,
            "aggressive": self.conf("seed") + 10 * seed_var + 9
        }
        self.random_dict = {key: np.random.RandomState(seed) for key, seed in seed_offsets.items()}


    def init_agents(self):
        ids = [i for i in self.conf("agents")]
        if self.conf("honesties"):
            honesties = self.conf("honesties") if self.conf("honesties") else honesties
        else:
            honesties = sorted([Info(0, 0).draw() for _ in self.conf("agents")]) if self.conf("RANDOM_HONESTIES") else np.linspace(0, 1, self.conf("n_agents"))
        characters = [self.characters_setup[agent] if agent in self.characters_setup.keys() else self.characters_setup["all"] for agent in self.conf("agents")]
        self.agents = [Agent(id, honesty, self.random_dict, character, self.log) for id, honesty, character in zip(ids, honesties, characters)]


    def save_state(self):
        return {"id": self.id, "name": self.name, "agents": [a.save_state().copy() for a in self.agents]}

    
    ### NAMING OUTPUT FILES

    def build_simulation_name(self):
        character = self.characters_setup
        character_agents = list(character.keys())
        character_names = list(character.values())
        n_agents = str(self.conf("n_agents"))
        names = self.conf("names_dict")

        basis_character = character["all"] if "all" in character.keys() else "ordinary"

        if len(character_agents) == 1 and "all" in character_agents:
            self.name = names[character_names[0]] + "_NA" + n_agents
        elif len(character_agents) == 2 and "all" in character_agents:
            character_names.remove(character["all"])
            self.name = "".join([names[character_names[0]], "+", basis_character])
        else:
            self.name = "mix_"
            basis_number = int(names[basis_character][:2])
            all_numbers = [int(names[character_name][:2]) for character_name in character_names]

            if basis_number not in all_numbers:
                all_numbers.append(basis_number)
            
            all_numbers.sort()
            all_numbers = [f"{num:02d}" for num in all_numbers]
            self.name += "|".join(all_numbers)
        self.name = "".join([self.name, "_NA=", n_agents, "_NR=",str(self.conf("n_rounds")), "_NST=", str(self.conf("n_stat"))])