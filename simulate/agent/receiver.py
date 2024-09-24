import numpy as np
from statistics import median
from simulate.information_theory import Info, Ift

class Receiver():
    def __init__(self, agent):
        self.a = agent

    def receive(self, topic, speaker, statement, blush):
        if topic == self.a.id:
            self.a.Updater.update_friendship(speaker, statement.mean)
        trust = self.compute_trust(topic=topic, speaker=speaker, statement=statement, blush=blush)
        self.a.Updater.update_ToM(trust=trust, speaker=speaker, topic=topic, statement=statement)
        
        Ispeaker = self.interprete_speaker(speaker=speaker, topic=topic, statement=statement)
        if speaker != topic:
            Itopic = self.interprete_topic(speaker=speaker, topic=topic, statement=statement)
            reception = {"trust": trust, "Ispeaker": Ispeaker, "Itopic": Itopic}
        reception = {"trust": trust, "Ispeaker": Ispeaker}
        
        return reception


    def compute_trust(self, topic: int, speaker: int, statement: Info, blush: bool):
        if self.a.naive: return 1
        if blush: return 0
        
        assumed_honesty = self.a.I[speaker].mean
        if self.a.listening and speaker == topic and statement.mean < assumed_honesty: return 1

        surprise_factor = self.handle_surprise(statement=statement, topic=topic)
        denominator = surprise_factor * (1 - self.a.conf("BLUSH_FREQ_LIE") * (1 - assumed_honesty))
        return assumed_honesty / (assumed_honesty + denominator)

    def handle_surprise(self, statement, topic):
        if not self.a.listening: return 1
        
        surprise = Ift.KL(statement, self.a.I[topic])
        surprise_factor = 0.5 * (surprise / self.a.kappa) ** 2
        self.a.K = (self.a.K + [surprise])[-10:]
        self.a.kappa = median(self.a.K) / np.sqrt(np.pi)
        return surprise_factor

    def interprete_topic(self, speaker, topic, statement):
        Itruth = Ift.get_info_difference(P=statement, Q=self.a.J[speaker][topic])
        Ilie = self.a.I[topic]
        return {"Itruth": Itruth, "Ilie": Ilie}
    
    def interprete_speaker(self, speaker, topic, statement):
        Itruth = self.a.I[speaker] + Info(1, 0)
        if speaker == topic:
            Itruth = statement + Info(1, 0)
        Ilie = self.a.I[speaker] + Info(0, 1)
        return {"Itruth": Itruth, "Ilie": Ilie}