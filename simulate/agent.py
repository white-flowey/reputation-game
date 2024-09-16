import numpy as np
from statistics import median
from scipy.optimize import root

from config import init_conf
from .information_theory import Info, Ift


class Agent:
    def __init__(self, id, honesty, random_dict, character, log):
        self.conf = conf = init_conf()
        self.log = log
        self.random_dict = random_dict
        
        self.character = character
        self.setup_character(character)
        self.id = id
        self.honesty = honesty
        self.friendships = [Info(1, 0) if i == id else Info(0, 0) for i in conf("agents")]
        self.n_conversations = [{"partner": 0, "topic": 0}] * conf("n_agents")
        self.I = [[Info(conf("mindI")[a][b][0], conf("mindI")[a][b][1]) if conf("mindI") and a == id else Info(0,0) for b in conf("agents")] for a in conf("agents")]
        if conf("mindI"):
            print("YES")
        self.J = [[Info(0,0) for _ in conf("agents")] for _ in conf("agents")]
        self.C = [[Info(0,0) for _ in conf("agents")] for _ in conf("agents")]
        self.K = conf("Ks")[id] if conf("Ks") else [np.sqrt(np.pi) for _ in range(self.conf("KLENGTH"))]
        self.kappa = median(self.K) / np.sqrt(np.pi) if conf("Ks") else 1
        self.buffer = []
        
    def save_state(self, log=False):
        if log:
            return {"id": self.id, "honesty": round(self.honesty, 2), "friendships": [round(I.mean, 2) for I in self.friendships], "character": self.character, 
                "I": [[str(self.I[a][b].round(2)) for b in self.conf("agents")] for a in self.conf("agents")],
                "J": [[str(self.J[a][b].round(2)) for b in self.conf("agents")] for a in self.conf("agents")],
                "C": [[str(self.C[a][b].round(2)) for b in self.conf("agents")] for a in self.conf("agents")],
                "K": [round(k, 2) for k in self.K], "kappa": round(self.kappa, 2)
            }
        else:
            return {"id": self.id, "honesty": self.honesty, "friendships": [I.mean for I in self.friendships], "character": self.character, 
                "I": [[self.I[a][b].mean for b in self.conf("agents")] for a in self.conf("agents")],
                "J": [[self.J[a][b].mean for b in self.conf("agents")] for a in self.conf("agents")],
                "C": [[self.C[a][b].mean for b in self.conf("agents")] for a in self.conf("agents")],
                "K": self.K, "kappa": self.kappa
            }

    def set_mind(self, mind_model, other_attrs=None):
        self.mind = mind_model
        if other_attrs:
            for key, value in other_attrs.items():
                setattr(self, key, value)


    def setup_character(self, character):
        self.aggressive = 0
        self.strategic = 0
        self.deceptive = False
        self.listening = True
        self.shyness = 1
        self.shameless = 0
        self.disturbing = False
        self.flattering = False

        DeafMind, NaiveMind, UncriticalMind, OrdinaryMind = None, None, None, None
        character_setup_dict = {
            "deaf": lambda: self.set_mind(DeafMind, other_attrs={"listening": False}),
            "naive": lambda: self.set_mind(NaiveMind),
            "uncritical": lambda: self.set_mind(UncriticalMind),
            "ordinary": lambda: self.set_mind(OrdinaryMind),
            "strategic": lambda: self.set_mind(None, other_attrs={"strategic": 1}),
            "egocentric": lambda: self.set_mind(None, other_attrs={"egocentric": 0.5}),
            "deceptive": lambda: self.set_mind(None, other_attrs={"deceptive": True, "honesty": 0}),
            "flattering": lambda: self.set_mind(None, other_attrs={"flattering": 1}),
            "aggressive": lambda: self.set_mind(None, other_attrs={"aggressive": 1}),
            "shameless": lambda: self.set_mind(None, other_attrs={"shameless": True}),
            "smart": lambda: self.set_mind(OrdinaryMind, other_attrs={"deceptive": True}),
            "clever": lambda: self.set_mind(OrdinaryMind, other_attrs={"deceptive": True, "clever": True, "true_honesty": 0}),
            "honest": lambda: self.set_mind(None, other_attrs={"honest": True, "x": 1}),
            "manipulative": lambda: self.set_mind(OrdinaryMind, other_attrs={"deceptive": True, "strategic": -1, "manipulative": True, "flattering": 1, "true_honesty": 0}),
            "dominant": lambda: self.set_mind(OrdinaryMind, other_attrs={"deceptive": True, "strategic": 1, "egocentric": 0.5, "dominant": True, "true_honesty": 0}),
            "destructive": lambda: self.set_mind(OrdinaryMind, other_attrs={"deceptive": True, "strategic": 1, "aggressive": 1, "shameless": 1, "destructive": True}),
            "good": lambda: self.set_mind(OrdinaryMind, other_attrs={"strategic": 1, "honest": True, "x": 1}),
            "disturbing": lambda: self.set_mind(None, other_attrs={"disturbing": True}),
            "antistrategic": lambda: self.set_mind(None, other_attrs={"strategic": -0.5})
        }
        character_setup_dict[character]()

    
    def draw_max_from_list(self, list, type):
        max_value = max(list)
        max_indices = [index for index, value in enumerate(list) if value == max_value]
        if len(max_indices) > 1:
            return self.random_dict[type].choice(max_indices)
        return max_indices[0]


    def rank_communication_partners(self):
        # shyness
        if self.character == "ordinary":
            id = self.random_dict["recipients"].choice([id for id in self.conf("agents") if id != self.id])
            return [1 if i == id else 0 for i in self.conf("agents")]
        friendship_weights = np.array([self.friendships[i].mean for i in self.conf("agents")])
        relation_weights = np.multiply(friendship_weights ** self.conf("FRIENDSHIP_AFFECTS_B"), np.array([self.n_conversations[i]["partner"] for i in self.conf("agents")]) ** self.conf("RELATION_AFFECTS_B"))

        strategic_weights = np.array([(self.I[self.id][b].mean if self.strategic > 0 else 1 - self.I[self.id][b].mean) ** abs(self.strategic) for b in self.conf("agents")])
        weights = np.multiply(relation_weights, strategic_weights)
        weights[self.id] = 0
        weights = [weight / sum(weights) for weight in weights]

        return weights


    def draw_topic(self, agents):
        # direct vs. indirect contact, self-conversation update, friendship affinity
        if getattr(self, "egocentric", False) and self.egocentric > self.random_dict["egocentric"].uniform(): 
            return self
        if self.character == "ordinary": return agents[self.random_dict["topic"].choice(self.conf("agents"))] 
        
        relation_weights = np.array([self.n_conversations[i]["partner"] for i in self.conf("agents")]) ** self.conf("RELATION_AFFECTS_C")
        friendship_weights = np.array([self.friendships[i].mean for i in self.conf("agents")]) ** self.conf("FRIENDSHIP_AFFECTS_C")
        aggressive_weights = np.array([1 - i for i in friendship_weights]) ** (self.aggressive > self.random_dict["aggressive"].uniform())
        
        weights = np.prod([relation_weights, friendship_weights, aggressive_weights], axis=0)
        return agents[self.draw_max_from_list(weights, "topic")]
    

    def talk(self, topic, listeners, listener_weights=[1]):
        if not isinstance(listeners, list): listeners = [listeners]
        if len(listeners) > 1:
            assumed_opinion = Ift.make_average_opinion(listener_weights, [self.I[a][topic.id] for a in self.conf("agents")]) ** self.shyness
        else:
            assumed_opinion = self.I[listeners[0].id][topic.id]

        if self.random_dict["honests"].uniform() <= self.honesty:
            message = Message(self.id, topic.id, listeners, self.I[self.id][topic.id], True, False)
        elif False: # ADD OTHER CHARACTERS
            message = Message(self.id, topic.id, listeners, Info(0, 0), False, False)
        else:
            blush = self.conf("BLUSH_FREQ_LIE") > (self.random_dict["blush"].uniform() + self.shameless)
            KL_target = self.random_dict["lies"].exponential(self.kappa) * (2 * self.conf("F_CAUTION") if self.disturbing else self.conf("F_CAUTION"))

            def lie_size(x, is_positive):
                info = assumed_opinion + Info(x ** 2, 0) if is_positive else assumed_opinion + Info(0, x ** 2)
                return Ift.KL(info, assumed_opinion) - KL_target

            opt_lie_size = root(lie_size, [1.0], args=(self.friendships[topic.id].mean >= 0.5,)).x[0] ** 2
            aggressive = self.aggressive > self.random_dict["aggressive"].uniform()
            if self.id == topic.id:
                lie = Info(opt_lie_size, 0) if aggressive else Info(0, 0) 
            elif self.flattering and topic in listeners:
                lie = Info(opt_lie_size * ((1 - self.memory[topic.id].mean) if self.conf("SCALED_FLATTERING") else 1), 0)
            else:
                friendship = self.friendships[topic.id].mean
                if self.conf("CONTINUOUS_FRIENDSHIP"):
                    lie = Info(
                        (friendship > 0.5) * 2 * (friendship - 0.5) * opt_lie_size,
                        - (friendship < 0.5) * 2 * (friendship - 0.5) * opt_lie_size
                    ) if aggressive else Info(0, 0) # CHECK
                else:
                    if friendship == 0.5: lie = Info(0, 0)
                    else: lie = Info((friendship > 0.5) * opt_lie_size, (friendship < 0.5) * opt_lie_size)

            message = Message(self.id, topic.id, listeners, assumed_opinion + lie, False, blush)
        
        if self.conf("LOGGING"): self.log.conversation(self, listeners, listener_weights, message)
        self.awareness(message)
        return message


    def awareness(self, message):
        topic, statement, honest = message.topic, message.statement, message.honest

        self.J[self.id][topic] = statement
        self.I[self.id][self.id] += Info(honest, not honest)
        if topic == self.id and self.conf("ACTIVE_SELF_FRIENDSHIP"):
            friendship = statement.mean - median([self.J[i][self.id] for i in self.conf("agents") if i != self.id])
            self.friendships[self.id] = self.friendships[self.id] + Info(friendship > 0, friendship < 0)
        
        if self.conf("LOGGING"): self.log.self_update(self, topic)
            
    
    def update_from_buffer(self):
        if self.buffer:
            [self.listen(m) if self.listening else self.watch(m) for m in self.buffer]
            del self.buffer[0]


    def watch(self, message):
        speaker, topic, blush = message.speaker, message.topic, message.blush
        self.count_conversations(speaker, topic)

        speaker_rep = self.I[self.id][speaker]
        assumed_honesty = speaker_rep.mean
        trust = assumed_honesty / (assumed_honesty + ((1 - self.conf("FFL")) if not blush else np.inf) * (1 - assumed_honesty))
        Itruth, Ilie = Info(0, 0), Info(0, 0) if blush else speaker_rep + Info(1, 0), speaker_rep + Info(0, 1)
        self.update_memory(speaker, trust, Itruth, Ilie, speaker_rep)


    def listen(self, message):
        speaker, topic, statement, blush = message.speaker, message.topic, message.statement, message.blush
        topic_rep, speaker_rep = self.I[self.id][topic], self.I[self.id][speaker]
        self.count_conversations(speaker, topic)

        Itruth_naive = topic_rep + Ift.get_info_difference(statement, self.J[speaker][topic])
        if self.character == "naive":
            self.update_memory(speaker, 1, speaker_rep + Info(1, 0), Info(0, 0), speaker_rep)
            self.update_memory(topic, 1, Itruth_naive, Info(0, 0), topic_rep)
            return

        surprise = Ift.KL(statement, topic_rep)
        Rb = np.inf if blush else (1 - self.conf("BLUSH_FREQ_LIE"))
        trust = 0 if blush else speaker_rep.mean / (speaker_rep.mean + 0.5 * (surprise / (self.kappa)) ** 2 * Rb * (1 - speaker_rep.mean))        

        if speaker == topic:  # Confession
            if statement.mean < speaker_rep.mean and not blush:
                trust = 1
            self.update_memory(speaker, trust, statement + Info(1, 0), speaker_rep + Info(0, 1), speaker_rep)
        else:
            self.update_memory(speaker, trust, speaker_rep + Info(1, 0), speaker_rep + Info(0, 1), speaker_rep)
            self.update_memory(topic, trust, Itruth_naive, topic_rep, topic_rep)            

        self.K = self.K[1:] + [surprise] if len(self.K) == 10 else self.K + [surprise]
        self.kappa = median(self.K) / np.sqrt(np.pi)
        if self.id == topic:
            self.maintain_friendship(message)
        self.update_ToM(message, trust)

        if self.conf("LOGGING"): self.log.update(self, message, trust)


    def update_memory(self, topic, trust, Itruth, Ilie, Istart=None):
        update_info = Ift.match(trust, Itruth, Ilie, Istart)

        if (coef_sum := update_info.mu + update_info.la) > self.conf("MAX_COUNT"):
            update_info *= self.conf("MAX_COUNT") / coef_sum

        self.I[self.id][topic] = update_info


    def maintain_friendship(self, message):
        speaker, statement = message.speaker, message.statement.mean
        
        x_median = median([self.J[b][self.id].mean for b in self.conf("agents") if b not in (self.id, speaker)])
        update = Info(1, 0) if statement > x_median else Info(0, 1) if statement < x_median else self.friendships[message.speaker]
        if update:
            self.friendships[speaker] = self.friendships[speaker] + update if self.conf("CONTINUOUS_FRIENDSHIP") else update
            


    def update_ToM(self, message, trust):
        speaker, topic, statement = message.speaker, message.topic, message.statement
        
        self.I[speaker][topic] = trust * statement + (1 - trust) * self.I[speaker][topic]
        self.J[speaker][topic] = statement
        self.C[speaker][topic] = (1 - trust) * statement + trust * self.C[speaker][topic]


### HELPER ###
    def count_conversations(self, speaker, topic):
        self.n_conversations[speaker]["partner"] += 1
        self.n_conversations[topic]["topic"] += 1
    

class Message():
    def __init__(self, speaker, topic, listeners, statement, honest, blush):
        self.speaker = speaker
        self.topic = topic
        self.listeners = listeners
        self.statement = statement
        self.honest = honest
        self.blush = blush