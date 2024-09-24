import os
from timeit import default_timer as timer
from helper import launch_parallel
from .simulation import Simulation
from config import init_conf
from helper import make_outfile_name, save_data_as_json
from evaluate import Postprocessor

class Game:
    def __init__(self, characters_setup: dict):
        self.conf = init_conf()
        self.characters_setup = characters_setup
        self.outfile_name = make_outfile_name(characters_setup)
        self.setup_simulations()

    def setup_simulations(self) -> None:
        self.simulations = [Simulation(seed, self.characters_setup, self.conf) for seed in range(self.conf("n_stat"))]

    def run(self, override: bool) -> None:
        start_time = timer()

        if not os.path.exists(self.outfile_name) or override:
            if len(self.simulations) == 1:
                results = [self.simulations[0].play()]
            else:
                results = launch_parallel(self.simulations, play)
            print(f"Time elapsed: {round(timer() - start_time, 3)}s")
            self.output(results, self.outfile_name)
        else:
            print("Simulation is already in processor folder.")

    def output(self, results: list, filename: str) -> None:
        start = timer()
        save_data_as_json(results, filename)
        print(f"Saving time: {round(timer() - start, 2)}s")
        
        start = timer()
        Postprocessor(filename)
        print(f"Processing time: {round(timer() - start, 2)}s")


def play(sim): return sim.play()