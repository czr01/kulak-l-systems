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

def is_color(color):
    colors_str = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "brown", "black", "gray", "white"]
    hexadec_pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"

    # String
    if color in colors_str:
        return True
    
    # Hexadecimal
    if bool(re.match(hexadec_pattern, color)):
        return True
    
    # RGB
    if len(color.split(" ")) == 3:
        if all((is_numeric(value) and 0 <= int(value) <= 255) for value in color.split(" ")):
            return True
    
    return False