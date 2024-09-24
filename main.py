from timeit import default_timer as timer
from helper import parse_arguments
from simulate import Game
from evaluate import plot, Postprocessor
from config import conf

if __name__ == "__main__":
    args = parse_arguments()
    
    if args.run:
        for characters_setup in conf("characters_dict"): 
            Game(characters_setup).run(args.override)
            
    if args.proc:
        start = timer()
        Postprocessor("evaluate/results/simulation/04_ordinary_NA=3_NR=300_NST=100_sim.json")
        print(f"Finished processing: {round(timer() - start, 2)}s")

    if args.plot:
        plot()
        
