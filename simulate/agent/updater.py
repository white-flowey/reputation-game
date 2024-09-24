from statistics import median

from simulate.information_theory import Ift, Info

class Updater():
    def __init__(self, agent, log):
        self.a = agent
        self.log = log
        self.buffer = []

    def awareness(self, honest, topic, statement):
        self.a.J[self.a.id][topic] = statement
        self.a.I[self.a.id] += Info(honest, not honest)

        if topic == self.a.id and self.a.conf("ACTIVE_SELF_FRIENDSHIP"):
            friendship = statement.mean - median([self.a.J[i][self.a.id] for i in self.a.conf("agents") if i != self.a.id])
            self.a.friendships[self.a.id] = self.a.friendships[self.a.id] + Info(friendship > 0, friendship < 0)

        if self.a.conf("LOGGING"): self.log.self_update(self.a, topic)

    def add_to_buffer(self, obj):
        self.buffer.append(obj)

    def update(self, topic, speaker):
        update = self.buffer.pop(0)
        if "Itopic" in update:
            self.a.I[topic] = Ift.match(trust=update["trust"], Itruth=update["Itopic"]["Itruth"], 
                                        Ilie=update["Itopic"]["Ilie"], Istart=self.a.I[topic])
        
        self.a.I[speaker] = Ift.match(trust=update["trust"], Itruth=update["Ispeaker"]["Itruth"], 
                                      Ilie=update["Ispeaker"]["Ilie"], Istart=self.a.I[speaker])
        
        self.log.update(self.a, speaker, topic, update)

    def update_friendship(self, speaker: int, statement: float):
        x_median = median([self.a.J[b][self.a.id].mean for b in self.a.conf("agents") if b not in (self.a.id, speaker)])
        update = Info(1, 0) if statement > x_median else Info(0, 1) if statement < x_median else self.a.friendships[speaker]
        self.a.friendships[speaker] = self.a.friendships[speaker] + update if self.a.conf("CONTINUOUS_FRIENDSHIP") else update

    def update_ToM(self, trust, speaker, topic, statement):
        self.a.Iothers[speaker][topic] = statement * trust + self.a.Iothers[speaker][topic] * (1 - trust)
        self.a.J[speaker][topic] = statement
        self.a.C[speaker][topic] = statement * (1 - trust) + self.a.C[speaker][topic] * trust