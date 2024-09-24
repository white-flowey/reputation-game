import numpy as np

from helper.help_conversation import draw_max_from_list

class Initiator():
    def __init__(self, agent):
        self.a = agent
    
    def pick_setting(self):
        if self.a.random["n_recipients"].uniform() <= self.a.conf("p_one_to_one"):
            return "one_to_one"
        else:
            return "one_to_all"
        
    def pick_listeners(self, setting):
        others = [id for id in self.a.conf("agents") if id != self.a.id]
        if setting == "one_to_one": 
            if self.a.character == "ordinary":
                return {"ids": [self.a.random["recipients"].choice(others)],
                        "weights": [1]}
            max_weight_id = draw_max_from_list(self.random, listeners["weights"], "recipients")
            listeners = {k: [v[max_weight_id]] for k, v in listeners.items()}
        weights = self.rank_listeners(others)
        return {"ids": others, "weights": weights}
    
    def pick_topic(self):
        if self.a.character == "ordinary":
            return self.a.random["topic"].choice(self.a.conf("agents"))
        if self.a.egocentric > self.a.random["egocentric"].uniform():
            return self.a.id

        agents = self.a.conf("agents")
        rel_weights = (np.array([self.a.n_conversations[i]["partner"] for i in agents]) 
                       ** self.a.conf("RELATION_AFFECTS_C") ** self.a.shyness)
        friend_weights = np.array([self.a.friendships[i].mean for i in agents]) ** self.a.conf("FRIENDSHIP_AFFECTS_C")
        agg_weights = (1 - friend_weights) ** self.a.aggressive > self.a.random["aggressive"].uniform()
        weights = rel_weights * friend_weights * agg_weights  
        return draw_max_from_list(self.a.random, weights, "topic")

    def rank_listeners(self, others):
        friend_weights = np.array([self.a.friendships[i].mean for i in others]) ** self.a.conf("FRIENDSHIP_AFFECTS_B")
        rel_weights = (friend_weights * np.array([self.a.n_conversations[i]["partner"] for i in others]) ** 
                            self.a.conf("RELATION_AFFECTS_B") ** self.a.shyness)
        
        strat_weights = np.array([(self.a.I[b].mean if self.a.strategic > 0 else 1 - self.a.I[b].mean) 
                                      ** abs(self.a.strategic) for b in others])
        weights = rel_weights * strat_weights
        weights /= weights.sum()
        return weights

    def draw_topic(self, agents):
        agents = self.a.conf("agents")
        rel_weights = np.array([self.a.n_conversations[i]["partner"] for i in agents]) ** self.a.conf("RELATION_AFFECTS_C")
        friend_weights = np.array([self.a.friendships[i].mean for i in agents]) ** self.a.conf("FRIENDSHIP_AFFECTS_C")
        agg_weights = (1 - friend_weights) ** (self.a.aggressive > self.a.random["aggressive"].uniform())

        weights = rel_weights * friend_weights * agg_weights
        return agents[self.a.draw_max_from_list(weights, "topic")]
