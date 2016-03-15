
def resolve_color(color):
    if color == None or color == (): return None

    if hasattr(color[0], "__getitem__"): color = color[0]

    color = list(color)
    for index, item in enumerate(color):
        if isinstance(item, float):
            color[index] = item * 255

        if item < 0: 
            color[index] = 0
        elif item > 255: 
            color[index] = 255

    if len(color) == 1:
        return (color[0], color[0], color[0])
    elif len(color) == 2:
        return (color[0], color[0], color[0], color[1])
    elif len(color) == 3:
        return (color[0], color[1], color[2])
    elif len(color) == 4:
        return (color[0], color[1], color[2], color[3])
