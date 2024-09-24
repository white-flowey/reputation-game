from timeit import default_timer as timer
import json
import numpy as np

from config import conf

class Postprocessor():
    def __init__(self, filename):
        self.data = self.load_results(filename)
        self.data = [self.make_time_series_data(result) for result in self.data]
        self.data = self.statistics(self.data)
        self.select = self.create_select_for_plotter()

    def load_results(self, filename):
        with open(filename, "r") as json_file:
            return json.load(json_file)
        
    def make_time_series_data(self, data):
        ts = self.initialise_time_series()
        ts = self.set_agent_start_values(ts, data[0])
        for a in conf("agents"):
            for t, entry in enumerate(data[1:], start=1):
                ts[a]["I"][:, t] = ts[a]["I"][:, t-1]
                ts[a]["lastK"][t] = ts[a]["lastK"][t-1]
                ts[a]["kappa"][t] = ts[a]["kappa"][t-1]
                ts[a]["friendships"][:, t] = ts[a]["friendships"][:, t-1]
                ts[a]["J"][:, :, t] = ts[a]["J"][:, :, t-1]
                if str(a) in entry.keys():
                    entry = entry[str(a)]
                    partner = entry['partner']
                    topic = entry['topic']
                
                    ts[a]["I"][a][t] = entry["Iself"]
                    ts[a]["I"][partner][t] = entry["Ipartner"]
                    ts[a]["I"][topic][t] = entry.get("Itopic", ts[a]["I"][topic][t-1])

                    ts[a]["J"][a][topic][t] = entry["Jself"]
                    ts[a]["J"][partner][topic][t] = entry["Jpartner"]

                    ts[a]["lastK"][t] = entry["lastK"]
                    ts[a]["kappa"][t] = entry["kappa"]
                    ts[a]["friendships"][partner][t] = entry.get("friendships", ts[a]["friendships"][partner][t-1])
        return ts
    
    def initialise_time_series(self):
        times, n_agents = conf("times"), conf("n_agents")
        time_series = {id: {
                "honesty": np.zeros(times),
                "I": np.zeros((n_agents, times)),
                "J": np.zeros((n_agents, n_agents, times)),
                "Iothers": np.zeros((n_agents, n_agents, times)),
                "lastK": np.zeros(times),
                "kappa": np.zeros(times),
                "friendships": np.zeros((n_agents, times))}
            for id in conf("agents") } 
        return time_series    
    
    def set_agent_start_values(self, ts, data):
        for a in conf("agents"):
            a_field = str(a)
            ts[a]["honesty"][:] = [data[a_field]["honesty"]] * conf("times")
            ts[a]["lastK"][0] = data[a_field]["lastK"]
            ts[a]["kappa"][0] = data[a_field]["kappa"]
            ts[a]["I"][:, 0] = data[a_field]["I"][:]
            ts[a]["friendships"][:, 0] = data[a_field]["friendships"][:]
            ts[a]["J"][:, :, 0] = data[a_field]["J"][:][:]
            ts[a]["Iothers"][:, :, 0] = data[a_field]["Iothers"][:][:]
        return ts
    
    def statistics(self, results):
        agg_ts = self.initialise_time_series()
        for a in conf("agents"):
            for t in range(conf("times")):
                agg_ts[a]["honesty"][t] = np.mean([result[a]["honesty"][t] for result in results])
                agg_ts[a]["lastK"][t] = np.mean([result[a]["lastK"][t] for result in results])
                agg_ts[a]["kappa"][t] = np.mean([result[a]["kappa"][t] for result in results])
                for b in conf("agents"):
                    agg_ts[a]["I"][b, t] = np.mean([result[a]["I"][b, t] for result in results], axis=0)
                    agg_ts[a]["friendships"][b, t] = np.mean([result[a]["friendships"][b, t] for result in results], axis=0)
                    for c in conf("agents"):
                        agg_ts[a]["J"][b, c, t] = np.mean([result[a]["J"][b, c, t] for result in results], axis=0)
        return agg_ts
    
    def create_select_for_plotter(self):
        select = {"time": list(range(conf("times")))}
        for a in conf("agents"):
            select[f"Honesty A{a}"] = self.data[a]["honesty"]
            select[f"Kappa A{a}"] = self.data[a]["kappa"]
            for b in conf("agents"):
                select[f"A{a} on A{b}"] = self.data[a]["I"][b]
                select[f"Friendship A{a}-A{b}"] = self.data[a]["friendships"][b]
                for c in conf("agents"):
                    select[f"A{b} said last to A{a} about A{c}"] = self.data[a]["J"][b][c]
        return select