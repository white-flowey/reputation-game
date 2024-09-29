import os
from timeit import default_timer as timer
from helper import launch_parallel
from .simulation import Simulation
from config import init_conf
from helper import make_outfile_name, save_data_as_json

class Game:
    """
    Manages game simulations, including setup, execution, and post-processing.

    Attributes:
        conf (dict): Simulation configuration settings.
        characters_setup (dict): Setup for characters in the simulation. 
            Format: {agent_id: character, agent_id: type, ...}
            Each key defines the character for that specific agent. 
            If "all" is a key, all agents not mentioned will get that character.
        outfile_name (str): Name of the file to store simulation results.
        simulations (list): List of `Simulation` instances.
    """

    def __init__(self, characters_setup: dict = None, write_to_file = True):
        """
        Initializes the game with character setup and configuration.

        Args:
            characters_setup (dict): Dictionary specifying agent characters.
        """
        self.conf = init_conf()
        self.characters_setup = characters_setup if characters_setup else self.conf("characters_dict")[0]
        self.write_to_file = write_to_file
        self.outfile_name = make_outfile_name(self.characters_setup)
        self.setup_simulations()

    def setup_simulations(self) -> None:
        """Prepares simulations based on config and character setup."""
        self.simulations = [Simulation(seed, self.characters_setup, self.conf) for seed in range(self.conf("n_stat"))]

    def run(self, override: bool) -> None:
        """
        Runs the simulations and passes results to output function.

        If the results file exists and override is False, skips the simulation.

        Args:
            override (bool): If True, runs simulations even if the output file exists.
        """
        start_time = timer()

        if not os.path.exists(self.outfile_name) or override:
            if len(self.simulations) == 1:
                results = [self.simulations[0].play()]
            else:
                results = launch_parallel(self.simulations, play_simulation)
            print(f"Time elapsed: {round(timer() - start_time, 3)}s")
            return self.output(results, self.outfile_name)
        else:
            print("Simulation is already in processor folder.")

    def output(self, results: list, filename: str) -> None:
        """
        Saves simulation results to a JSON file.

        Args:
            results (list): List of simulation results.
            filename (str): Filename to save the results.
        """
        if self.write_to_file:
            start = timer()
            save_data_as_json(results, filename)
            print(f"Saving time: {round(timer() - start, 2)}s")
        else:
            return results


def play_simulation(sim: Simulation) -> dict:
    """
    Plays a simulation. This is just a function for parallel processing.

    Args:
        sim (Simulation): A `Simulation` instance.

    Returns:
        dict: The result of the simulation.
    """
    return sim.play()
