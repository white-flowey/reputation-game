from simulate import Game
from simulate.information_theory import Info
from config import init_conf

conf = init_conf()
game = Game(conf("characters_dict")[0])
game.setup_simulations()
agent = game.simulations[0].agents[0]

def test_updater_awareness():
    self_info = Info(32, 5)
    statement = Info(10, 3)

    agent.I[agent.id] = self_info
    agent.Updater.awareness(False, 1, statement)
    update = agent.I[agent.id]
    assert update.mu == self_info.mu and update.la == self_info.la + 1

    agent.Updater.awareness(True, 0, statement)
    update = agent.I[agent.id]
    assert update.mu == self_info.mu + 1 and update.la == self_info.la + 1