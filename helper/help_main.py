import os
import json
import argparse
from config import conf

def parse_arguments():
    """
    Parse command-line arguments for the simulation script.

    Returns:
        argparse.Namespace: Parsed arguments containing flags for run, plot and override.
    """
    parser = argparse.ArgumentParser(description="Process some arguments.")
    parser.add_argument('-r', '--run', action='store_true', help='Flag to run the simulation')
    parser.add_argument('-p', '--plot', action='store_true', help='Flag to generate plots')
    parser.add_argument('-pr', '--proc', action='store_true', help='Flag to only postprocess')
    parser.add_argument('-o', '--override', action='store_true', help='Flag to override existing file with same config')
    return parser.parse_args()

def make_outfile_name(character):
    """
    Generate the output file name based on character configuration and simulation parameters.

    Args:
        character (dict): Dictionary with {agent_id: character, ...}. The key 'all' may be used as a special case.

    Returns:
        str: The complete file path where the simulation output will be saved.
    """
    ids = conf("character_ids_dict")
    characters = list(character.values())
    basis_character = character.get("all", "ordinary")

    if len(character) == 1 and "all" in character:
        name = "_".join([ids[basis_character], basis_character])
    elif "all" in character:
        name = ids[next(c for c in characters if c != basis_character)] + "+" + basis_character
    else:
        name = "mix_" + "|".join(f"{int(ids[c]):02d}" for c in sorted({*characters, basis_character}))

    suffix = f"_NA={conf('n_agents')}_NR={conf('n_rounds')}_NST={conf('n_stat')}"
    return os.path.join(conf("folder"), "simulation", name + suffix) + "_sim.json"

def save_data_as_json(data, filename):
    """
    Save simulation data as a JSON file.

    Args:
        data (dict): The data to save in JSON format.
        filename (str): The output file name for the saved JSON data.
    """
    os.makedirs(conf("folder"), exist_ok=True)
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)