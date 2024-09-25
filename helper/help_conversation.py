def draw_max_from_list(random: dict, list: list, type: str):
    """Draws a random index of the maximum value from a list. Used for drawing a single topic or listener.

    Args:
        random (dict): A random number generator.
        list (list): A list of numerical values from which to find the maximum.
        type (str): A key from the simulation's random dict (e.g., "topic").

    Returns:
        int: The index of the maximum value in the list. If there are multiple maximum values,
        a random index among them is returned.
    """
    max_value = max(list)
    max_indices = [index for index, value in enumerate(list) if value == max_value]
    if len(max_indices) > 1:
        return random[type].choice(max_indices)
    return max_indices[0]