import pytest

from simulate import Game, Simulation
from config import conf

game = Game()
game.setup_simulations()

def test_setup():
    assert len(game.simulations) == conf("n_stat")
    for simulation in game.simulations:
        assert isinstance(simulation, Simulation)

def test_conversation():
    simulation = game.simulations[0]
    assert isinstance(game.conversation(simulation.agents[0], simulation), Simulation)

