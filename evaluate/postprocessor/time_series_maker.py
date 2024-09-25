import numpy as np
from config import conf

class TimeSeriesMaker:
    def make_time_series_data(self, data: list[dict], times: int) -> dict:
        """Create time series data for agents based on the provided (CHANGES-ONLY) conversation data.

        Args:
            data (list[dict]): A list of dictionaries containing only update data from conversations.

        Returns:
            dict: A dictionary containing the time series data for each agent.
        """
        ts = self.initialise_time_series(times)
        ts = self.set_agent_start_values(ts, data[0], times)

        for a in conf("agents"):
            ts = self.update_agent_time_series(ts, a, data)
        return ts

    def initialise_time_series(self, times: int) -> dict:
        """Initialize a time series structure for agents.

        Returns:
            dict: A dictionary initialized with zeros for each agent's time series data.
        """
        n_agents = conf("n_agents")
        time_series = {
            id: {
                "honesty": np.zeros(times),
                "I": np.zeros((n_agents, times)),
                "J": np.zeros((n_agents, n_agents, times)),
                "Iothers": np.zeros((n_agents, n_agents, times)),
                "lastK": np.zeros(times),
                "kappa": np.zeros(times),
                "friendships": np.zeros((n_agents, times)),
            }
            for id in conf("agents")
        }
        return time_series

    def set_agent_start_values(self, ts: dict, data: dict, times: int) -> dict:
        """Set initial values for agents based on the first entry of the data.

        Args:
            ts (dict): The time series data structure.
            data (dict): The first entry of the data containing agent values.

        Returns:
            dict: Updated time series data structure with initial values.
        """
        for a in conf("agents"):
            a_field = str(a)
            ts[a]["honesty"][:] = [data[a_field]["honesty"]] * times
            ts[a]["lastK"][0] = data[a_field]["lastK"]
            ts[a]["kappa"][0] = data[a_field]["kappa"]
            ts[a]["I"][:, 0] = data[a_field]["I"][:]
            ts[a]["friendships"][:, 0] = data[a_field]["friendships"][:]
            ts[a]["J"][:, :, 0] = data[a_field]["J"][:][:]
            ts[a]["Iothers"][:, :, 0] = data[a_field]["Iothers"][:][:]
        return ts

    def update_agent_time_series(self, ts: dict, a: int, data: list[dict]) -> dict:
        """Update the time series data for a specific agent. Either with the value from the previous time step
        (if they haven't interacted) or - if applicable - with the new one.

        Args:
            ts (dict): The time series data structure.
            a (int): The index of the agent to update.
            data (list[dict]): The list of data entries for the agents.

        Returns:
            dict: Updated time series data structure for the agent.
        """
        for t, entry in enumerate(data[1:], start=1):
            ts = self.carry_forward_values(ts, a, t)
            if str(a) in entry.keys():
                ts = self.update_entry_for_agent(ts, a, t, entry[str(a)])
            else:
                ts[a]["lastK"][t] = ts[a]["lastK"][t-1]
                ts[a]["kappa"][t] = ts[a]["kappa"][t-1]
        return ts

    def carry_forward_values(self, ts: dict, a: int, t: int) -> dict:
        """Carry forward values for an agent at a given time step. (using values from previous time step)

        Args:
            ts (dict): The time series data structure.
            a (int): The index of the agent.
            t (int): The current time step.

        Returns:
            dict: Updated time series data structure with carried forward values.
        """
        ts[a]["I"][:, t] = ts[a]["I"][:, t-1]
        ts[a]["friendships"][:, t] = ts[a]["friendships"][:, t-1]
        ts[a]["J"][:, :, t] = ts[a]["J"][:, :, t-1]
        return ts

    def update_entry_for_agent(self, ts: dict, agent: int, t: int, entry: dict) -> dict:
        """Update the time series entry for a specific agent at a given time step.

        Args:
            ts (dict): The time series data structure.
            agent (int): The index of the agent to update.
            t (int): The current time step.
            entry (dict): The entry containing update values for the agent.

        Returns:
            dict: Updated time series data structure with new entry values.
        """
        partner = entry['partner']
        topic = entry['topic']
        ts[agent]["I"][agent][t] = entry["Iself"]
        ts[agent]["I"][partner][t] = entry["Ipartner"]
        ts[agent]["I"][topic][t] = entry.get("Itopic", ts[agent]["I"][topic][t-1])
        ts[agent]["J"][agent][topic][t] = entry["Jself"]
        ts[agent]["J"][partner][topic][t] = entry["Jpartner"]
        ts[agent]["lastK"][t] = entry["lastK"]
        ts[agent]["kappa"][t] = entry["kappa"]
        ts[agent]["friendships"][partner][t] = entry.get("friendships", ts[agent]["friendships"][partner][t-1])
        return ts
