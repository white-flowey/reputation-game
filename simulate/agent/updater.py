from statistics import median
from simulate.information_theory import Ift, Info

class Updater():
    """Handles updating the mind attributes of the associated agent."""
    def __init__(self, agent, log):
        """Initializes the Updater with a reference to the associated agent and log.

        Args:
            agent: The agent that this updater belongs to.
            log: The logging system used to record updates.
        """
        self.a = agent
        self.log = log
        self.buffer = []

    def awareness(self, honest: bool, topic: int, statement: Info) -> None:
        """Updates the agent's awareness of a topic based on the received statement.

        Args:
            honest (bool): Indicates if the speaker is honest.
            topic (int): The topic being discussed.
            statement (Info): The statement made by the speaker.
        """
        self.a.J[self.a.id][topic] = statement
        self.a.I[self.a.id] += Info(honest, not honest)

        if topic == self.a.id and self.a.conf("ACTIVE_SELF_FRIENDSHIP"):
            friendship = statement.mean - median([self.a.J[i][self.a.id] for i in self.a.conf("agents") if i != self.a.id])
            self.a.friendships[self.a.id] = self.a.friendships[self.a.id] + Info(friendship > 0, friendship < 0)

        if self.a.conf("LOGGING"): 
            self.log.self_update(self.a, topic)

    def add_to_buffer(self, obj) -> None:
        """Adds an object to the internal buffer for later processing."""
        self.buffer.append(obj)

    def update(self, topic: int, speaker: int) -> None:
        """Updates the beliefs of the agent based on buffered information.

        Args:
            topic (int): The topic being discussed.
            speaker (int): The speaker providing information.
        """
        update = self.buffer.pop(0)
        if "Itopic" in update: ### if competence: trust=update["trust"] * update["competence"]
            self.a.I[topic] = Ift.match(trust=update["trust"], Itruth=update["Itopic"]["Itruth"], 
                                        Ilie=update["Itopic"]["Ilie"], Istart=self.a.I[topic])
        
        self.a.I[speaker] = Ift.match(trust=update["trust"], Itruth=update["Ispeaker"]["Itruth"], 
                                      Ilie=update["Ispeaker"]["Ilie"], Istart=self.a.I[speaker])
        
        if self.a.conf("LOGGING"): self.log.update(self.a, speaker, topic, update)

    def update_friendship(self, speaker: int, statement: float) -> None:
        """Updates the friendship value between the agent and another speaker.

        Args:
            speaker (int): The ID of the speaker whose friendship value is being updated.
            statement (float): The statement (Beta.mean) made by the speaker used to evaluate the update.
        """
        x_median = median([self.a.J[b][self.a.id].mean for b in self.a.conf("agents") if b not in (self.a.id, speaker)])
        update = Info(1, 0) if statement > x_median else Info(0, 1) if statement < x_median else self.a.friendships[speaker]
        self.a.friendships[speaker] = self.a.friendships[speaker] + update if self.a.conf("CONTINUOUS_FRIENDSHIP") else update

    def update_ToM(self, trust: float, speaker: int, topic: int, statement: Info) -> None:
        """Updates the Theory of Mind (ToM) for the speaker based on trust and the statement.

        Args:
            trust (float): The level of trust in the speaker's statement.
            speaker (int): The ID of the speaker.
            topic (int): The topic being discussed.
            statement (Info): The statement made by the speaker.
        """
        self.a.Iothers[speaker][topic] = statement * trust + self.a.Iothers[speaker][topic] * (1 - trust)
        self.a.J[speaker][topic] = statement
        self.a.C[speaker][topic] = statement * (1 - trust) + self.a.C[speaker][topic] * trust
