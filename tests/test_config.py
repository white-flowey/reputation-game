import pytest
from config import init_conf


def test_config_loader():
    conf = init_conf()
    
    int_types = ["n_agents", "n_rounds", "n_stat", "seed", "seed_offset"]
    for i in int_types:
        assert conf(i) != None
        assert isinstance(conf(i), int)

    list_types = ["mindI", "Ks"]
    for l in list_types:
        if conf(l):
            assert isinstance(conf(l), list)
            assert len(conf(l)) == conf("n_agents")

    assert isinstance(conf("characters_dict"), list)
    characters = conf("characters_dict")

    for character_setup in characters:
        if "all" in character_setup.keys():
            assert len(character_setup.keys()) <= conf("n_agents")
        else:
            assert len(character_setup.keys()) == conf("n_agents")


    

    