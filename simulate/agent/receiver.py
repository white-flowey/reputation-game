import numpy as np
from statistics import median
from simulate.information_theory import Info, Ift

class Receiver():
    """Handles receiving messages from speakers, interpreting statements,
    and updating the receiver's beliefs and friendships.
    """
    def __init__(self, agent) -> None:
        """Initializes the Receiver with a reference to the associated agent.

        Args:
            agent (Agent): The agent that this receiver belongs to.
        """
        self.a = agent

    def receive(self, topic: int, speaker: int, statement: Info, blush: bool) -> dict:
        """Processes a received statement, updates trust, and interprets the speaker and topic.

        Args:
            topic (int): The topic of conversation.
            speaker (int): The ID of the speaker.
            statement (Info): The statement received from the speaker.
            blush (bool): Indicates if the speaker is blushing.

        Returns:
            dict: A dictionary containing trust and interpreted information about the speaker and topic.
        """
        if topic == self.a.id:
            self.a.Updater.update_friendship(speaker, statement.mean)
        trust = self.compute_trust(topic=topic, speaker=speaker, statement=statement, blush=blush)
        
        Ispeaker = self.interprete_speaker(speaker=speaker, topic=topic, statement=statement)
        if speaker != topic:
            Itopic = self.interprete_topic(speaker=speaker, topic=topic, statement=statement)
            reception = {"trust": trust, "Ispeaker": Ispeaker, "Itopic": Itopic}
        else:
            reception = {"trust": trust, "Ispeaker": Ispeaker}
        
        self.a.Updater.update_ToM(trust=trust, speaker=speaker, topic=topic, statement=statement)
        return reception


    def compute_trust(self, topic: int, speaker: int, statement: 'Info', blush: bool) -> float:
        """Computes the trustworthiness of the speaker based on the received statement.

        Args:
            topic (int): The topic of conversation.
            speaker (int): The ID of the speaker.
            statement (Info): The statement received from the speaker.
            blush (bool): Indicates if the speaker is blushing.

        Returns:
            float: The computed trust value.
        """
        if self.a.naive: return 1
        if blush: return 0
        
        assumed_honesty = self.a.I[speaker].mean
        if self.a.listening and speaker == topic and statement.mean < assumed_honesty: return 1

        if self.a.conf["competence"]:  # remove surprise from denominator, only blush
            denominator = assumed_honesty + (1 - self.a.conf("BLUSH_FREQ_LIE") * (1 - assumed_honesty))
        else:
            surprise_factor = self.handle_surprise(statement=statement, topic=topic)
            denominator = surprise_factor * (1 - self.a.conf("BLUSH_FREQ_LIE") * (1 - assumed_honesty))
        return assumed_honesty / (assumed_honesty + denominator)

    def compute_competence(self, speaker: int, topic: int, statement: 'Info'):
        assumed_competence = self.a.Icomp[speaker].mean
        surprise_factor = self.handle_surprise(statement=statement, topic=topic)
        competence = assumed_competence / (assumed_competence + surprise_factor * (1 - assumed_competence))
             
        # Annahme - Ich bin kompetent

    def handle_surprise(self, statement: Info, topic: int) -> float:
        """Calculates the surprise factor based on the received statement and topic.

        Args:
            statement (Info): The statement received from the speaker.
            topic (int): The topic of conversation.

        Returns:
            float: The computed surprise factor.
        """
        if not self.a.listening or self.a.uncritical: return 1
        
        surprise = Ift.KL(statement, self.a.I[topic])
        surprise_factor = 0.5 * (surprise / (self.a.kappa + 1e-6)) ** 2
        self.a.K = (self.a.K + [surprise])[-10:]
        self.a.kappa = median(self.a.K) / np.sqrt(np.pi)
        return surprise_factor

    def interprete_topic(self, speaker: int, topic: int, statement: 'Info') -> dict:
        """Interprets the information about the topic based on the statement.

        Args:
            speaker (int): The ID of the speaker.
            topic (int): The topic of conversation.
            statement (Info): The statement received from the speaker.

        Returns:
            dict: A dictionary containing the interpreted information about truth and lies.
        """
        Inew = Ift.get_info_difference(P=statement, Q=self.a.Iothers[speaker][topic])
        Itruth = Inew + self.a.I[topic]
        Ilie = self.a.I[topic]
        return {"Itruth": Itruth, "Ilie": Ilie}
    
    def interprete_speaker(self, speaker: int, topic: int, statement: 'Info') -> dict:
        """Interprets the information about the speaker based on the statement.

        Args:
            speaker (int): The ID of the speaker.
            topic (int): The topic of conversation.
            statement (Info): The statement received from the speaker.

        Returns:
            dict: A dictionary containing the interpreted information about the speaker's truth and lies.
        """
        Itruth = self.a.I[speaker] + Info(1, 0)
        if speaker == topic:
            Inew = Ift.get_info_difference(P=statement, Q=self.a.Iothers[speaker][topic])
            Itruth = statement + Info(1, 0) + Inew
        Ilie = self.a.I[speaker] + Info(0, 1)
        return {"Itruth": Itruth, "Ilie": Ilie}