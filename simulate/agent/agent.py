import numpy as np
from statistics import median

from config import conf
from helper import character_mapping
from simulate.information_theory import Info
from . import Initiator, Sender, Receiver, Updater, StateSaver

agents = conf("agents")

class Agent:
    """
    Represents an agent in the simulation with defined characteristics and memory.
    """

    def __init__(self, id: int, honesty: float, character: str, random_dict: dict, log: any, conf: dict) -> None:
        """Initializes an agent with specified attributes and sets up its character and memory.

        Args:
            id (int): Unique identifier for the agent.
            honesty (float): Fixed honesty level of the agent.
            character (str): Character traits of the agent.
            random_dict (dict): Random number generator dict.
            log (Logger): Logger instance for recording events.
            conf (dict): Configuration settings for the simulation.
        """
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
        self.Saver = StateSaver(self)

    def setup_character(self, character: str) -> None:
        """Sets up the agent's character attributes based on the provided character mapping e.g., self.deceptive."

        Args:
            character (str): Character traits of the agent.
        """
        for key, value in character_mapping(character).items():
            setattr(self, key, value)

    def setup_memory(self) -> None:
        """Initializes the agent's memory structures for friendships and information states."""
        n_agents = self.conf("n_agents")
        self.friendships = [Info(1, 0) if i == self.id else Info(0, 0) for i in agents]
        self.I = [Info(0, 0)] * n_agents
        self.Iothers = [[Info(0, 0)] * n_agents for _ in range(n_agents)]  # Changed to avoid reference issue
        self.J = [[Info(0, 0)] * n_agents for _ in range(n_agents)]  # Changed to avoid reference issue
        self.C = [[Info(0, 0)] * n_agents for _ in range(n_agents)]  # Changed to avoid reference issue
        self.K = [np.sqrt(np.pi)] * self.conf("KLENGTH")
        self.kappa = 1
        self.n_conversations = [{"partner": 0, "topic": 0} for _ in range(n_agents)]  # Changed to avoid reference issue

    def initialise_memory(self) -> None:
        """Initializes the agent's memory with predefined values from the configuration."""
        if self.conf("mindI"):
            self.I = [Info(self.conf("mindI")[b][0], self.conf("mindI")[b][1]) for b in agents]
        self.K = self.conf("Ks")[self.id] if self.conf("Ks") else [np.sqrt(np.pi) for _ in range(self.conf("KLENGTH"))]
        self.kappa = median(self.K) / np.sqrt(np.pi) if self.conf("Ks") else 1
