from scipy.optimize import root
from simulate.information_theory import Ift, Info


class Sender():
    """Handles creating a statement about a topic, constructing a lie if needed, and blushing."""
    def __init__(self, agent):
        """Initializes the Sender with a reference to the associated agent.

        Args:
            agent: The agent that this sender belongs to.
        """
        self.a = agent

    def talk(self, listeners: dict[list], topic: int) -> dict:
        """Simulates the process of talking by sending a message to listeners.

        Args:
            listeners (dict[list]): A dictionary containing listeners' IDs and weights.
            topic (int): The topic of conversation.

        Returns:
            dict: A message containing the statement and whether the sender blushes.
        """
        [self.count_conversations(listener, topic) for listener in listeners["ids"]]
        if honest := self.tells_truth_now():
            statement = self.a.I[topic]
            message = {"statement": statement, "blushes": False}
        else:
            assumed_opinion = self.assume_others_opinion(listeners, topic)
            max_lie = self.get_maximum_lie_size(topic, assumed_opinion)
            lie = self.choose_lie_method(topic, max_lie)
            statement = assumed_opinion + lie
            message = {"statement": statement, "blushes": self.blushes()}
        
        if self.a.conf("LOGGING"): 
            self.a.log.conversation(honest, message["blushes"], self.a.id, listeners["ids"], listeners["weights"], topic, statement)
        
        self.a.Updater.awareness(honest, topic, statement)
        return message
    
    def tells_truth_now(self) -> bool:
        """Determines whether the sender is telling the truth at the current moment."""
        return self.a.random["honests"].uniform() <= self.a.honesty
    
    def assume_others_opinion(self, listeners: dict[list], topic: int) -> Info:
        """Assumes the opinions of other listeners on the given topic.

        Args:
            listeners (dict[list]): A dictionary containing listeners' IDs and weights.
            topic (int): The topic of conversation.

        Returns:
            Info: The assumed opinion of others on the topic.
        """
        if len(listeners["ids"]) > 1:
            opinions_on_topic = [self.a.Iothers[b][topic] for b in listeners["ids"]]
            return Ift.make_average_opinion(listeners["weights"], opinions_on_topic)
        return self.a.Iothers[listeners["ids"][0]][topic]

    def get_maximum_lie_size(self, topic: int, assumed_opinion: Info) -> float:
        """Calculates the maximum size of a lie that can be told based on the difference to the assumed opinion.

        Args:
            topic (int): The topic of conversation.
            assumed_opinion (Info): The assumed opinion on the topic.

        Returns:
            float: The maximum size of the lie that can be told.
        """
        def lie_tolerance() -> float:
            tolerance = self.a.random["lies"].exponential(self.a.kappa) * self.a.conf("F_CAUTION")
            if self.a.disturbing:
                return 2 * tolerance
            return tolerance
        
        def lie_size(x, friend) -> float:
            statement = assumed_opinion + Info(x ** 2, 0) if friend else assumed_opinion + Info(0, x ** 2)
            return Ift.KL(statement, assumed_opinion) - lie_tolerance()
        
        friend = self.a.friendships[topic].mean > 0.5
        return root(lie_size, [2.0], args=(friend,)).x[0] ** 2

    def choose_lie_method(self, topic: int, lie: float) -> Info:
        """Chooses the lie method based on the topic and agent character.

        Args:
            topic (int): The topic of conversation.
            lie (float): The calculated lie size.

        Returns:
            Info: The chosen method of lying based on various factors.
        """
        aggressive = self.a.aggressive > self.a.random["aggressive"].uniform()
        if self.a.id == topic:
            lie = Info(lie, 0) if aggressive else Info(0, 0)
        elif self.a.flattering and topic in lie:
            scaling_factor = (1 - self.a.I[topic].mean) if self.a.conf("SCALED_FLATTERING") else 1
            lie = Info(lie * scaling_factor, 0)
        else:
            friendship = self.a.friendships[topic].mean
            if self.a.conf("CONTINUOUS_FRIENDSHIP"):
                lie = Info(2 * (friendship - 0.5) * lie, 0) if aggressive else Info(0, 0)
            else:
                if friendship == 0.5: 
                    lie = Info(0, 0)
                else: 
                    lie = Info((friendship > 0.5) * lie, (friendship < 0.5) * lie)

        return lie
    
    def blushes(self) -> bool:
        """Determines whether the sender blushes when lying."""
        return self.a.conf("BLUSH_FREQ_LIE") > (self.a.random["blush"].uniform() + self.a.shameless)


    def count_conversations(self, partner: int, topic: int):
        """Keeping track of the times an agent has talked WITH or ABOUT someone."""
        self.a.n_conversations[partner]["partner"] += 1
        self.a.n_conversations[topic]["topic"] += 1
