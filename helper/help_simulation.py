import numpy as np
from config import conf

def make_random_dict(simulation_seed: int) -> dict:
    """
    Generate a dictionary of seeded random number generators based on the configuration and seed variation.
    Used throughout the simulation to make "random" decisions.

    Args:
        config (dict): A dictionary containing the base configuration, including a "seed" value.
        simulation_seed (int): An integer used to vary the seeds for different categories.

    Returns:
        dict: A dictionary where each key corresponds to a specific category, and each value is a seeded `RandomState` object.
    """
    fixed_seed = conf("seed")
    seed_offsets = {
        "honesties": fixed_seed,
        "varying_random_honesties": fixed_seed + simulation_seed,
        "fr_affinities": fixed_seed + simulation_seed + 1,
        "shynesses": fixed_seed + simulation_seed + 2,
        "one_to_one": fixed_seed + 10 * simulation_seed - 1,
        "n_recipients": fixed_seed + 10 * simulation_seed,
        "recipients": fixed_seed + 10 * simulation_seed + 1,
        "topic": fixed_seed + 10 * simulation_seed + 2,
        "honests": fixed_seed + 10 * simulation_seed + 3,
        "lies": fixed_seed + 10 * simulation_seed + 4,
        "blush": fixed_seed + 10 * simulation_seed + 5,
        "ego": fixed_seed + 10 * simulation_seed + 6,
        "strategic": fixed_seed + 10 * simulation_seed + 7,
        "flattering": fixed_seed + 10 * simulation_seed + 8,
        "aggressive": fixed_seed + 10 * simulation_seed + 9
    }
    
    return {key: np.random.RandomState(seed) for key, seed in seed_offsets.items()}