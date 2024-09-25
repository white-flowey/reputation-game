from config import conf

def create_select_for_plotter(data: dict, times: int) -> dict:
    """Create a selection dictionary for plotting data. In the plotter, directly select key via dropdown.

    Args:
        data (dict): A dictionary containing time series data for agents.
        times (int): Number of conversations in the simulation

    Returns:
        dict: A dictionary with selections for plotting, including honesties, kappa,
              interactions, friendships, and last statements between agents.
    """
    select = {"time": list(range(times))}
    for a in conf("agents"):
        select[f"Honesty A{a}"] = data[a]["honesty"]
        select[f"Kappa A{a}"] = data[a]["kappa"]
        for b in conf("agents"):
            select[f"A{a} on A{b}"] = data[a]["I"][b]
            select[f"Friendship A{a}-A{b}"] = data[a]["friendships"][b]
            for c in conf("agents"):
                select[f"A{b} said last to A{a} about A{c}"] = data[a]["J"][b][c]
    return select
