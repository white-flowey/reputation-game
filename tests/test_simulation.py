import pytest

from simulate import Game
from config import init_conf

conf = init_conf()
game = Game(conf("characters_dict")[0])
game.setup_simulations()

def test_setup():
    simulation = game.simulations[0]
    assert isinstance(simulation.random, dict)
    assert len(simulation.agents) == conf("n_agents")
    assert len(simulation.conversations) == conf("n_rounds") * conf("n_agents")

def test_simulation_name():
    pass
