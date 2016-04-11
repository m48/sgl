
def resolve_color(color):
    if color == None or color == (): return None

    if hasattr(color[0], "__getitem__"): color = color[0]

    color = list(color)
    for index, item in enumerate(color):
        if isinstance(item, float):
            color[index] = int(item * 255)
            item = color[index]

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

def is_color_alpha(color):
    return len(color) == 4 and color[3] != 255
