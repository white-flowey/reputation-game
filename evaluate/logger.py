import os

def log(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if result:  # Ensure there's a message to log
            with open(self.file_path, 'a') as file:
                file.write(f'{result}\n')
    return wrapper

class Logger():
    def __init__(self, id):
        self.directory = os.path.join(os.getcwd(), 'evaluate/results', 'logs')
        self.file_path = os.path.join(self.directory, f'{id}.txt')
        self.next_line = ""
        self.create_folder()
        self.clear_file()
        
    def create_folder(self):
        os.makedirs(self.directory, exist_ok=True)
    
    def clear_file(self):
        with open(self.file_path, 'w') as _:
            pass  # Simply opening the file in 'w' mode clears it

    @log
    def start(self, sim_id, agents):
        agents = "\n".join([f"A{agent.id}: Honesty = {round(agent.honesty, 2)}, Character = {agent.character}" for agent in agents])
        return f"===== Started simulation {sim_id}\n{agents}\n====="

    @log
    def time(self, round, time, agent):
        return f"\n=== ROUND {round + 1} - TIME {time} - A{agent} speaks ==="
    
    @log
    def partner_selection(self, friendship_weights, relation_weights, strategic_weights, weights):
        return f"Friendships: {friendship_weights}. Relations: {relation_weights}. Strategic: {strategic_weights}. Final: {weights}."

    @log
    def conversation(self, speaker, listeners, topic):
        listeners = "|".join([str(l.id) for l in listeners])
        return f"A{speaker.id} talks with A{listeners} about A{topic.id}."
    
    @log
    def topic(self, topic):
        return f"Picks A{topic.id} as topic.\n"
    
    @log
    def message(self, message):
        truth_status = "TELLS THE TRUTH" if message.honest else "LIES"
        blush_status = "BLUSHES" if message.blush else "DOESN'T BLUSH"
        return f"A{message.speaker} {truth_status}, {blush_status} and states {str(message.statement)} about A{message.topic}."
    
    @log
    def listen(self, message, listener, topic_rep, surprise, trust, kappa):
        return " ".join([f"Listener A{listener.id} trusts speaker A{message.speaker} to {round(trust, 2) * 100}%.",
                f"Surprise: {topic_rep} | {message.statement}.",
                f"Surprise size: {round(surprise, 2)}.",
                f"Sensitivity: {round(kappa, 2)}"])

    
    @log
    def match(self, agent, topic, trust, Itruth, Ilie, Istart, update_info):
        return f"A{agent} UPDATES ABOUT A{topic}: Trust: {round(trust, 2) * 100}%. True info: {Itruth}. Lie: {Ilie}. Start value: {Istart}. Match result: {update_info}"

    @log
    def update(self, speaker, topic, listeners, agents_pre):
        topic, id = topic.id, speaker.id
        speaker_pre = agents_pre[id][id]
        listeners_pre = [agents_pre[l.id][l.id] for l in listeners]
        # remove all the id calls?
        speaker_update = "".join([f"Speaker A{id} updates: \n",
                                    f"\tSelf: A{id}: {speaker_pre[id]} -> {speaker.I[id][id]}\n",
                                    f"\tPartner: A{id}: {speaker_pre[listeners[0].id]} -> {speaker.I[id][listeners[0].id]}\n" if len(listeners) == 1 else "",
                                    f"\tTopic: A{topic}: {speaker_pre[topic]} -> {speaker.I[id][topic]}\n" if len(listeners) == 1 else ""])
        listener_update = "\n"
        for listener, id, listener_pre in zip(listeners, [l.id for l in listeners], listeners_pre):
            listener_update += "".join([f"Listener A{id} updates: \n",
                                    f"\tSelf: A{id}: {listener_pre[id]} -> {listener.I[id][id]}\n" if len(listeners) == 1 else "",
                                    f"\tPartner: A{id}: {listener_pre[speaker.id]} -> {listener.I[id][speaker.id]}\n",
                                    f"\tTopic: A{topic}: {listener_pre[topic]} -> {listener.I[id][topic]}\n"])
    
        return "\n" + speaker_update + listener_update

