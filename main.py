from timeit import default_timer as timer
from helper import parse_arguments
from simulate import Game
from evaluate import plot, Postprocessor
from config import conf

def main(args=None):
    """
    Main function. Runs simulations, postprocessor (benchmarking), or only plot based on terminal args. Can be combined.
    
    - Running a simulation (`-r` or `--run`)
    - Overriding an existing simulation output (`-o` or `--override`)
    - Running the postprocessor for benchmarking (`-pr` or `--proc`)
    - Plotting the results (`-p` or `--plot`)
    
    These flags can be combined to perform multiple actions in one execution.
    
    Example usage:
    ==============
    python3 main.py -r -o -p
    
    This will run the simulation, apply overrides, postprocess the results, and generate plots.
    
    Returns:
    ========
    None

    Outputs:
    ========
    The "Game" instance writes a JSON file with conversation round data to evaluate/results/simulation/
    
    plot(): Postprocessor processes this file into time series data and feeds into Plotter Tool.
    """
    args = args if args else parse_arguments()
    
    if args.run:
        for characters_setup in conf("characters_dict"):
            Game(characters_setup).run(args.override)

    if args.proc:
        start = timer()
        Postprocessor("evaluate/results/simulation/04_ordinary_NA=3_NR=500_NST=1_sim.json")
        print(f"Finished processing: {round(timer() - start, 2)}s")

    if args.plot:
        plot()

if __name__ == "__main__":
    main()
