import os
import json
import argparse
import multiprocessing
from timeit import default_timer as timer
from concurrent.futures import ProcessPoolExecutor

from config import conf
from simulate import Game
from evaluate import plot, Postprocessor

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process some arguments.")

    parser.add_argument('--run', type=int, help='Flag to run', default=None)
    parser.add_argument('--seed', type=int, help='Seed of simulation', default=None)
    parser.add_argument('--plot', type=int, help='Flag to plot', default=None)
    parser.add_argument('--override', type=int, help='Flag to plot', default=None)

    return parser.parse_args()
    
def run_simulations(args):
    for i, characters_setup in enumerate(conf("characters_dict")):
        game = Game(args.seed, characters_setup)
        if not os.path.exists(game.outfile) or args.override:
            start_time = timer()
            
            if len(game.simulations) == 1 or args.seed:
                results = [game.play(game.simulations[0])]
            else:
                num_parallel_jobs = multiprocessing.cpu_count() * conf("n_parallel_core_jobs")
                with ProcessPoolExecutor(max_workers=num_parallel_jobs) as executor:
                    results = list(executor.map(game.play, game.simulations))
            save_data_as_json(results, game.outfile)
            
            print(f"Sim {i} done. Time elapsed: {round(timer() - start_time)}s")
        else:
            print("Simulation is already in processor folder.")
        
        Postprocessor(game.outfile)


def save_data_as_json(data, filename):
    os.makedirs(conf("folder"), exist_ok=True)
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)


if __name__ == "__main__":
    args = parse_arguments()
    if args.run:
        run_simulations(args)
    if args.plot:
        plot()
