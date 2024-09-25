import numpy as np
from config import conf

def calculate_statistics(results: list[dict], times: int) -> dict:
    """Calculate the mean over all simulation results.

    Args:
        results (list[dict]): A list of dictionaries containing simulation results.
        times (int): Number of conversations in the simulation

    Returns:
        dict: A dictionary containing aggregated time series data for each agent.
    """
    agg_ts = initialise_time_series(times)
    for a in conf("agents"):
        for t in range(times):
            agg_ts[a]["honesty"][t] = np.mean([result[a]["honesty"][t] for result in results])
            agg_ts[a]["lastK"][t] = np.mean([result[a]["lastK"][t] for result in results])
            agg_ts[a]["kappa"][t] = np.mean([result[a]["kappa"][t] for result in results])
            for b in conf("agents"):
                agg_ts[a]["I"][b, t] = np.mean([result[a]["I"][b, t] for result in results], axis=0)
                agg_ts[a]["friendships"][b, t] = np.mean([result[a]["friendships"][b, t] for result in results], axis=0)
                for c in conf("agents"):
                    agg_ts[a]["J"][b, c, t] = np.mean([result[a]["J"][b, c, t] for result in results], axis=0)
    return agg_ts

def initialise_time_series(times: int) -> dict:
    """Initialize a time series structure for agent simulation data."""
    n_agents = conf("n_agents")
    return {
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
