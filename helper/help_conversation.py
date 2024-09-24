def draw_max_from_list(random, list, type):
    max_value = max(list)
    max_indices = [index for index, value in enumerate(list) if value == max_value]
    if len(max_indices) > 1:
        return random[type].choice(max_indices)
    return max_indices[0]