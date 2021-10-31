
def clip(value, min, max):
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value

def max_or_value(values, alternative_value):
    values_list = list(values)  # list(['a']) = ['a']
    if len(values_list) == 0:
        return alternative_value
    else:
        return max(values_list)