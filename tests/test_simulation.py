import pytest

from simulate import Game, Simulation, Agent
from config import init_conf

game = Game()
game.setup_simulations()

def test_setup():
    conf = init_conf()
    simulation = game.simulations[0]
    assert isinstance(simulation.random_dict, dict)
    assert len(simulation.agents) == conf("n_agents")

def test_simulation_name():
    pass
