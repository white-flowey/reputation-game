from .agent import Agent

class Conversation:
    """
    Represents a conversation between agents, managing the dialogue and interactions.

    Attributes:
        conf (any): Configuration settings for the conversation. Passed as arg to avoid loading again.
        speaker (Agent): The agent initiating the conversation.
        random (dict): Random values for managing conversation dynamics.
        agents (list[Agent]): List of all agents participating in the conversation.
        setting (str): The type of conversation setting (e.g., one-to-one).
        listeners (dict): Selected listeners for the conversation.
        topic (str): The topic of conversation.
    """

    def __init__(self, conf: any, speaker: Agent, random: dict, agents: list[Agent]):
        """
        Initializes the conversation with configuration, speaker, random values, and agents.

        Args:
            conf (any): Configuration settings for the conversation.
            speaker (Agent): The agent initiating the conversation.
            random (dict): Randomized values for conversation dynamics.
            agents (list[Agent]): List of agents involved in the conversation.
        """
        self.conf = conf
        self.speaker = speaker
        self.random = random
        self.agents = agents

    def run_conversation_protocol(self):
        """
        Executes the conversation protocol, managing message exchanges between agents (sending, receiving, updating).

        Returns:
            dict: The attributes of all participating agents that changed during the simulation.
        """
        self.initiate_conversation()

        message = self.speaker.Sender.talk(self.listeners, self.topic)        
        listeners = [self.agents[i] for i in self.listeners["ids"]]
        for listener in listeners:
            reception = listener.Receiver.receive(topic=self.topic, speaker=self.speaker.id, 
                                                  statement=message["statement"], blush=message["blushes"])
            [listener.Updater.add_to_buffer(reception) for listener in listeners]

        if self.setting == "one_to_one":
            response = listeners[0].Sender.talk({"ids": [self.speaker.id], "weights": [1]}, self.topic)
            reception = self.speaker.Receiver.receive(topic=self.topic, speaker=listeners[0].id, 
                                                      statement=response["statement"], blush=response["blushes"])
            self.speaker.Updater.add_to_buffer(reception)
            self.speaker.Updater.update(self.topic, listeners[0].id)
            
        [agent.Updater.update(self.topic, self.speaker.id) for agent in listeners]

        return self.save_state()

    def initiate_conversation(self):
        """Initializes the conversation by selecting its setting, listeners, and topic."""
        self.setting = self.pick_setting()
        self.listeners = self.pick_listeners()
        self.topic = self.pick_topic()

    def pick_setting(self):
        """Selects the conversation setting based on the speaker's preferences."""
        return self.speaker.Initiator.pick_setting()
        
    def pick_listeners(self):
        """Chooses the listeners for the conversation based on the selected setting."""
        return self.speaker.Initiator.pick_listeners(self.setting)

    def pick_topic(self):
        """Selects the topic of conversation based on the speaker's preferences."""
        return self.speaker.Initiator.pick_topic()
    
    def save_state(self):
        """
        Saves the state of the conversation based on the current setting.

        Returns:
            dict: A dictionary containing the attributes of all participating agents that changed during the simulation.
        """
        if self.setting == "one_to_one":
            listener = self.agents[self.listeners["ids"][0]]
            return {
                self.speaker.id: self.speaker.Saver.save_state(self.topic, self.listeners["ids"], self.setting),
                listener.id: listener.Saver.save_state(self.topic, [self.speaker.id], self.setting)
            }
