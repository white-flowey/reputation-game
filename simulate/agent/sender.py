from scipy.optimize import root

from simulate.information_theory import Ift, Info


class Sender():
    def __init__(self, agent):
        self.a = agent

    def talk(self, listeners: dict[list], topic: int):
        if honest := self.tells_truth_now():
            statement = self.a.I[topic]
            message = {"statement": statement, "blushes": False}
        else:
            assumed_opinion = self.assume_others_opinion(listeners, topic)
            max_lie = self.get_maximum_lie_size(topic, assumed_opinion)
            lie = self.choose_lie_method(topic, max_lie)
            statement = assumed_opinion + lie
            message = {"statement": statement, "blushes": self.blushes()}
        
        if self.a.conf("LOGGING"): self.a.log.conversation(honest, message["blushes"], self.a.id, listeners["ids"], listeners["weights"], topic, statement)
        self.a.Updater.awareness(honest, topic, statement)
        return message
    
    def tells_truth_now(self) -> bool:
        return self.a.random["honests"].uniform() <= self.a.honesty
    
    def assume_others_opinion(self, listeners: dict[list], topic: int) -> Info:
        if len(listeners["ids"]) > 1:
            opinions_on_topic = [self.a.Iothers[b][topic] for b in listeners["ids"]]
            return Ift.make_average_opinion(listeners["weights"], opinions_on_topic)
        return self.a.Iothers[listeners["ids"][0]][topic]

    def get_maximum_lie_size(self, topic, assumed_opinion):

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

    def choose_lie_method(self, topic, lie):
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
                if friendship == 0.5: lie = Info(0, 0)
                else: lie = Info((friendship > 0.5) * lie, (friendship < 0.5) * lie)

        return lie
    
    def blushes(self) -> bool:
        return self.a.conf("BLUSH_FREQ_LIE") > (self.a.random["blush"].uniform() + self.a.shameless)


    # def count_conversations(self, speaker, topic):
    #     self.n_conversations[speaker]["partner"] += 1
    #     self.n_conversations[topic]["topic"] += 1
    