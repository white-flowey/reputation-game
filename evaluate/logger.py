import os
import json

from config import config
from helper import make_outfile_name

class Logger:
    def __init__(self, id):
        self.id = id
        self.data = []

    def log(self, log_type, **kwargs):
        self.data.append({"type": log_type, **kwargs})
    
    def initial_status(self, agents):
        self.log("Config", **config.conf)
        for agent in agents:
            self.log(f"Init A{agent.id}", **agent.Saver.log_state())

    def time(self, time):
        self.log("time", time=time)

    def conversation(self, honest, blush, speaker, listeners, listener_weights, topic, statement):
        self.log("conversation", id=speaker, listeners="|".join(map(str, listeners)),
                 weights=[round(w, 2) for w in listener_weights], topic=int(topic), 
                 statement=str(statement.round(2)), honest=int(honest), blush=blush)

    def self_update(self, agent, topic):
        state = agent.Saver.log_state()
        self.log("self_update_", id=agent.id, I=state["I"][agent.id], J=state["J"][agent.id][topic])

    def update(self, agent, speaker, topic, update):
        state = agent.Saver.log_state()
        conv_data = {
            "id": agent.id, "topic": int(topic), "trust": round(update["trust"], 2), 
            "Itruth_s": str(update["Ispeaker"]["Itruth"].round(2)),
            "Ilie_s": str(update["Ispeaker"]["Ilie"].round(2)),
            "update_speaker": state["I"][speaker], 
            "update_topic": state["I"][topic], 
            "J": state["J"][speaker][topic], "C": state["C"][speaker][topic], 
            "friendship": state["friendships"][speaker], 
            "kappa": state["kappa"], "K": state["K"]
        }
        if "Itopic" in update:
            conv_data.update({
                "Itruth_t": str(update["Itopic"]["Itruth"].round(2)), 
                "Ilie_t": str(update["Itopic"]["Ilie"].round(2))
            })
        self.log("conv_update_", **conv_data)

    def save_data_as_json(self, characters_setup):
        directory = os.path.join(os.getcwd(), 'evaluate/results/logs')
        os.makedirs(directory, exist_ok=True)
        outfile = make_outfile_name(characters_setup)
        file_path = os.path.join(directory, f'{os.path.basename(outfile)}_{self.id}.json')
        
        with open(file_path, 'w') as file:
            for obj in self.data:
                json.dump(obj, file)
                file.write("\n")
