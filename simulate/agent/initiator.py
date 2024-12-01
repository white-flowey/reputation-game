import numpy as np
from helper.help_conversation import draw_max_from_list


class Initiator:
    """
    Responsible for initiating conversations by selecting settings, listeners, and topics based on agent characteristics.
    """

    def __init__(self, agent) -> None:
        """Initializes the Initiator with a reference to the associated agent.

        Args:
            agent (Agent): The agent that this initiator belongs to.
        """
        self.a = agent

    def pick_setting(self) -> str:
        """Selects the conversation setting (one-to-one or one-to-all) based on a probability.

        Returns:
            str: The chosen setting, either "one_to_one" or "one_to_all".
        """
        return (
            "one_to_one"
            if self.a.random["n_recipients"].uniform() <= self.a.conf("p_one_to_one")
            else "one_to_all"
        )

    def pick_listeners(self, setting: str) -> dict:
        """Selects listeners based on the conversation setting and the agent's character.

        Args:
            setting (str): The setting for the conversation.

        Returns:
            dict: A dictionary containing the selected listener IDs and their weights.
        """
        others = [id for id in self.a.conf("agents") if id != self.a.id]
        if setting == "one_to_one":
            if self.a.character in ["ordinary", "werewolf", "villager_1", "villager_2"]:
                return {
                    "ids": [self.a.random["recipients"].choice(others)],
                    "weights": [1],
                }
            if self.a.character == "villager_1":
                listeners = {
                    "ids": others,
                    "weights": self.rank_listeners_villagers(others),
                }
                max_weight_id = draw_max_from_list(
                    self.a.random, listeners["weights"], "recipients"
                )
                return {k: [v[max_weight_id]] for k, v in listeners.items()}
            listeners = {"ids": others, "weights": self.rank_listeners(others)}
            max_weight_id = draw_max_from_list(
                self.a.random, listeners["weights"], "recipients"
            )
            return {k: [v[max_weight_id]] for k, v in listeners.items()}

        weights = self.rank_listeners(others)
        return {"ids": others, "weights": weights}

    def pick_topic(self) -> int:
        """Selects the conversation topic based on the agent's character and relationships.

        Returns:
            int: The ID of the chosen topic.
        """
        if self.a.character in ["ordinary", "werewolf", "villager_1", "villager_2"]:
            return self.a.random["topic"].choice(self.a.conf("agents"))

        if self.a.egocentric > self.a.random["egocentric"].uniform():
            return self.a.id
        others = [id for id in self.a.conf("agents") if id != self.a.id]
        if self.a.character == "villager_1":
            return self.pick_topic_villagers(others)

        agents = self.a.conf("agents")

        friend_weights = np.array(
            [self.a.friendships[i].mean for i in agents]
        ) ** self.a.conf("FRIENDSHIP_AFFECTS_C")
        rel_weights = (
            np.array([self.a.n_conversations[i]["topic"] for i in agents])
            + np.array([self.a.n_conversations[i]["partner"] for i in agents])
            * self.a.conf("Q")
        ) ** self.a.conf("RELATION_AFFECTS_C")

        rel_weights = rel_weights * friend_weights * self.a.shyness
        agg_weights = (1 - friend_weights) ** (
            self.a.aggressive > self.a.random["aggressive"].uniform()
        )
        weights = rel_weights * friend_weights * agg_weights
        return draw_max_from_list(self.a.random, weights, "topic")

    def rank_listeners(self, others: list[int]) -> np.ndarray:
        """Ranks potential listeners based on friendship and relationship weights.

        Args:
            others (list[int]): A list of IDs of potential listeners.

        Returns:
            np.ndarray: An array of weights representing the ranking of the listeners.
        """
        friend_weights = np.array(
            [self.a.friendships[i].mean for i in others]
        ) ** self.a.conf("FRIENDSHIP_AFFECTS_B")
        rel_weights = (
            np.array([self.a.n_conversations[i]["topic"] for i in others])
            + np.array([self.a.n_conversations[i]["partner"] for i in others])
            * self.a.conf("Q")
        ) ** self.a.conf("RELATION_AFFECTS_B")
        rel_weights = rel_weights * friend_weights * self.a.shyness

        strat_weights = np.array(
            [
                (self.a.I[b].mean if self.a.strategic > 0 else 1 - self.a.I[b].mean)
                ** abs(self.a.strategic)
                for b in others
            ]
        )
        weights = rel_weights * strat_weights
        weights_sum = weights.sum()
        return (
            weights / weights_sum if weights_sum > 0 else weights
        )  # Normalize the weights

    def rank_listeners_villagers(self, others: list[int]) -> np.ndarray:
        partners = np.array([self.a.n_conversations[i]["partner"] for i in others])
        if np.sum(partners) <= (2 * self.a.conf("n_rounds") / 3):
            min_index = np.argmin(partners)
            partners = np.zeros_like(partners, dtype=int)
            partners[min_index] = 1
            return partners
        else:
            # max_truthfulness = -1
            # id_truthfulness = self.a.id
            # for id, info in zip(self.a.conf("agents"), self.a.I):
            #     curr_truthfulness = info.mu / (info.mu + info.la)
            #     if curr_truthfulness > max_truthfulness and id != self.a.id:
            #         max_truthfulness = curr_truthfulness
            #         id_truthfulness = id
            most_trusted_agend = self.a.who_do_i_trust_most()
            return np.array([1 if o == most_trusted_agend else 0 for o in others])

    def pick_topic_villagers(self, others: list[int]) -> int:
        topics = np.array([self.a.n_conversations[i]["topic"] for i in others])
        min_index = np.argmin(topics)

        return others[min_index]

    def draw_topic(self, agents: list[int]) -> int:
        """Draws a topic based on the weights derived from relationships and friendships.

        Args:
            agents (list[int]): A list of agent IDs.

        Returns:
            int: The ID of the drawn topic.
        """
        rel_weights = np.array(
            [self.a.n_conversations[i]["partner"] for i in agents]
        ) ** self.a.conf("RELATION_AFFECTS_C")
        friend_weights = np.array(
            [self.a.friendships[i].mean for i in agents]
        ) ** self.a.conf("FRIENDSHIP_AFFECTS_C")
        agg_weights = (1 - friend_weights) ** (
            self.a.aggressive > self.a.random["aggressive"].uniform()
        )

        weights = rel_weights * friend_weights * agg_weights
        return agents[draw_max_from_list(self.a.random, weights, "topic")]
