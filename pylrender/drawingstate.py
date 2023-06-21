"""
    A class representing a DrawingState.
"""
class DrawingState:
    def __init__(self, x, y, angle, color):
        """
        Initializes a new DrawingState object.

        :param x: x-coordinate of the drawing state 
        :param y: y-coordinate of the drawing state
        :param angle: angle of the drawing state
        :param color: color of the drawing state
        """
        self.x = x
        self.y = y
        self.angle = angle
        self.color = color

    def __repr__(self):
        return f"DrawingState({self.x}, {self.y}, {self.angle}, {self.color})"