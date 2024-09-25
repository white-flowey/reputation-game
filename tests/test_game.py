import pytest

from simulate import Game, Simulation
from config import conf

game = Game(conf("characters_dict")[0])
game.setup_simulations()

def test_setup():
    assert len(game.simulations) == conf("n_stat")
    for simulation in game.simulations:
        assert isinstance(simulation, Simulation)
