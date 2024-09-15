import os
import json
import numpy as np

from config import conf

class Postprocessor():
    def __init__(self, filename):
        self.raw = self.load_results(filename)
        self.results = self.raw[0] if len(self.raw) == 1 else self.statistics(self.raw)
        self.data = {}
        
        self.get_time()
        self.get_data(conf("n_stat") > 1)
        self.save_data_as_json()

    def load_results(self, filename):
        with open(filename, "r") as json_file:
            return json.load(json_file)

    def statistics(self, results):
        mean_results = []
        for t in range(conf("n_rounds")):
            mean_time_step = {"state": {"agents": []}}
            for a in conf("agents"):
                a_b_I = [np.mean([float(results[sim][t]["state"]["agents"][a]["I"][a][b]) for sim in range(conf("n_stat"))]) for b in conf("agents")]
                a_b_J = [np.mean([float(results[sim][t]["state"]["agents"][a]["J"][a][b]) for sim in range(conf("n_stat"))]) for b in conf("agents")]
                a_b_C = [np.mean([float(results[sim][t]["state"]["agents"][a]["C"][a][b]) for sim in range(conf("n_stat"))]) for b in conf("agents")]
                a_b_friends = [np.mean([float(results[sim][t]["state"]["agents"][a]["friendships"][b]) for sim in range(conf("n_stat"))]) for b in conf("agents")]
                
                a_kappa = np.mean([float(results[sim][t]["state"]["agents"][a]["kappa"]) for sim in range(conf("n_stat"))])
                a_honesty = results[0][0]["state"]["agents"][a]["honesty"]
                mean_time_step["state"]["agents"].append({"I": a_b_I, "J": a_b_J, "C": a_b_C, "friendships": a_b_friends, "kappa": a_kappa, "honesty": a_honesty})
            
            mean_results.append(mean_time_step)
        return mean_results

    def get_time(self):
        self.data["time"] = list(range(len(self.results)))

    def get_data(self, statistics=False):
        for a in conf("agents"):
            self.data[f"Kappa A{a}"] = []
            self.data[f"Honesty A{a}"] = []
            for b in conf("agents"):
                self.data[f"A{a} on A{b}"] = []
                self.data[f"Friendship A{a}-A{b}"] = []
                self.data[f"A{b} said last to A{a}"] = []
                self.data[f"A{b} wants A{a} to believe"] = []

        for t in self.results:
            for a in conf("agents"):
                for b in conf("agents"):
                    if statistics:
                        self.data[f"A{a} on A{b}"].append(float(t["state"]["agents"][a]["I"][b]))
                        self.data[f"A{b} said last to A{a}"].append(float(t["state"]["agents"][a]["J"][b]))
                        self.data[f"A{b} wants A{a} to believe"].append(float(t["state"]["agents"][a]["C"][b]))
                    else:
                        self.data[f"A{a} on A{b}"].append(float(t["state"]["agents"][a]["I"][a][b]))
                        self.data[f"A{b} said last to A{a}"].append(float(t["state"]["agents"][a]["J"][a][b]))
                        self.data[f"A{b} wants A{a} to believe"].append(float(t["state"]["agents"][a]["C"][a][b]))
                    self.data[f"Friendship A{a}-A{b}"].append(float(t["state"]["agents"][a]["friendships"][b]))
                self.data[f"Kappa A{a}"].append(float(t["state"]["agents"][a]["kappa"]))
                self.data[f"Honesty A{a}"].append(float(t["state"]["agents"][a]["honesty"]))
                
    def build_result_file_names(self):
        basis_mode = conf("characters_dict").get("all")
        all_modes = list(conf("characters_dict").values())

        if basis_mode in all_modes:
            all_modes.remove(basis_mode)

        if not all_modes or all([m == basis_mode for m in all_modes]):
            self.title = f"{basis_mode} agents"
        elif len(all_modes) == self.n_agents:
            self.title = ",".join(all_modes) + " agents"
        elif len(all_modes) == self.n_agents - 1:
            self.title = ",".join(all_modes) + f" among {basis_mode} agent"
        else:
            self.title = ",".join(all_modes) + f" among {basis_mode} agents"

        self.outfile = os.path.join(conf("folder") + self.name)
    
    def save_data_as_json(self):
        file_path = os.path.join(conf("folder"), "processor", self.raw[0][0]["state"]["name"]) + ".json"
        os.makedirs(conf("folder"), exist_ok=True)

        with open(file_path, 'w') as json_file:
            json.dump(self.data, json_file, indent=4)