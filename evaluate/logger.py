import os
import json

from config import config

class Logger():
    def __init__(self, id):
        self.id = id
        self.data = []
        
    def initial_status(self, agents):
        self.data.append({"type": "Config", **config.conf})
        for a in agents:
            self.data.append({"type": f"Init A{a.id}", **a._save_state(log=True)})
    
    def time(self, time):
        self.data.append({"time": time})

    def conversation(self, honest, blush, speaker, listeners, listener_weights, topic, statement):
        self.data.append({"type": "conversation", "id": speaker, "listeners": "|".join(str(l) for l in listeners), 
                          "weights": [round(w, 2) for w in listener_weights], "topic": int(topic), 
                          "statement": str(statement.round(2)), "honest": honest, "blush": blush})
    
    def self_update(self, agent, topic):
        obj = agent._save_state(log=True)
        self.data.append({"type": "self_update_", "id": agent.id, "I": obj["I"][agent.id], "J": obj["J"][agent.id][topic]})
    
    def update(self, agent, speaker, topic, update):
        obj = agent._save_state(log=True)
        if "Itopic" in update:
            self.data.append({"type": "conv_update_", "id": agent.id, "topic": int(topic), "trust": round(update["trust"], 2), 
                            "Itruth_s": str(update["Ispeaker"]["Itruth"].round(2)), "Ilie_s": str(update["Ispeaker"]["Ilie"].round(2)), 
                            "Itruth_t": str(update["Itopic"]["Itruth"].round(2)), "Ilie_t": str(update["Itopic"]["Ilie"].round(2)), 
                            "update_speaker": obj["I"][speaker], "update_topic": obj["I"][topic],
                            "J": obj["J"][speaker][topic], "C": obj["C"][speaker][topic],
                            "friendship": obj["friendships"][speaker], "kappa": obj["kappa"], "K": obj["K"]})
        else:
            self.data.append({"type": "conv_update_", "id": agent.id, "topic": int(topic), "trust": round(update["trust"], 2), 
                            "Itruth_s": str(update["Ispeaker"]["Itruth"].round(2)), "Ilie_s": str(update["Ispeaker"]["Ilie"].round(2)), 
                            "update_speaker": obj["I"][speaker], "update_topic": obj["I"][topic],
                            "J": obj["J"][speaker][topic], "C": obj["C"][speaker][topic],
                            "friendship": obj["friendships"][speaker], "kappa": obj["kappa"], "K": obj["K"]})

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
        