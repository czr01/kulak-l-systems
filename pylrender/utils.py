import re

def is_numeric(n):
    try:
        float(n)
        return True
    except ValueError:
        return False

def is_pos_int(n):
    try:
        int(n)
        return int(n) > 0
    except ValueError:
        return False

def is_color(color, supported_colour_strings):
    if color in supported_colour_strings:
        return True
    
    if bool(re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", color)):
        return True
    
    if len(color.split(" ")) == 3:
        if all((is_numeric(value) and 0 <= int(value) <= 255) for value in color.split(" ")):
            return True
    
    return False