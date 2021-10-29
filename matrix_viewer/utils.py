
def clip(value, min, max):
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value