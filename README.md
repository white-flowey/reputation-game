# Reputation Game V2

## Structure

0. config > creates and checks simulation config
1. main.py > creates game instances per character config
2. simulate

   1. game.py > creates n_stat Simulation objects (each with unique seed), runs each simulation, writes to JSON at the end
   2. simulation.py > initialises agents, random_dict and simulation name
   3. agent.py > handles all agent attributes and behaviour
   4. information theory
      1. info.py > contains the Info class (purely "mathematical" object)
      2. IFT.py > contains information theoretical operations (match, KL, KL_minimise etc.)

3. evaluate

   1. logger.py > writes .txt logs to evaluate/results/logs during run, exists for debugging
   2. postprocessor.py > turns JSON data from simulation into easily plottable timeseries data
   3. plotter > application for plotting
      1. main_window.py > contains and manages all plotter instances, launches evaluation application
      2. plotter.py > pulls data from JSONs in evaluate/results/processor and plots

4. tests
   1. Contains unit tests for all packages (in progress)

## How to run

1. Install dependencies
2. python3 main.py --run 1 --plot 1 (run > create new simulation data, plot > evaluate existing postprocessed data)
