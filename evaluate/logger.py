import os
import json

from config import config

class Logger():
    def __init__(self, id):
        self.id = id
        self.data = []
        
    # Update format: {"time": "", "type": "", "id": "", "I": [], "J": [], "friendships": [], "kappa"}
    
    def initial_status(self, agents):
        self.data.append({"type": "Config", **config.conf})
        for a in agents:
            self.data.append({"type": f"Init A{a.id}", **a.save_state(log=True)})
    
    def time(self, time):
        self.data.append({"time": time})

    def conversation(self, speaker, listeners, listener_weights, message):
        self.data.append({"type": "conversation", "id": speaker.id, "listeners": "|".join(str(l.id) for l in listeners), "weights": [round(w, 2) for w in listener_weights], 
                          "topic": message.topic, "statement": str(message.statement), "honest": message.honest, "blush": message.blush})
    
    def self_update(self, agent, topic):
        obj = agent.save_state(log=True)
        self.data.append({"type": "self_update_", "id": agent.id, "I": obj["I"][agent.id][agent.id], "J": obj["J"][agent.id][topic]})
    
    def update(self, agent, message, trust):
        obj = agent.save_state(log=True)
        # {id, topic, trust, update_s, update_t, J, C, friendship, kappa, K}
        self.data.append({"type": "conv_update_", "id": agent.id, "topic": message.topic, "trust": round(trust, 2), 
                          "update_speaker": obj["I"][agent.id][message.speaker], "update_topic": obj["I"][agent.id][message.topic],
                          "J": obj["J"][message.speaker][message.topic], "C": obj["C"][message.speaker][message.topic],
                          "friendship": obj["friendships"][message.speaker], "kappa": obj["kappa"], "K": obj["K"]})

    def save_data_as_json(self):
        directory = os.path.join(os.getcwd(), 'evaluate/results', 'logs')
        os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, f'{self.id}.json')
        with open(file_path, 'w') as _:
            pass  # Simply opening the file in 'w' mode clears it
        
        with open(file_path, 'a') as file:
            for obj in self.data:
                json.dump(obj, file)
                file.write("\n")
        