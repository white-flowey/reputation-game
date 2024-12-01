def set_mind(agent, other_attrs=None) -> None:
    """Sets the attributes of the agent based on the provided dictionary.

    Args:
        other_attrs (dict, optional): A dictionary of attribute names and values to set.
            If None, no attributes are set. Defaults to None.
    """
    if other_attrs:
        for key, value in other_attrs.items():
            setattr(agent, key, value)

def character_mapping(character: str) -> dict:
    """Maps a character type to its corresponding attributes.

    Args:
        character (str): The character type to map.

    Returns:
        dict: A dictionary containing the attributes associated with the specified character type or defaults.
    """
    default = {
        "aggressive": 0, "strategic": 0, "deceptive": False, "listening": True,
        "shyness": 1, "shameless": 0, "disturbing": False, "flattering": False,
        "naive": False, "uncritical": False, "egocentric": False
    }

    character_setup_dict = {
        "deaf": {"listening": False}, 
        "naive": {"naive": True},
        "uncritical": {"uncritical": True}, 
        "ordinary": {},
        "strategic": {"strategic": 1}, 
        "egocentric": {"egocentric": 0.5},
        "deceptive": {"deceptive": True, "honesty": 0}, 
        "flattering": {"flattering": 1},
        "aggressive": {"aggressive": 1}, 
        "shameless": {"shameless": True},
        "smart": {"deceptive": True}, 
        "clever": {"deceptive": True, "honesty": 0},
        "honest": {"honest": True, "x": 1}, 
        "manipulative": {"deceptive": True, "strategic": -1, "flattering": 1, "honesty": 0},
        "dominant": {"deceptive": True, "strategic": 1, "egocentric": 0.5, "honesty": 0},
        "destructive": {"deceptive": True, "strategic": 1, "aggressive": 1, "shameless": 1},
        "good": {"strategic": 1, "honest": True, "x": 1}, 
        "disturbing": {"disturbing": True},
        "antistrategic": {"strategic": -0.5},
        "villager_1": {"honesty": 0.9},
        "villager_2": {"honesty": 0.9},

    }

    result = {**default, **character_setup_dict.get(character, {})}
    return result
