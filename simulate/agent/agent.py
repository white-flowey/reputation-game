import numpy as np
from statistics import median

from config import conf
from helper import character_mapping
from simulate.information_theory import Info
from . import Initiator, Sender, Receiver, Updater

agents = conf("agents")

class Agent:
    def __init__(self, id, honesty, character, random_dict, log, conf):
        self.conf = conf
        self.id = id
        self.honesty = honesty
        self.character = character
        self.random = random_dict
        self.log = log
        self.setup_character(character)
        self.setup_memory()
        self.initialise_memory()

        self.Initiator = Initiator(self)
        self.Sender = Sender(self)
        self.Receiver = Receiver(self)
        self.Updater = Updater(self, log)

    def setup_character(self, character):
        for key, value in character_mapping(character).items():
            setattr(self, key, value)

    def setup_memory(self):
        n_agents = self.conf("n_agents")
        self.friendships = [Info(1, 0) if i == self.id else Info(0, 0) for i in agents]
        self.I = [Info(0, 0)] * n_agents
        self.Iothers = [[Info(0, 0)] * n_agents] * n_agents
        self.J = [[Info(0, 0)] * n_agents] * n_agents
        self.C = [[Info(0, 0)] * n_agents] * n_agents
        self.K = [np.sqrt(np.pi)] * self.conf("KLENGTH")
        self.kappa = 1
        self.n_conversations = [{"partner": 0, "topic": 0}] * n_agents

    def initialise_memory(self):
        # self.I = [[Info(self.conf("mindI")[a][b][0], self.conf("mindI")[a][b][1]) if self.conf("mindI") and a == id else Info(0,0) for b in agents] for a in agents]
        self.K = self.conf("Ks")[id] if self.conf("Ks") else [np.sqrt(np.pi) for _ in range(self.conf("KLENGTH"))]
        self.kappa = median(self.K) / np.sqrt(np.pi) if self.conf("Ks") else 1

### HELPER ###
    def initial_state(self):
        return {
            "honesty": self.honesty, "character": self.character, 
            "friendships": [f.round_mean() for f in self.friendships],
            "I": [i.round_mean() for i in self.I],
            "Iothers": [[ii.round_mean() for ii in i] for i in self.Iothers],
            "J": [[jj.round_mean() for jj in j] for j in self.J],
            "lastK": self.K[-1], "kappa": float(self.kappa)
        }

    def save_state(self, topic, partners, setting):
        if setting == "one_to_one":
            partner = partners[0]
            state = {
                "topic": int(topic),
                "partner": int(partner),
                "id": self.id,
                "Iself": self.I[self.id].round_mean(),
                "Ipartner": self.I[partner].round_mean(),
                "Iothers": self.Iothers[partner][topic].round_mean(),
                "Jself": self.J[self.id][topic].round_mean(),
                "Jpartner": self.J[partner][topic].round_mean(),
                "lastK": round(float(self.K[-1]), 3),
                "kappa": round(float(self.kappa), 3)
            }
            if topic == self.id:
                state["friendships"] = float(self.friendships[partner].mean)
            if topic not in [self.id, partner]:
                state["Itopic"] = float(self.I[topic].mean)
        else:
            state = {}
        return state

    def _save_state(self, log=False):
        if log:
            return {"id": self.id, "honesty": round(self.honesty, 2), "friendships": [round(I.mean, 2) for I in self.friendships], "character": self.character, 
                "I": [str(self.I[b].round(2)) for b in self.conf("agents")],
                "J": [[str(self.J[a][b].round(2)) for b in self.conf("agents")] for a in self.conf("agents")],
                "C": [[str(self.C[a][b].round(2)) for b in self.conf("agents")] for a in self.conf("agents")],
                "K": [round(k, 2) for k in self.K], "kappa": round(self.kappa, 2)
            }
        else:
            return {"id": self.id, "honesty": self.honesty, "friendships": [I.mean for I in self.friendships], "character": self.character, 
                "I": [self.I[b].mean for b in self.conf("agents") for b in self.conf("agents")],
                "J": [[self.J[a][b].mean for b in self.conf("agents")] for a in self.conf("agents")],
                "C": [[self.C[a][b].mean for b in self.conf("agents")] for a in self.conf("agents")],
                "K": self.K, "kappa": self.kappa
            }
