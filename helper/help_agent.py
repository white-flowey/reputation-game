def set_mind(self, mind_model, other_attrs=None):
    if other_attrs:
        for key, value in other_attrs.items():
            setattr(self, key, value)

def character_mapping(character):
    default = {
        "aggressive": 0, "strategic": 0, "deceptive": False, "listening": True,
        "shyness": 1, "shameless": 0, "disturbing": False, "flattering": False,
        "naive": False, "uncritical": False
    }

    character_setup_dict = {
        "deaf": {"listening": False}, "naive": {"naive": True},
        "uncritical": {"uncritical": True}, "ordinary": {},
        "strategic": {"strategic": 1}, "egocentric": {"egocentric": 0.5},
        "deceptive": {"deceptive": True, "honesty": 0}, "flattering": {"flattering": 1},
        "aggressive": {"aggressive": 1}, "shameless": {"shameless": True},
        "smart": {"deceptive": True}, "clever": {"deceptive": True, "clever": True, "true_honesty": 0},
        "honest": {"honest": True, "x": 1}, "manipulative": {"deceptive": True, "strategic": -1, "manipulative": True, "flattering": 1, "true_honesty": 0},
        "dominant": {"deceptive": True, "strategic": 1, "egocentric": 0.5, "dominant": True, "true_honesty": 0},
        "destructive": {"deceptive": True, "strategic": 1, "aggressive": 1, "shameless": 1, "destructive": True},
        "good": {"strategic": 1, "honest": True, "x": 1}, "disturbing": {"disturbing": True},
        "antistrategic": {"strategic": -0.5}
    }

    result = {**default, **character_setup_dict.get(character, {})}
    return result
