import os

from config import init_conf
from .simulation import Simulation

class Game():
    def __init__(self, seed=None, characters_setup=None):
        self.conf = init_conf()
        self.characters_setup = characters_setup if characters_setup else self.conf("characters_dict")[0]
        self.setup_simulations(seed)
        self.outfile = self.make_outfile_name()
    
    def make_outfile_name(self):
        return os.path.join(self.conf("folder"), "simulation", self.simulations[0].name) + "_sim.json"

    def setup_simulations(self, seed=None):
        if seed:
            self.simulations = [Simulation(seed, self.characters_setup)]
        else:
            self.simulations = [Simulation(seed, self.characters_setup) for seed in range(self.conf("n_stat"))]
    
    def play(self, simulation):
        print(f"Started simulation {simulation.id}")
        if self.conf("LOGGING"): simulation.log.initial_status(simulation.agents)

        rounds = [{"time": 0, "speaker": 0, "state": simulation.save_state().copy()}]
        for round in range(self.conf("n_rounds")):
            for i, agent in enumerate(simulation.agents):
                time = round * 3 + i + 1
                rounds.append({"time": time, "speaker": agent.id, "state": self.conversation(agent, simulation, time).save_state().copy()})
        
        if self.conf("LOGGING"): simulation.log.save_data_as_json()
        return rounds
    
    def conversation(self, speaker, simulation, time):
        if self.conf("LOGGING"): simulation.log.time(time)

        one_to_one = self.conf("p_one_to_one") > simulation.random_dict["n_recipients"].uniform()

        listener_weights = speaker.rank_communication_partners()
        topic = speaker.draw_topic(simulation.agents)
        
        if one_to_one:
            listeners = [simulation.agents[speaker.draw_max_from_list(listener_weights, "recipients")]]
            message = speaker.talk(topic, listeners)
            listeners[0].buffer.append(message)
            
            response = listeners[0].talk(topic, speaker)
            speaker.buffer.append(response)

            [a.update_from_buffer() for a in [speaker, listeners[0]]]
        else: # Broadcast
            listeners = [a for a in simulation.agents if a.id != speaker.id]
            message = speaker.talk(topic, listeners, listener_weights)
            [listener.buffer.append(message) for listener in listeners]
            
            [a.update_from_buffer() for a in listeners]
    
        return simulation