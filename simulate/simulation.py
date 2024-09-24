import numpy as np

from helper import make_random_dict
from .information_theory import Info
from .agent import Agent
from .conversation import Conversation
from evaluate import Logger

class Simulation():
    def __init__(self, seed, characters_setup, conf):
        self.conf = conf
        self.random = make_random_dict(seed)
        self.characters_setup = characters_setup
        self.id = seed
        self.log = Logger(seed)

        self.init_agents()
        self.schedule_conversations()

    def init_agents(self):
        
        agents = self.conf("agents")
        honesties = (self.conf("honesties") or 
                    sorted([Info(0, 0).draw() for _ in agents]) if self.conf("RANDOM_HONESTIES") 
                    else np.linspace(0, 1, self.conf("n_agents")))

        characters = [self.characters_setup.get(agent, self.characters_setup["all"]) for agent in agents]
        
        self.agents = [Agent(id, honesty, character, self.random, self.log, self.conf) 
                        for id, honesty, character in zip(agents, honesties, characters)]
    
    def schedule_conversations(self) -> list[Conversation]:
        self.conversations = [
            Conversation(speaker=agent, random=self.random, 
                         conf=self.conf, agents=self.agents)
            for _ in range(self.conf("n_rounds"))
            for _, agent in enumerate(self.agents)
        ]

    def play(self):
        print(f"Started simulation {self.id}")
        if self.conf("LOGGING"): self.log.initial_status(self.agents)
        results = [{i: self.agents[i].initial_state() for i in self.conf("agents")}]
        for t, c in enumerate(self.conversations):
            if self.conf("LOGGING"): self.log.time(t)
            results.append(c.run_conversation_protocol())

        if self.conf("LOGGING"): self.log.save_data_as_json()
        return results

    
    # def save_state(self):
    #     return {"id": self.id, "agents": [a._save_state().copy() for a in self.agents]}.copy()