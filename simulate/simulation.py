import numpy as np

from helper import make_random_dict
from .information_theory import Info
from .agent import Agent
from .conversation import Conversation
from evaluate import Logger

class Simulation:
    """
    Manages the simulation process, including agent initialization, conversation scheduling, and running the simulation.

    Attributes:
        conf (dict): Simulation configuration settings.
        random (dict): Randomized values generated using the seed.
        characters_setup (dict): Dictionary specifying character traits for agents.
        id (int): The unique identifier for this simulation (seed).
        log (Logger): Logger for tracking simulation data.
        agents (list): List of initialized `Agent` objects.
        conversations (list): List of scheduled `Conversation` objects.
    """

    def __init__(self, seed: int, characters_setup: dict, conf: dict):
        """
        Initializes the simulation with the given seed, character setup, and configuration.

        Args:
            seed (int): Seed for random number generation. Also used as simulation id.
            characters_setup (dict): Dictionary specifying agent characters.
            conf (dict): Simulation configuration settings. Passed as arg to avoid loading again.
        """
        self.conf = conf
        self.random = make_random_dict(seed)
        self.characters_setup = characters_setup
        self.id = seed
        self.log = Logger(seed)

        self.init_agents()
        self.schedule_conversations()

    def init_agents(self):
        """
        Initializes agents for the simulation based on the configuration and character setup.
        
        Agents are assigned honesty levels and characters either from the setup or randomly.
        The random dict is simulation-specific, thus passed onto the simulation's agents.
        """
        agents = self.conf("agents")
        honesties = (self.conf("honesties_dict") or 
                    sorted([Info(0, 0).draw() for _ in agents]) if self.conf("RANDOM_HONESTIES") 
                    else np.linspace(0, 1, self.conf("n_agents")))
        characters = [self.characters_setup.get(str(agent), self.characters_setup["all"]) for agent in agents]
        
        self.agents = [Agent(id, honesties[id], character, self.random, self.log, self.conf) 
                        for id, character in zip(agents, characters)]
    
    def schedule_conversations(self) -> list[Conversation]:
        """
        Schedules conversations for the agents based on the configuration.

        Returns:
            list[Conversation]: A list of `Conversation` objects scheduled for the simulation.
        """
        self.conversations = [
            Conversation(speaker=agent, random=self.random, 
                         conf=self.conf, agents=self.agents)
            for _ in range(self.conf("n_rounds"))
            for _, agent in enumerate(self.agents)
        ]

    def play(self) -> list[dict]:
        """
        Runs the simulation by processing each conversation round and logging the results.

        Returns:
            list[dict]: A list of results containing initial states and outcomes of each conversation.
        """
        print(f"Started simulation {self.id}")
        if self.conf("LOGGING"): self.log.initial_status(self.agents)
        
        results = [{i: self.agents[i].Saver.initial_state() for i in self.conf("agents")}]
        for t, c in enumerate(self.conversations):
            if self.conf("LOGGING"): self.log.time(t)
            results.append(c.run_conversation_protocol())

        if self.conf("LOGGING"): self.log.save_data_as_json(self.characters_setup)
        return results
