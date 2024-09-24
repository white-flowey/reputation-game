from .agent import Agent

class Conversation():
    def __init__(self, conf: any, speaker: Agent, random: dict, agents: list[Agent]):
        self.conf = conf
        self.speaker = speaker
        self.random = random
        self.agents = agents
    
    def run_conversation_protocol(self):
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
        self.setting = self.pick_setting()
        self.listeners = self.pick_listeners()
        self.topic = self.pick_topic()

    def pick_setting(self):
        return self.speaker.Initiator.pick_setting()
        
    def pick_listeners(self):
        return self.speaker.Initiator.pick_listeners(self.setting)

    def pick_topic(self):
        return self.speaker.Initiator.pick_topic()
    
    def save_state(self):
        if self.setting == "one_to_one":
            listener = self.agents[self.listeners["ids"][0]]
            return {
                self.speaker.id: self.speaker.save_state(self.topic, self.listeners["ids"], self.setting),
                listener.id: listener.save_state(self.topic, [self.speaker.id], self.setting)
            }
        return {}
        