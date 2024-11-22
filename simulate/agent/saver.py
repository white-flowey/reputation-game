class StateSaver():
    """Handles compressing an agent's state into a small dict for logging or writing to JSON."""
    def __init__(self, agent):
        """Initializes the StateSaver with a reference to the associated agent.

        Args:
            agent: The agent that this StateSaver belongs to.
        """
        self.a = agent

    def initial_state(self) -> dict:
        """Gets the initial state of the agent.

        Returns:
            dict: A dictionary containing the initial state information of the agent.
        """
        return {
            "honesty": self.a.honesty, "character": self.a.character, 
            "friendships": [f.round_mean() for f in self.a.friendships],
            "I": [i.round_mean() for i in self.a.I],
            "Iothers": [[ii.round_mean() for ii in i] for i in self.a.Iothers],
            "J": [[jj.round_mean() for jj in j] for j in self.a.J],
            "lastK": self.a.K[-1], "kappa": float(self.a.kappa)
        }

    def save_state(self, topic: int, partners: list, setting: str) -> dict:
        """Saves only the necessary agent attributes that changed during this conversation.

        Args:
            topic (int): The topic of conversation.
            partners (list): The list of partners involved in the conversation.
            setting (str): The setting of the conversation ('one_to_one' or 'one_to_all').

        Returns:
            dict: A dictionary containing only the necessary agent attributes that changed during this conversation.
        """
        if setting == "one_to_one":
            partner = partners[0]
            state = {
                "topic": int(topic), "partner": int(partner), "id": self.a.id, "Iself": self.a.I[self.a.id].round_mean(),
                "Ipartner": self.a.I[partner].round_mean(), "Iothers": self.a.Iothers[partner][topic].round_mean(),
                "Jself": self.a.J[self.a.id][topic].round_mean(), "Jpartner": self.a.J[partner][topic].round_mean(),
                "lastK": float(self.a.K[-1]), "kappa": float(self.a.kappa)
            }
            if topic == self.a.id:
                state["friendships"] = float(self.a.friendships[partner].mean)
            if topic not in [self.a.id, partner]:
                state["Itopic"] = float(self.a.I[topic].mean)
        else:
            state = {}
        return state

    def log_state(self) -> dict:
        """Returns the current state of the agent, but nicely formatted.

        Returns:
            dict: A dictionary containing the logged state information of the agent.
        """
        return {
            "id": self.a.id, 
            "honesty": self.a.honesty, 
            "character": self.a.character, 
            "friendships": [str(I.round(2)) for I in self.a.friendships], 
            "I": [str(self.a.I[b].round(2)) for b in self.a.conf("agents")],
            "J": [[str(self.a.J[a][b].round(2)) for b in self.a.conf("agents")] for a in self.a.conf("agents")],
            "C": [[str(self.a.C[a][b].round(2)) for b in self.a.conf("agents")] for a in self.a.conf("agents")],
            "K": [k for k in self.a.K], 
            "kappa": self.a.kappa
        }
