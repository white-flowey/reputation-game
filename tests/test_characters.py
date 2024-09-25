import pytest

from simulate import Game
from simulate.information_theory import Info
from config import config_swap, init_conf

def test_characters():
    with config_swap("config/tests/config_characters.yml"):
        conf = init_conf()
        game = Game(conf("characters_dict")[0])
        game.setup_simulations()
        sim = game.simulations[0]
        agents = sim.agents

        assert get_agent_by_character(sim, "deceptive").character == "deceptive"
        assert get_agent_by_character(sim, "egocentric").egocentric == 0.5
        assert get_agent_by_character(sim, "strategic").strategic == 1
        assert get_agent_by_character(sim, "deceptive").deceptive
        assert get_agent_by_character(sim, "aggressive").aggressive == 1

        aggr_agent = get_agent_by_character(sim, "aggressive")
        set_target(aggr_agent, agents, friend=False)

def get_agent_by_character(simulation, character):
    for a in simulation.agents:
        print(a.character)
    return [a for a in simulation.agents if a.character == character][0]

def set_target(agent, agents, friend=True, character="ordinary"):
    agent.friendships = [Info(100 * friend, 100 * (not friend)) if agents[i].character == character else f for i, f in enumerate(agent.friendships)]
